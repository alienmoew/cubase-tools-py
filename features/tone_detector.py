import re
import time
import threading

import pyautogui

import config
from features.base_feature import BaseFeature
from utils.helpers import OCRHelper, ImageHelper, MessageHelper, MouseHelper
from utils.process_finder import CubaseProcessFinder
from utils.window_manager import WindowManager


class ToneDetector(BaseFeature):
    """Tính năng dò tone và auto-click."""

    def __init__(self):
        super().__init__()
        OCRHelper.setup_tesseract()
        self._detection_lock = threading.Lock()  # Thread safety
        self._manual_active = False  # Flag cho bất kỳ manual operation nào
        self.auto_detect_active = False  # Flag cho auto-detect state
        self.auto_detect_thread = None  # Thread cho auto-detect
        self.tone_callback = None  # Callback để update UI
        self.current_tone_getter = None  # Getter để lấy current tone
    
    def pause_auto_detect(self):
        """Tạm dừng auto-detect cho các chức năng khác."""
        self._manual_active = True
    
    def resume_auto_detect(self):
        """Cho phép auto-detect tiếp tục sau khi chức năng khác hoàn thành."""
        self._manual_active = False

    def get_name(self):
        return "Dò Tone"
    
    def _calculate_crop_box(self, win_w, win_h):
        """Tính toán crop box với margin ratio từ config."""
        margin_ratio = config.CROP_MARGIN_RATIO
        return (
            win_w // margin_ratio,              # x1
            win_h // margin_ratio,              # y1  
            win_w * (margin_ratio - 1) // margin_ratio,  # x2
            win_h * (margin_ratio - 1) // margin_ratio   # y2
        )
    
    def _screenshot_and_crop_plugin(self, plugin_win):
        """Screenshot plugin window và crop theo margin."""
        left, top, right, bottom = plugin_win.left, plugin_win.top, plugin_win.right, plugin_win.bottom
        full = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
        
        win_w, win_h = right - left, bottom - top
        crop_box = self._calculate_crop_box(win_w, win_h)
        cropped = full.crop(crop_box)
        
        return cropped, (left, top, crop_box)

    def execute(self, tone_callback=None):
        """Thực thi tính năng dò tone."""
        # Set flag cho manual operation và đợi auto release lock
        self._manual_active = True
        
        # Đợi để lấy lock (blocking=True để đợi)
        self._detection_lock.acquire()
            
        self.tone_callback = tone_callback
        # 1. Tìm Cubase process
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Không tìm thấy tiến trình Cubase!")
            MessageHelper.show_error(
                "Lỗi Cubase", 
                "Không tìm thấy tiến trình Cubase!\n\nVui lòng:\n• Mở Cubase trước khi sử dụng\n• Đảm bảo Cubase đang chạy"
            )
            self._manual_active = False
            self._detection_lock.release()
            return False

        # 2. Focus Cubase
        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        if not hwnd:
            print("❌ Không focus được Cubase!")
            MessageHelper.show_error(
                "Lỗi Focus", 
                "Không thể focus vào cửa sổ Cubase!\n\nThử lại sau vài giây."
            )
            self._manual_active = False
            self._detection_lock.release()
            return False
        time.sleep(config.FOCUS_DELAY)

        # 3. Tìm plugin window
        plugin_win = WindowManager.find_window("AUTO-KEY")
        if not plugin_win:
            print("❌ Không tìm thấy plugin AUTO-KEY!")
            MessageHelper.show_error(
                "Lỗi Plugin AUTO-KEY", 
                "Không tìm thấy plugin AUTO-KEY!\n\nVui lòng:\n• Mở plugin AUTO-KEY trong Cubase\n• Đảm bảo cửa sổ plugin hiển thị trên màn hình\n• Kiểm tra tên cửa sổ có chứa 'AUTO-KEY'"
            )
            self._manual_active = False
            self._detection_lock.release()
            return False

        plugin_win.activate()
        time.sleep(config.FOCUS_DELAY)

        # 4. Screenshot và OCR
        success = self._process_plugin_window(plugin_win)
        
        # Reset flag và release lock
        self._manual_active = False
        self._detection_lock.release()
        return success

    def _process_plugin_window(self, plugin_win):
        """Xử lý cửa sổ plugin."""
        # Screenshot và crop
        cropped, (left, top, crop_box) = self._screenshot_and_crop_plugin(plugin_win)

        # OCR
        data_crop = OCRHelper.extract_text_data(cropped)
        words_crop = OCRHelper.get_text_words(data_crop)
        print("📜 OCR text:", words_crop)

        # Trích xuất và hiển thị tone hiện tại
        current_tone = self._extract_current_tone(words_crop)
        if current_tone and self.tone_callback:
            self.tone_callback(current_tone)

        # Debug image
        debug_path = ImageHelper.save_debug_image_with_boxes(
            cropped.copy(), data_crop, "plugin_ocr_debug.png"
        )
        print(f"🖼 OCR debug image saved -> {debug_path}")

        # Tìm và click tone
        tone_found = self._find_and_click_tone(data_crop, left, top, crop_box)
        if not tone_found:
            return False

        # Đợi và click Send button
        time.sleep(config.ANALYSIS_DELAY)
        send_clicked = self._find_and_click_send_button(
            data_crop, left, top, crop_box)

        return send_clicked

    def _find_and_click_tone(self, ocr_data, left, top, crop_box):
        """Tìm và click tone (Major/Minor) - đợi khi đang Listening."""
        # Đợi cho đến khi plugin không còn listening
        if self._is_listening(ocr_data):
            print("🎧 Plugin đang Listening... Đợi cho đến khi hoàn tất...")
            if not self._wait_for_listening_complete():
                print("⏰ Timeout waiting for listening to complete")
                return False
        
        for i, txt in enumerate(ocr_data["text"]):
            if txt and txt.strip() in ("Major", "Minor"):
                note = ocr_data["text"][i-1].strip() if i > 0 else ""
                found = f"{note} {txt.strip()}".strip()

                click_x = left + \
                    crop_box[0] + ocr_data["left"][i] + \
                    ocr_data["width"][i] // 2
                click_y = top + \
                    crop_box[1] + ocr_data["top"][i] + \
                    ocr_data["height"][i] // 2

                MouseHelper.safe_click(click_x, click_y)
                print(f"🎹 Click key: {found}")
                return True

        print("⚠️ Không tìm thấy 'Major' hoặc 'Minor'")
        return False
    
    def _is_listening(self, ocr_data):
        """Kiểm tra xem plugin có đang ở trạng thái Listening không."""
        try:
            # Kiểm tra các từ trong OCR data
            for txt in ocr_data["text"]:
                if txt and txt.strip():
                    txt_clean = txt.strip().lower()
                    # Kiểm tra các biến thể của "Listening"
                    if any(keyword in txt_clean for keyword in [
                        "listening", "listen", "analyzing", "processing", 
                        "detecting", "analysis", "wait", "processing..."
                    ]):
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking listening state: {e}")
            return False
    
    def _wait_for_listening_complete(self, max_wait_time=30, check_interval=1.0):
        """Đợi cho đến khi plugin không còn ở trạng thái Listening."""
        print("⏳ Đang đợi plugin hoàn tất phân tích...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Tìm plugin window
                plugin_win = WindowManager.find_window("AUTO-KEY")
                if not plugin_win:
                    print("❌ Mất kết nối với plugin AUTO-KEY")
                    return False
                
                # Screenshot và OCR để kiểm tra trạng thái
                left, top, right, bottom = plugin_win.left, plugin_win.top, plugin_win.right, plugin_win.bottom
                full = pyautogui.screenshot(
                    region=(left, top, right - left, bottom - top))
                
                # Crop
                win_w, win_h = right - left, bottom - top
                crop_box = self._calculate_crop_box(win_w, win_h)
                cropped = full.crop(crop_box)
                
                # OCR
                data_crop = OCRHelper.extract_text_data(cropped)
                
                # Kiểm tra xem còn listening không
                if not self._is_listening(data_crop):
                    elapsed_time = time.time() - start_time
                    print(f"✅ Plugin đã hoàn tất phân tích sau {elapsed_time:.1f}s")
                    return True
                
                # Hiển thị progress
                elapsed_time = time.time() - start_time
                print(f"🎧 Vẫn đang phân tích... ({elapsed_time:.1f}s)")
                
                # Đợi trước khi kiểm tra lại
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Error waiting for listening: {e}")
                return False
        
        print(f"⏰ Timeout sau {max_wait_time}s - plugin vẫn đang phân tích")
        return False

    def _find_and_click_send_button(self, ocr_data, left, top, crop_box):
        """Tìm và click nút Send."""
        for i, txt in enumerate(ocr_data["text"]):
            txt_clean = txt.strip() if txt else ""
            if txt_clean.lower() in ("send", "send to auto-tune™", "auto-tune"):
                click_x = left + \
                    crop_box[0] + ocr_data["left"][i] + \
                    ocr_data["width"][i] // 2
                click_y = top + \
                    crop_box[1] + ocr_data["top"][i] + \
                    ocr_data["height"][i] // 2

                MouseHelper.safe_click(click_x, click_y)
                print(f"✅ Clicked '{txt_clean}' button")
                return True

        print("⚠️ Không tìm thấy nút 'Send to Auto-Tune'")
        return False
    
    def _extract_current_tone(self, words_list):
        """Trích xuất tone hiện tại từ danh sách từ OCR - chỉ lấy Note + Mode."""
        try:
            # Tìm vị trí của AUTO-KEY và Send
            auto_key_index = -1
            send_index = -1
            
            for i, word in enumerate(words_list):
                if "AUTO-KEY" in word.upper():
                    auto_key_index = i
                elif word.upper() in ("SEND", "Send"):
                    send_index = i
                    break
            
            # Nếu tìm thấy cả hai markers
            if auto_key_index >= 0 and send_index >= 0 and send_index > auto_key_index:
                # Lấy các từ giữa AUTO-KEY và Send
                tone_words = words_list[auto_key_index + 1:send_index]
                
                # Lọc các từ hợp lệ
                if tone_words:
                    # Danh sách các note hợp lệ (bao gồm cả viết hoa và thường)
                    valid_notes = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", 
                                  "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B",
                                  "c", "c#", "db", "d", "d#", "eb", "e", "f",
                                  "f#", "gb", "g", "g#", "ab", "a", "a#", "bb", "b"]
                    
                    # Danh sách các mode hợp lệ  
                    valid_modes = ["Major", "Minor", "major", "minor"]
                    
                    note = None
                    mode = None
                    

                    
                    # Tìm note và mode
                    for word in tone_words:
                        word_clean = word.strip()
                        
                        # Làm sạch ký tự đặc biệt aggressive hơn
                        word_cleaned = re.sub(r"[^A-Za-z#b]", "", word_clean)  # Chỉ giữ chữ cái, # và b
                        
                        # Kiểm tra note (giữ nguyên format gốc)
                        if word_cleaned in valid_notes and note is None:
                            note = word_cleaned  # Giữ nguyên như OCR đọc được
                        
                        # Kiểm tra mode (giữ nguyên format gốc)
                        elif word_cleaned in valid_modes and mode is None:
                            mode = word_cleaned  # Giữ nguyên như OCR đọc được
                    
                    # Trả về kết hợp note + mode
                    if note and mode:
                        return f"{note} {mode}"
                    elif note:  # Chỉ có note
                        return note
                    elif mode:  # Chỉ có mode (hiếm khi xảy ra)
                        return mode
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting tone: {e}")
            return None
    
    def start_auto_detect(self, tone_callback=None, current_tone_getter=None):
        """Bắt đầu auto detect tone."""
        if self.auto_detect_active:
            return
        
        self.tone_callback = tone_callback
        self.current_tone_getter = current_tone_getter
        self.auto_detect_active = True
        
        # Tạo thread để chạy auto detect
        self.auto_detect_thread = threading.Thread(target=self._auto_detect_loop, daemon=True)
        self.auto_detect_thread.start()
        
        print("✅ Auto detect bắt đầu hoạt động")
    
    def stop_auto_detect(self):
        """Dừng auto detect tone."""
        if not self.auto_detect_active:
            return
        
        self.auto_detect_active = False
        if self.auto_detect_thread:
            self.auto_detect_thread.join(timeout=config.THREAD_JOIN_TIMEOUT)
        
        print("⏹️ Auto detect đã dừng")
    
    def _auto_detect_loop(self):
        """Loop chính của auto detect."""
        check_interval = config.AUTO_DETECT_INTERVAL
        
        while self.auto_detect_active:
            try:
                # Kiểm tra manual operation trước
                if self._manual_active:
                    time.sleep(config.AUTO_DETECT_RESPONSIVE_DELAY)
                    continue
                
                # Kiểm tra xem có thể lấy lock không
                if not self._detection_lock.acquire(blocking=False):
                    time.sleep(check_interval)
                    continue
                
                try:
                    # Kiểm tra tone mới
                    new_tone = self._check_current_tone()
                
                    if new_tone:
                        # Lấy tone hiện tại từ app
                        current_app_tone = "--"
                        if self.current_tone_getter:
                            current_app_tone = self.current_tone_getter()
                        
                        # So sánh tone
                        if new_tone != current_app_tone:
                            print(f"🔄 Phát hiện tone mới: {current_app_tone} → {new_tone}")
                            
                            # Cập nhật UI
                            if self.tone_callback:
                                self.tone_callback(new_tone)
                            
                            # Tự động gửi tone mới
                            self._auto_send_tone()
                    
                    # Đợi trước khi kiểm tra lần tiếp theo
                    time.sleep(check_interval)
                
                finally:
                    # Luôn release lock sau khi xong
                    self._detection_lock.release()
                
            except Exception as e:
                print(f"❌ Auto detect error: {e}")
                time.sleep(check_interval)
    
    def _check_current_tone(self):
        """Kiểm tra tone hiện tại từ plugin (chỉ OCR, không click)."""
        try:
            # Tìm plugin window
            plugin_win = WindowManager.find_window("AUTO-KEY")
            if not plugin_win:
                return None
            
            # Screenshot và OCR
            left, top, right, bottom = plugin_win.left, plugin_win.top, plugin_win.right, plugin_win.bottom
            full = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top))
            
            # Crop
            win_w, win_h = right - left, bottom - top
            crop_box = self._calculate_crop_box(win_w, win_h)
            cropped = full.crop(crop_box)
            
            # OCR
            data_crop = OCRHelper.extract_text_data(cropped)
            words_crop = OCRHelper.get_text_words(data_crop)
            
            # Trích xuất tone
            return self._extract_current_tone(words_crop)
            
        except Exception as e:
            print(f"❌ Error checking current tone: {e}")
            return None
    
    def _auto_send_tone(self):
        """Tự động gửi tone (chỉ click Send button) - đợi khi đang Listening."""
        try:
            # Tìm plugin window
            plugin_win = WindowManager.find_window("AUTO-KEY")
            if not plugin_win:
                return False
            
            # Screenshot và OCR
            left, top, right, bottom = plugin_win.left, plugin_win.top, plugin_win.right, plugin_win.bottom
            full = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top))
            
            # Crop
            win_w, win_h = right - left, bottom - top
            crop_box = self._calculate_crop_box(win_w, win_h)
            cropped = full.crop(crop_box)
            
            # OCR
            data_crop = OCRHelper.extract_text_data(cropped)
            
            # Đợi nếu đang Listening (timeout ngắn hơn cho auto mode)
            if self._is_listening(data_crop):
                print("🎧 Auto mode: Plugin đang Listening... Đợi...")
                if not self._wait_for_listening_complete(
                    max_wait_time=config.AUTO_DETECT_TIMEOUT_SHORT, 
                    check_interval=config.AUTO_DETECT_RESPONSIVE_DELAY
                ):
                    print("⏰ Auto mode timeout - bỏ qua lần này")
                    return False
            
            # Tìm và click Send button
            success = self._find_and_click_send_button(data_crop, left, top, crop_box)
            
            if success:
                print("✅ Auto sent tone successfully")
            
            return success
            
        except Exception as e:
            print(f"❌ Error in auto send: {e}")
            return False

"""
Tone Mic Detector - Điều chỉnh bass (LOW) và treble (HIGH) của mic
"""
import time
import pyautogui
import cv2
import numpy as np

import config
from features.base_feature import BaseFeature
from utils.helpers import ImageHelper, TemplateHelper, MessageHelper, MouseHelper, OCRHelper
from utils.process_finder import CubaseProcessFinder
from utils.window_manager import WindowManager


class ToneMicDetector(BaseFeature):
    """Tính năng điều chỉnh tone mic (bass/treble) trực tiếp trong Cubase."""
    
    def __init__(self):
        super().__init__()
        
        # Template path
        self.template_path = config.TEMPLATE_PATHS['tone_mic_template']
        
        # Khởi tạo OCR
        OCRHelper.setup_tesseract()
        
    def get_name(self):
        """Trả về tên hiển thị của detector."""
        return "Tone Mic"
    
    def _find_cubase_process(self):
        """Tìm tiến trình Cubase."""
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Không tìm thấy tiến trình Cubase!")
            MessageHelper.show_error(
                "Lỗi Cubase", 
                "Không tìm thấy tiến trình Cubase đang chạy!\n\nVui lòng mở Cubase trước khi sử dụng chức năng này."
            )
        return proc

    def _focus_cubase_window(self, proc):
        """Focus cửa sổ Cubase."""
        try:
            hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        except Exception as e:
            print(f"❌ Lỗi khi focus Cubase window: {e}")
            MessageHelper.show_error(
                "Lỗi Focus Window", 
                "Không thể focus cửa sổ Cubase!"
            )
            return None
        
        time.sleep(0.3)
        return hwnd
        
    def _find_xvox_window(self):
        """Tìm cửa sổ XVox plugin."""
        # Try different possible window titles for XVox
        possible_titles = ["Xvox", "XVOX", "xvox", "X-Vox", "X_Vox"]
        
        for title in possible_titles:
            plugin_win = WindowManager.find_window(title)
            if plugin_win:
                print(f"✅ Found XVox window: {title}")
                plugin_win.activate()
                time.sleep(0.3)
                return plugin_win
        
        print("❌ XVox plugin window not found")
        MessageHelper.show_error(
            "Lỗi XVox Plugin", 
            "Không tìm thấy XVox plugin window!\n\nVui lòng:\n• Mở XVox plugin trong Cubase\n• Đảm bảo cửa sổ plugin hiển thị trên màn hình"
        )
        return None
    
    def _find_tone_mic_template(self, xvox_window):
        """Tìm tone mic template và OCR vùng đó để tìm LOW/HIGH trong XVox plugin."""
        try:
            # Lấy thông tin cửa sổ XVox
            x, y, w, h = xvox_window.left, xvox_window.top, xvox_window.width, xvox_window.height
            print(f"📐 XVox window: {x}, {y}, {w}x{h}")
            
            # Screenshot XVox window
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            print(f"📐 XVox screenshot size: {w}x{h}")
            
            # Load template
            template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"❌ Cannot load tone mic template: {self.template_path}")
                return None
                
            template_h, template_w = template.shape[:2]
            print(f"📐 Tone Mic template size: {template_w}x{template_h}")
            
            # Adaptive template matching
            best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
            
            print(f"🏆 Tone Mic best method: {best_result['method']}")
            print(f"🔍 Tone Mic confidence: {best_result['confidence']:.3f}")
            print(f"📏 Tone Mic scale: {best_result['scale']:.2f}")
            
            if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ Tone Mic template confidence too low: {best_result['confidence']:.3f}")
                return None
            
            # Template match coordinates
            match_x, match_y = best_result['location']
            scaled_w, scaled_h = best_result['template_size']
            
            print(f"✅ Tone Mic template found at: ({match_x}, {match_y}) with size {scaled_w}x{scaled_h}")
            
            # Define OCR region (toàn bộ template area)
            ocr_x, ocr_y = match_x, match_y
            ocr_w, ocr_h = scaled_w, scaled_h
            
            print(f"📖 OCR region: ({ocr_x}, {ocr_y}, {ocr_w}x{ocr_h})")
            print(f"🔍 OCR region size: {ocr_w}x{ocr_h}")
            
            # Direct capture OCR region để tránh double crop color shift
            absolute_ocr_x = x + ocr_x
            absolute_ocr_y = y + ocr_y
            ocr_region_pil = pyautogui.screenshot(region=(absolute_ocr_x, absolute_ocr_y, ocr_w, ocr_h))
            
            # Convert OCR region to grayscale như Auto-Tune detector
            print("📖 Converting OCR region to grayscale...")
            ocr_region_np = np.array(ocr_region_pil)
            ocr_region_gray = cv2.cvtColor(ocr_region_np, cv2.COLOR_RGB2GRAY)
            
            # Convert back to PIL for OCR
            from PIL import Image
            ocr_region_gray_pil = Image.fromarray(ocr_region_gray, mode='L')
            
            print("📖 OCR on grayscale region...")
            ocr_data = OCRHelper.extract_text_data(ocr_region_gray_pil)
            words = OCRHelper.get_text_words(ocr_data)
            print(f"📜 OCR text in tone mic region: {words}")
            
            # Tìm vị trí LOW và HIGH
            low_pos = None
            high_pos = None
            
            for i, text in enumerate(ocr_data["text"]):
                if text and text.strip():
                    text_clean = text.strip().upper()
                    
                    if "LOW" in text_clean:
                        # Tính vị trí absolute của LOW
                        low_x = x + ocr_x + ocr_data["left"][i] + ocr_data["width"][i] // 2
                        low_y = y + ocr_y + ocr_data["top"][i] + ocr_data["height"][i] // 2
                        low_pos = (low_x, low_y)
                        print(f"🔉 Found LOW at: ({low_x}, {low_y})")
                    
                    elif "HIGH" in text_clean:
                        # Tính vị trí absolute của HIGH
                        high_x = x + ocr_x + ocr_data["left"][i] + ocr_data["width"][i] // 2
                        high_y = y + ocr_y + ocr_data["top"][i] + ocr_data["height"][i] // 2
                        high_pos = (high_x, high_y)
                        print(f"🔊 Found HIGH at: ({high_x}, {high_y})")
            
            # Fallback logic: Nếu không detect được LOW/HIGH, dùng position-based approach
            if not low_pos or not high_pos:
                print("⚠️ OCR không detect đủ LOW/HIGH, sử dụng position-based fallback...")
                
                # Lọc ra các text có content
                valid_texts = []
                for i, text in enumerate(ocr_data["text"]):
                    if text and text.strip():
                        text_info = {
                            'text': text.strip(),
                            'index': i,
                            'left': ocr_data["left"][i],
                            'top': ocr_data["top"][i],
                            'width': ocr_data["width"][i],
                            'height': ocr_data["height"][i]
                        }
                        valid_texts.append(text_info)
                
                print(f"📝 Valid OCR texts: {[t['text'] for t in valid_texts]}")
                
                # Nếu có ít nhất 3 elements (để có index 0 và 2)
                if len(valid_texts) >= 3:
                    # Element đầu tiên (index 0) = LOW
                    if not low_pos:
                        low_info = valid_texts[0]
                        low_x = x + ocr_x + low_info['left'] + low_info['width'] // 2
                        low_y = y + ocr_y + low_info['top'] + low_info['height'] // 2
                        low_pos = (low_x, low_y)
                        print(f"🔉 Fallback LOW ('{low_info['text']}') at: ({low_x}, {low_y})")
                    
                    # Element thứ 3 (index 2) = HIGH  
                    if not high_pos:
                        high_info = valid_texts[2]
                        high_x = x + ocr_x + high_info['left'] + high_info['width'] // 2
                        high_y = y + ocr_y + high_info['top'] + high_info['height'] // 2
                        high_pos = (high_x, high_y)
                        print(f"🔊 Fallback HIGH ('{high_info['text']}') at: ({high_x}, {high_y})")
                
                else:
                    print(f"❌ Không đủ OCR elements để fallback (cần ít nhất 3, có {len(valid_texts)})")
            
            # Save debug image
            debug_filename = "tone_mic_ocr_debug.png"
            
            # Tạo debug image với template match và OCR results
            debug_image = screenshot_np.copy()
            
            # Vẽ template match box
            cv2.rectangle(debug_image, 
                        (match_x, match_y), 
                        (match_x + scaled_w, match_y + scaled_h), 
                        (0, 255, 0), 2)
            cv2.putText(debug_image, f"Template Match {best_result['confidence']:.3f}", 
                       (match_x, match_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Vẽ OCR region box
            cv2.rectangle(debug_image, 
                        (ocr_x, ocr_y), 
                        (ocr_x + ocr_w, ocr_y + ocr_h), 
                        (255, 0, 0), 2)
            cv2.putText(debug_image, "OCR Region", 
                       (ocr_x, ocr_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            # Vẽ LOW và HIGH positions
            if low_pos:
                rel_low_x = low_pos[0] - x
                rel_low_y = low_pos[1] - y
                cv2.circle(debug_image, (rel_low_x, rel_low_y), 5, (0, 0, 255), -1)
                cv2.putText(debug_image, "LOW", (rel_low_x + 10, rel_low_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if high_pos:
                rel_high_x = high_pos[0] - x
                rel_high_y = high_pos[1] - y
                cv2.circle(debug_image, (rel_high_x, rel_high_y), 5, (255, 0, 255), -1)
                cv2.putText(debug_image, "HIGH", (rel_high_x + 10, rel_high_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            
            # Save debug image
            debug_path = f"result/{debug_filename}"
            cv2.imwrite(debug_path, debug_image)
            print(f"🖼 Tone Mic OCR debug saved -> {debug_path}")
            
            return {
                'low_pos': low_pos,
                'high_pos': high_pos,
                'template_match': best_result,
                'ocr_words': words
            }
            
        except Exception as e:
            print(f"❌ Error in tone mic template detection: {e}")
            return None
    
    def detect_tone_mic_controls(self):
        """Phát hiện các control của tone mic và tạo debug image."""
        print("🎤 Tone Mic Detector - Detecting controls in XVox...")
        
        # 1. Find và focus Cubase process
        proc = self._find_cubase_process()
        if not proc:
            return False
        
        # 2. Focus Cubase window
        if not self._focus_cubase_window(proc):
            return False
        
        # 3. Find XVox plugin window
        xvox_window = self._find_xvox_window()
        if not xvox_window:
            return False
        
        # 4. Find tone mic template và OCR trong XVox
        result = self._find_tone_mic_template(xvox_window)
        if not result:
            print("❌ Failed to detect tone mic controls")
            return False
        
        # 4. Report results
        low_pos = result['low_pos']
        high_pos = result['high_pos']
        
        if low_pos and high_pos:
            print(f"✅ Successfully detected both controls:")
            print(f"   🔉 LOW (Bass): {low_pos}")
            print(f"   🔊 HIGH (Treble): {high_pos}")
            return True
        elif low_pos:
            print(f"⚠️ Only detected LOW (Bass): {low_pos}")
            return True
        elif high_pos:
            print(f"⚠️ Only detected HIGH (Treble): {high_pos}")
            return True
        else:
            print("❌ Could not detect LOW or HIGH controls")
            return False
    
    def set_bass_value(self, value):
        """
        Set bass (LOW) value với workflow: OCR -> click text -> click 40% -> triple-click + Ctrl+A -> type value
        Range: -30 to 30
        """
        # Validate range
        if value < -30:
            value = -30
            print(f"⚠️ Bass value clamped to minimum: {value}")
        elif value > 30:
            value = 30
            print(f"⚠️ Bass value clamped to maximum: {value}")
            
        print(f"🔉 Setting Bass (LOW) value to: {value}")
        
        # Store original cursor position
        original_pos = pyautogui.position()
        
        try:
            # 1. Find và focus Cubase process
            proc = self._find_cubase_process()
            if not proc:
                return False
            
            # 2. Focus Cubase window
            if not self._focus_cubase_window(proc):
                return False
            
            # 3. Find XVox plugin window
            xvox_window = self._find_xvox_window()
            if not xvox_window:
                return False
            
            # 4. Find tone mic template và OCR để tìm LOW text
            result = self._find_tone_mic_template(xvox_window)
            if not result or not result.get('low_pos'):
                print("❌ Could not find LOW text position")
                return False
            
            low_pos = result['low_pos']
            print(f"✅ Found LOW text at: {low_pos}")
            
            # 5. Click vào LOW text
            pyautogui.click(low_pos[0], low_pos[1])
            time.sleep(0.2)
            print(f"🖱 Clicked on LOW text at {low_pos}")
            
            # 6. Click ở vị trí chiều dọc 40% từ trên xuống (giữ nguyên x coordinate)
            # Tính toán vị trí 40% theo chiều dọc từ top của template
            template_match = result['template_match']
            template_top = template_match['location'][1]
            template_height = template_match['template_size'][1]  # template_size is (w, h)
            
            click_y = template_top + (template_height * 0.40)
            click_x = low_pos[0]  # Giữ nguyên x coordinate của LOW text
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.2)
            print(f"🖱 Clicked at 40% position: ({click_x}, {click_y})")
            
            # 7. Multiple selection methods để ensure text được select
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.1)
            print("🖱 Triple-clicked to select text")
            
            # Thử thêm Ctrl+A để chắc chắn
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            print("⌨️ Also tried Ctrl+A")
            
            # 8. Type giá trị mới (sẽ replace selected text)
            pyautogui.typewrite(str(value))
            time.sleep(0.1)
            print(f"⌨️ Typed value: {value}")
            
            # 9. Nhấn Enter để confirm
            pyautogui.press('enter')
            time.sleep(0.2)
            print("⌨️ Pressed Enter to confirm")
            
            print(f"✅ Successfully set Bass (LOW) to {value}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting bass value: {e}")
            return False
        finally:
            # Restore cursor position at the end of entire workflow
            pyautogui.moveTo(original_pos[0], original_pos[1])
    
    def set_treble_value(self, value):
        """
        Set treble (HIGH) value với workflow: OCR -> click text -> click 40% -> triple-click + Ctrl+A -> type value
        Range: -20 to 30
        """
        # Validate range
        if value < -20:
            value = -20
            print(f"⚠️ Treble value clamped to minimum: {value}")
        elif value > 30:
            value = 30
            print(f"⚠️ Treble value clamped to maximum: {value}")
            
        print(f"🔊 Setting Treble (HIGH) value to: {value}")
        
        # Store original cursor position
        original_pos = pyautogui.position()
        
        try:
            # 1. Find và focus Cubase process
            proc = self._find_cubase_process()
            if not proc:
                return False
            
            # 2. Focus Cubase window
            if not self._focus_cubase_window(proc):
                return False
            
            # 3. Find XVox plugin window
            xvox_window = self._find_xvox_window()
            if not xvox_window:
                return False
            
            # 4. Find tone mic template và OCR để tìm HIGH text
            result = self._find_tone_mic_template(xvox_window)
            if not result or not result.get('high_pos'):
                print("❌ Could not find HIGH text position")
                return False
            
            high_pos = result['high_pos']
            print(f"✅ Found HIGH text at: {high_pos}")
            
            # 5. Click vào HIGH text
            pyautogui.click(high_pos[0], high_pos[1])
            time.sleep(0.2)
            print(f"🖱 Clicked on HIGH text at {high_pos}")
            
            # 6. Click ở vị trí chiều dọc 40% từ trên xuống (giữ nguyên x coordinate)
            # Tính toán vị trí 40% theo chiều dọc từ top của template
            template_match = result['template_match']
            template_top = template_match['location'][1]
            template_height = template_match['template_size'][1]  # template_size is (w, h)
            
            click_y = template_top + (template_height * 0.40)
            click_x = high_pos[0]  # Giữ nguyên x coordinate của HIGH text
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.2)
            print(f"🖱 Clicked at 40% position: ({click_x}, {click_y})")
            
            # 7. Multiple selection methods để ensure text được select
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.1)
            print("🖱 Triple-clicked to select text")
            
            # Thử thêm Ctrl+A để chắc chắn
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            print("⌨️ Also tried Ctrl+A")
            
            # 8. Type giá trị mới (sẽ replace selected text)
            pyautogui.typewrite(str(value))
            time.sleep(0.1)
            print(f"⌨️ Typed value: {value}")
            
            # 9. Nhấn Enter để confirm
            pyautogui.press('enter')
            time.sleep(0.2)
            print("⌨️ Pressed Enter to confirm")
            
            print(f"✅ Successfully set Treble (HIGH) to {value}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting treble value: {e}")
            return False
        finally:
            # Restore cursor position at the end of entire workflow
            pyautogui.moveTo(original_pos[0], original_pos[1])
    
    def execute(self):
        """Execute tone mic detection."""
        return self.detect_tone_mic_controls()
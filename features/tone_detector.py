import time
import pyautogui
from features.base_feature import BaseFeature
from utils.process_finder import CubaseProcessFinder
from utils.window_manager import WindowManager
from utils.helpers import OCRHelper, ImageHelper
import config


class ToneDetector(BaseFeature):
    """Tính năng dò tone và auto-click."""

    def __init__(self):
        super().__init__()
        OCRHelper.setup_tesseract()

    def get_name(self):
        return "Dò Tone"

    def execute(self):
        """Thực thi tính năng dò tone."""
        # 1. Tìm Cubase process
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Không tìm thấy tiến trình Cubase!")
            return False

        # 2. Focus Cubase
        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        if not hwnd:
            print("❌ Không focus được Cubase!")
            return False
        time.sleep(config.FOCUS_DELAY)

        # 3. Tìm plugin window
        plugin_win = WindowManager.find_window("AUTO-KEY")
        if not plugin_win:
            print("❌ Không tìm thấy plugin AUTO-KEY!")
            return False

        plugin_win.activate()
        time.sleep(config.FOCUS_DELAY)

        # 4. Screenshot và OCR
        success = self._process_plugin_window(plugin_win)
        return success

    def _process_plugin_window(self, plugin_win):
        """Xử lý cửa sổ plugin."""
        # Screenshot
        left, top, right, bottom = plugin_win.left, plugin_win.top, plugin_win.right, plugin_win.bottom
        full = pyautogui.screenshot(
            region=(left, top, right - left, bottom - top))

        # Crop
        win_w, win_h = right - left, bottom - top
        crop_box = (
            win_w // 6,          # x1 (bỏ 1/6 bên trái)
            win_h // 6,          # y1 (bỏ 1/6 trên)
            win_w * 5 // 6,      # x2 (bỏ 1/6 bên phải)
            win_h * 5 // 6       # y2 (bỏ 1/6 dưới)
        )
        cropped = full.crop(crop_box)

        # OCR
        data_crop = OCRHelper.extract_text_data(cropped)
        words_crop = OCRHelper.get_text_words(data_crop)
        print("📜 OCR text:", words_crop)

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
        """Tìm và click tone (Major/Minor)."""
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

                pyautogui.click(click_x, click_y, _pause=False)
                print(f"🎹 Click key: {found}")
                return True

        print("⚠️ Không tìm thấy 'Major' hoặc 'Minor'")
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

                pyautogui.click(click_x, click_y, _pause=False)
                print(f"✅ Clicked '{txt_clean}' button")
                return True

        print("⚠️ Không tìm thấy nút 'Send to Auto-Tune'")
        return False

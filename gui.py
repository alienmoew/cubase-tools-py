import tkinter as tk
import time
import os
import pyautogui
import pytesseract
from pytesseract import Output
from PIL import Image, ImageDraw
import win32gui
import win32con

from process_finder import CubaseProcessFinder
from window_manager import WindowManager

# đường dẫn tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

RESULT_DIR = "result"

class CubaseAutoToolGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cubase Auto Tools")
        self.root.geometry("300x200")

        btn_tone = tk.Button(
            self.root,
            text="Dò Tone",
            font=("Arial", 12),
            command=self.do_tone_and_click,
        )
        btn_tone.pack(pady=20)

    def save_debug_image_with_boxes(self, pil_img, ocr_data, path):
        draw = ImageDraw.Draw(pil_img)
        for i, txt in enumerate(ocr_data["text"]):
            if txt and txt.strip():
                x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
        pil_img.save(path)

    def do_tone_and_click(self):
        os.makedirs(RESULT_DIR, exist_ok=True)

        # 1) find Cubase process
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Không tìm thấy tiến trình Cubase!")
            return

        # 2) focus Cubase
        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        if not hwnd:
            print("❌ Không focus được Cubase!")
            return
        time.sleep(0.5)

        # 3) find plugin window
        plugin_win = WindowManager.find_window("AUTO-KEY")
        if not plugin_win:
            print("❌ Không tìm thấy plugin AUTO-KEY!")
            return

        plugin_win.activate()
        time.sleep(0.5)

        # 4) screenshot full plugin
        left, top, right, bottom = plugin_win.left, plugin_win.top, plugin_win.right, plugin_win.bottom
        full = pyautogui.screenshot(
            region=(left, top, right - left, bottom - top))

        # 5) crop lớn để lấy hết chữ
        win_w, win_h = right - left, bottom - top
        crop_box = (0, win_h // 8, win_w, win_h * 7 // 8)
        cropped = full.crop(crop_box)

        # 6) OCR trên cropped image
        config = r"--oem 3 --psm 6"
        data_crop = pytesseract.image_to_data(
            cropped, output_type=Output.DICT, config=config)
        words_crop = [w.strip() for w in data_crop["text"] if w.strip()]
        print("📜 OCR text:", words_crop)

        # 7) debug image
        debug_path = os.path.join(RESULT_DIR, "plugin_ocr_debug.png")
        self.save_debug_image_with_boxes(cropped.copy(), data_crop, debug_path)
        print(f"🖼 OCR debug image saved -> {debug_path}")

        # 8) Tìm chữ Major/Minor và click
        found = None
        for i, txt in enumerate(data_crop["text"]):
            if txt and txt.strip() in ("Major", "Minor"):
                note = data_crop["text"][i-1].strip() if i > 0 else ""
                found = f"{note} {txt.strip()}".strip()
                click_x = left + \
                    crop_box[0] + data_crop["left"][i] + \
                    data_crop["width"][i] // 2
                click_y = top + \
                    crop_box[1] + data_crop["top"][i] + \
                    data_crop["height"][i] // 2
                pyautogui.click(click_x, click_y, _pause=False)
                break

        if not found:
            print("⚠️ Không tìm thấy 'Major' hoặc 'Minor'")
            return
        print(f"🎹 Click key: {found}")

        # 9) đợi 6 giây rồi click 'Send to Auto-Tune'
        time.sleep(6)
        send_btn_found = None
        for i, txt in enumerate(data_crop["text"]):
            txt_clean = txt.strip() if txt else ""
            if txt_clean.lower() in ("send", "send to auto-tune™", "auto-tune"):
                send_btn_found = txt_clean
                click_x2 = left + \
                    crop_box[0] + data_crop["left"][i] + \
                    data_crop["width"][i] // 2
                click_y2 = top + \
                    crop_box[1] + data_crop["top"][i] + \
                    data_crop["height"][i] // 2
                pyautogui.click(click_x2, click_y2, _pause=False)
                break

        if send_btn_found:
            print(f"✅ Clicked '{send_btn_found}' button")
        else:
            print("⚠️ Không tìm thấy nút 'Send to Auto-Tune'")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CubaseAutoToolGUI().run()

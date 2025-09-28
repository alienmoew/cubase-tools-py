import os
import pytesseract
from pytesseract import Output
from PIL import ImageDraw
import tkinter as tk
from tkinter import messagebox
import config

class OCRHelper:
    """Helper class cho các thao tác OCR."""
    
    @staticmethod
    def setup_tesseract():
        """Cấu hình Tesseract."""
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
        os.environ["TESSDATA_PREFIX"] = config.TESSDATA_DIR
    
    @staticmethod
    def extract_text_data(image):
        """Trích xuất text từ image."""
        return pytesseract.image_to_data(
            image, output_type=Output.DICT, config=config.OCR_CONFIG
        )
    
    @staticmethod
    def get_text_words(ocr_data):
        """Lấy danh sách từ từ OCR data."""
        return [w.strip() for w in ocr_data["text"] if w.strip()]

class ImageHelper:
    """Helper class cho các thao tác với hình ảnh."""
    
    @staticmethod
    def save_debug_image_with_boxes(pil_img, ocr_data, filename):
        """Lưu ảnh debug với các box OCR."""
        draw = ImageDraw.Draw(pil_img)
        
        for i, txt in enumerate(ocr_data["text"]):
            if txt and txt.strip():
                x, y, w, h = (
                    ocr_data["left"][i], 
                    ocr_data["top"][i], 
                    ocr_data["width"][i], 
                    ocr_data["height"][i]
                )
                draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
        
        path = os.path.join(config.RESULT_DIR, filename)
        pil_img.save(path)
        return path

class MessageHelper:
    """Helper class cho các thông báo popup."""
    
    @staticmethod
    def show_error(title, message):
        """Hiển thị popup lỗi."""
        # Tạo root window ẩn
        root = tk.Tk()
        root.withdraw()  # Ẩn cửa sổ chính
        root.attributes('-topmost', True)  # Đưa lên trên cùng
        
        # Hiển thị messagebox
        messagebox.showerror(title, message)
        
        # Đóng root window
        root.destroy()
    
    @staticmethod
    def show_warning(title, message):
        """Hiển thị popup cảnh báo."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        messagebox.showwarning(title, message)
        root.destroy()
    
    @staticmethod
    def show_info(title, message):
        """Hiển thị popup thông tin."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        messagebox.showinfo(title, message)
        root.destroy()
    
    @staticmethod
    def show_success(title, message):
        """Hiển thị popup thành công."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        messagebox.showinfo(title, message)
        root.destroy()

class MouseHelper:
    """Helper class cho các thao tác chuột an toàn."""
    
    @staticmethod
    def safe_click(x, y, return_mode="instant", delay=0.15):
        """
        Click an toàn với việc khôi phục vị trí chuột ban đầu.
        
        Args:
            x, y: Tọa độ click
            return_mode: Chế độ trả về vị trí cũ
                - "instant": Nhảy ngay lập tức (mặc định - teleport như khi click)
                - "fast": Di chuyển nhanh (0.05s)
                - "smooth": Di chuyển mượt (0.15s)
            delay: Thời gian chờ sau khi click (giây)
        """
        import pyautogui
        import time
        import win32api
        
        # Lưu vị trí chuột hiện tại
        original_x, original_y = pyautogui.position()
        
        # Thực hiện click
        pyautogui.click(x, y, _pause=False)
        
        # Trả chuột về vị trí ban đầu
        time.sleep(delay)
        
        if return_mode == "instant":
            # Sử dụng Win32 API để teleport ngay lập tức - không có animation
            win32api.SetCursorPos((original_x, original_y))
        elif return_mode == "fast":
            # Di chuyển nhanh
            pyautogui.moveTo(original_x, original_y, duration=0.05)
        elif return_mode == "smooth":
            # Di chuyển mượt
            pyautogui.moveTo(original_x, original_y, duration=0.15)
    
    @staticmethod
    def safe_double_click(x, y, return_mode="instant", delay=0.15):
        """Double click an toàn với việc khôi phục vị trí chuột."""
        import pyautogui
        import time
        import win32api
        
        original_x, original_y = pyautogui.position()
        pyautogui.doubleClick(x, y, _pause=False)
        
        time.sleep(delay)
        
        if return_mode == "instant":
            # Sử dụng Win32 API để teleport ngay lập tức
            win32api.SetCursorPos((original_x, original_y))
        elif return_mode == "fast":
            pyautogui.moveTo(original_x, original_y, duration=0.05)
        elif return_mode == "smooth":
            pyautogui.moveTo(original_x, original_y, duration=0.15)
    
    @staticmethod
    def safe_right_click(x, y, return_mode="instant", delay=0.15):
        """Right click an toàn với việc khôi phục vị trí chuột."""
        import pyautogui
        import time
        import win32api
        
        original_x, original_y = pyautogui.position()
        pyautogui.rightClick(x, y, _pause=False)
        
        time.sleep(delay)
        
        if return_mode == "instant":
            # Sử dụng Win32 API để teleport ngay lập tức
            win32api.SetCursorPos((original_x, original_y))
        elif return_mode == "fast":
            pyautogui.moveTo(original_x, original_y, duration=0.05)
        elif return_mode == "smooth":
            pyautogui.moveTo(original_x, original_y, duration=0.15)
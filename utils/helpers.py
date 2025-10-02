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
    
    @staticmethod
    def extract_text_data_from_image(image_array):
        """Extract OCR data từ numpy image array."""
        import pytesseract
        from PIL import Image
        
        # Convert numpy array to PIL Image
        if len(image_array.shape) == 3:
            pil_image = Image.fromarray(image_array)
        else:
            pil_image = Image.fromarray(image_array, mode='L')
        
        # OCR với detailed data
        ocr_data = pytesseract.image_to_data(
            pil_image, 
            output_type=pytesseract.Output.DICT,
            config='--psm 6'  # Assume uniform block of text
        )
        
        return ocr_data

class ImageHelper:
    """Helper class cho các thao tác với hình ảnh."""
    
    @staticmethod
    def save_debug_image_with_boxes(pil_img, ocr_data, filename):
        """Lưu ảnh debug với các box OCR."""
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(pil_img)
        
        # Font cho text labels
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        for i, txt in enumerate(ocr_data["text"]):
            if txt and txt.strip():
                x, y, w, h = (
                    ocr_data["left"][i], 
                    ocr_data["top"][i], 
                    ocr_data["width"][i], 
                    ocr_data["height"][i]
                )
                
                # Different colors for different text types
                text_lower = txt.strip().lower()
                if any(keyword in text_lower for keyword in ["major", "minor"]):
                    color = "lime"  # Green cho tone buttons
                elif "send" in text_lower:
                    color = "cyan"  # Cyan cho send button
                elif "auto-key" in text_lower:
                    color = "yellow"  # Yellow cho plugin name
                else:
                    color = "red"    # Red cho text khác
                
                # Draw rectangle
                draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
                
                # Add text label
                label_pos = (x, max(0, y - 15))
                draw.text(label_pos, txt.strip(), fill=color, font=font)
        
        path = os.path.join(config.RESULT_DIR, filename)
        pil_img.save(path)
        return path
    
    @staticmethod
    def save_template_debug_image(screenshot_np, template, match_loc, confidence, filename):
        """Lưu ảnh debug template matching với highlight box."""
        import cv2
        from PIL import Image, ImageDraw, ImageFont
        
        # pyautogui screenshot đã là RGB, chỉ cần convert thành PIL
        if len(screenshot_np.shape) == 3 and screenshot_np.shape[2] == 3:
            # Screenshot from pyautogui is already RGB
            pil_img = Image.fromarray(screenshot_np)
        else:
            # Fallback nếu format khác
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(screenshot_rgb)
        
        draw = ImageDraw.Draw(pil_img)
        
        # Draw template match box với thickness dựa trên confidence
        template_h, template_w = template.shape[:2]
        top_left = match_loc
        bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
        
        # Color và thickness dựa trên confidence
        if confidence >= 0.9:
            color = "lime"  # Bright green cho match tốt
            thickness = 4
        elif confidence >= 0.7:
            color = "orange"  # Orange cho match trung bình
            thickness = 3
        else:
            color = "red"     # Red cho match kém
            thickness = 2
        
        # Draw rectangle với thickness
        for i in range(thickness):
            draw.rectangle([
                (top_left[0] - i, top_left[1] - i), 
                (bottom_right[0] + i, bottom_right[1] + i)
            ], outline=color, width=1)
        
        # Add confidence text với background
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        text = f"Confidence: {confidence:.3f}"
        text_pos = (top_left[0], max(0, top_left[1] - 30))
        
        # Text background
        text_bbox = draw.textbbox(text_pos, text, font=font)
        draw.rectangle(text_bbox, fill="black", outline=color)
        draw.text(text_pos, text, fill="white", font=font)
        
        # Add cross-hair at click position để show exact click point
        center_x = top_left[0] + template_w // 2
        center_y = top_left[1] + template_h // 2
        cross_size = 10
        
        # Draw cross-hair
        draw.line([
            (center_x - cross_size, center_y), 
            (center_x + cross_size, center_y)
        ], fill="yellow", width=2)
        draw.line([
            (center_x, center_y - cross_size), 
            (center_x, center_y + cross_size)
        ], fill="yellow", width=2)
        
        # Save debug image
        path = os.path.join(config.RESULT_DIR, filename)
        pil_img.save(path)
        return path
    
    @staticmethod
    def get_result_path(filename):
        """Lấy đường dẫn file trong thư mục result."""
        os.makedirs(config.RESULT_DIR, exist_ok=True)
        return os.path.join(config.RESULT_DIR, filename)

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
        """Hiển thị popup thành công (alias cho show_info)."""
        MessageHelper.show_info(title, message)

class ConfigHelper:
    """Helper class để đọc file cấu hình giá trị mặc định."""
    
    @staticmethod
    def load_default_values(config_file="default_values.txt"):
        """Đọc giá trị mặc định từ file cấu hình."""
        defaults = {}
        try:
            # Đường dẫn tới file config
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_file)
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Bỏ qua dòng comment và dòng trống
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse key=value
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Chuyển đổi sang số nếu có thể
                            try:
                                if '.' in value:
                                    defaults[key] = float(value)
                                else:
                                    defaults[key] = int(value)
                            except ValueError:
                                defaults[key] = value
                                
            return defaults
        except Exception as e:
            print(f"❌ Lỗi đọc file cấu hình: {e}")
            # Trả về giá trị mặc định backup
            return {
                'transpose_default': 0, 'transpose_min': -12, 'transpose_max': 12,
                'return_speed_default': 200, 'return_speed_min': 0, 'return_speed_max': 400,
                'flex_tune_default': 0, 'flex_tune_min': 0, 'flex_tune_max': 100,
                'natural_vibrato_default': 0, 'natural_vibrato_min': -12, 'natural_vibrato_max': 12,
                'humanize_default': 0, 'humanize_min': 0, 'humanize_max': 100
            }

class TemplateHelper:
    """Helper class cho multi-scale template matching."""
    
    @staticmethod
    def multi_scale_template_match(screenshot_gray, template, scale_range=(0.6, 1.4), scale_step=0.1):
        """Thực hiện multi-scale template matching để handle plugin resize."""
        import cv2
        import numpy as np
        import config
        
        best_confidence = 0
        best_location = None
        best_scale = 1.0
        best_template_size = None
        
        # Generate scale factors
        scales = np.arange(scale_range[0], scale_range[1] + scale_step, scale_step)
        
        for scale in scales:
            # Resize template
            template_h, template_w = template.shape[:2]
            new_w = int(template_w * scale)
            new_h = int(template_h * scale)
            
            if new_w < 10 or new_h < 10 or new_w > screenshot_gray.shape[1] or new_h > screenshot_gray.shape[0]:
                continue
            
            scaled_template = cv2.resize(template, (new_w, new_h))
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Boost confidence for scaled templates (they might be slightly less accurate)
            if scale != 1.0:
                max_val += config.SCALE_CONFIDENCE_BOOST
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_location = max_loc
                best_scale = scale
                best_template_size = (new_w, new_h)
        
        return best_confidence, best_location, best_scale, best_template_size
    
    @staticmethod
    def adaptive_template_match(screenshot_gray, template):
        """Adaptive template matching với fallback strategies."""
        import cv2
        import config
        
        results = []
        
        # Method 1: Standard template matching
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        results.append({
            'method': 'Standard',
            'confidence': max_val,
            'location': max_loc,
            'scale': 1.0,
            'template_size': template.shape[:2][::-1]  # (w, h)
        })
        
        # Method 2: Multi-scale matching (if enabled)
        if config.MULTI_SCALE_ENABLED:
            confidence, location, scale, template_size = TemplateHelper.multi_scale_template_match(
                screenshot_gray, template, config.SCALE_RANGE, config.SCALE_STEP
            )
            results.append({
                'method': 'Multi-Scale',
                'confidence': confidence,
                'location': location,
                'scale': scale,
                'template_size': template_size
            })
        
        # Method 3: Edge-based matching (for very different scales)
        try:
            # Convert to edges
            screenshot_edges = cv2.Canny(screenshot_gray, 50, 150)
            template_edges = cv2.Canny(template, 50, 150)
            
            result = cv2.matchTemplate(screenshot_edges, template_edges, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            results.append({
                'method': 'Edge-Based',
                'confidence': max_val * 0.9,  # Slightly lower weight for edge matching
                'location': max_loc,
                'scale': 1.0,
                'template_size': template.shape[:2][::-1]
            })
        except Exception as e:
            print(f"Edge-based matching failed: {e}")
        
        # Select best result
        best_result = max(results, key=lambda x: x['confidence'])
        
        return best_result

class MouseHelper:
    """Helper class cho các thao tác chuột an toàn."""
    
    @staticmethod
    def _restore_cursor_position(original_pos, return_mode, delay):
        """
        Shared logic để restore cursor position.
        
        Args:
            original_pos: (x, y) tuple of original position
            return_mode: "instant", "fast", or "smooth"
            delay: Delay before restoring position
        """
        import pyautogui
        import time
        import win32api
        
        time.sleep(delay)
        original_x, original_y = original_pos
        
        if return_mode == "instant":
            # Sử dụng Win32 API để teleport ngay lập tức
            win32api.SetCursorPos((original_x, original_y))
        elif return_mode == "fast":
            pyautogui.moveTo(original_x, original_y, duration=0.05)
        elif return_mode == "smooth":
            pyautogui.moveTo(original_x, original_y, duration=0.15)
    
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
        
        # Lưu vị trí chuột hiện tại
        original_pos = pyautogui.position()
        
        # Thực hiện click
        pyautogui.click(x, y, _pause=False)
        
        # Restore cursor position
        MouseHelper._restore_cursor_position(original_pos, return_mode, delay)
    
    @staticmethod
    def safe_double_click(x, y, return_mode="instant", delay=0.15):
        """Double click an toàn với việc khôi phục vị trí chuột."""
        import pyautogui
        
        original_pos = pyautogui.position()
        pyautogui.doubleClick(x, y, _pause=False)
        
        # Restore cursor position
        MouseHelper._restore_cursor_position(original_pos, return_mode, delay)
    
    @staticmethod
    def safe_right_click(x, y, return_mode="instant", delay=0.15):
        """Right click an toàn với việc khôi phục vị trí chuột."""
        import pyautogui
        
        original_pos = pyautogui.position()
        pyautogui.rightClick(x, y, _pause=False)
        
        # Restore cursor position
        MouseHelper._restore_cursor_position(original_pos, return_mode, delay)
    
    @staticmethod
    def batch_click_start():
        """Bắt đầu batch click - lưu vị trí cursor ban đầu."""
        import pyautogui
        return pyautogui.position()
    
    @staticmethod
    def batch_click(x, y, delay=0.05):
        """Click không restore cursor - dùng cho batch operations."""
        import pyautogui
        import time
        pyautogui.click(x, y, _pause=False)
        time.sleep(delay)
    
    @staticmethod  
    def batch_click_end(original_pos, return_mode="instant", delay=0.15):
        """Kết thúc batch click - restore cursor về vị trí ban đầu."""
        MouseHelper._restore_cursor_position(original_pos, return_mode, delay)
import os
import pytesseract
from pytesseract import Output
from PIL import ImageDraw
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
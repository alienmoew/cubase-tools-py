from features.auto_tune_detector import AutoTuneDetector


class TransposeDetector(AutoTuneDetector):
    """Tính năng Transpose adjustment với AUTO-TUNE PRO plugin."""

    def __init__(self):
        super().__init__(
            feature_name="Transpose",
            template_filename="transpose_template.png",
            config_prefix="transpose"
        )
    
    def set_pitch_value(self, pitch_value):
        """Set giá trị pitch - wrapper cho compatibility."""
        return self.set_auto_tune_value(pitch_value)
    
    def reset_to_zero(self):
        """Backward compatibility method - reset về 0."""
        return self.set_auto_tune_value(0)
    
    def _find_template_match(self, plugin_win):
        """Override để sử dụng 60% từ top thay vì 90% cho transpose."""
        import cv2
        import numpy as np
        import pyautogui
        import config
        
        # Chụp ảnh màn hình vùng plugin
        x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        # Load template
        template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"❌ Không thể load template: {self.template_path}")
            return None, 0

        # Template matching
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"🔍 {self.feature_name} Template matching confidence: {max_val:.2f}")

        if max_val < config.TEMPLATE_MATCH_THRESHOLD:
            print(f"❌ Template not found for {self.feature_name.lower()}. Confidence: {max_val:.2f}")
            return None, max_val

        # Tính toán vị trí click (60% từ top của template cho transpose)
        template_height = template.shape[0]
        click_x = x + max_loc[0] + template.shape[1] // 2
        click_y = y + max_loc[1] + int(template_height * 0.6)  # 60% thay vì 90%

        print(f"✅ Template found for {self.feature_name.lower()} with confidence: {max_val:.2f}")
        print(f"🎯 {self.feature_name} click position: ({click_x}, {click_y})")

        return (click_x, click_y), max_val
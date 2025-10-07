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
        """Override để sử dụng 60% từ top thay vì 90% cho transpose với adaptive matching."""
        import cv2
        import numpy as np
        import pyautogui
        import config
        from utils.helpers import ImageHelper, TemplateHelper
        
        # Chụp ảnh màn hình vùng plugin
        x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        print(f"📐 Transpose plugin window size: {w}x{h}")

        # Load template
        template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"❌ Không thể load template: {self.template_path}")
            return None, 0

        template_h, template_w = template.shape[:2]
        print(f"📐 Transpose template size: {template_w}x{template_h}")

        # Adaptive template matching
        best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
        
        print(f"🏆 Transpose best method: {best_result['method']}")
        print(f"🔍 Transpose confidence: {best_result['confidence']:.3f}")
        print(f"📏 Transpose scale: {best_result['scale']:.2f}")

        # Save debug image với adaptive result
        debug_filename = f"{self.config_prefix}_adaptive_debug.png"
        
        # Create scaled template for debug visualization
        if best_result['scale'] != 1.0:
            scaled_w, scaled_h = best_result['template_size']
            debug_template = cv2.resize(template, (scaled_w, scaled_h))
        else:
            debug_template = template
        
        debug_path = ImageHelper.save_template_debug_image(
            screenshot_np, debug_template, best_result['location'], 
            best_result['confidence'], debug_filename
        )
        print(f"🖼 Transpose adaptive debug saved -> {debug_path}")

        if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
            print(f"❌ Transpose template not found. Confidence: {best_result['confidence']:.3f}")
            print(f"💡 Try resizing AUTO-TUNE plugin or update transpose template")
            return None, best_result['confidence']

        # Tính toán vị trí click (60% từ top của scaled template cho transpose)
        scaled_w, scaled_h = best_result['template_size']
        click_x = x + best_result['location'][0] + scaled_w // 2
        click_y = y + best_result['location'][1] + int(scaled_h * 0.6)  # 60% thay vì 90%

        print(f"✅ Transpose template found with confidence: {best_result['confidence']:.3f}")
        print(f"🎯 Transpose click position: ({click_x}, {click_y}) - 60% from top [Scale: {best_result['scale']:.2f}]")

        return (click_x, click_y), best_result['confidence']
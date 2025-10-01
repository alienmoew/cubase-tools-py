"""
Reverb Detector - Điều chỉnh độ vang mic qua plugin reverb
"""
import time
import pyautogui
from features.auto_tune_detector import AutoTuneDetector
from utils.helpers import ConfigHelper

class ReverbDetector(AutoTuneDetector):
    """Tính năng điều chỉnh độ vang mic với reverb plugin."""
    
    def __init__(self):
        # Initialize với đúng arguments cho AutoTuneDetector
        super().__init__(
            feature_name="Reverb",
            template_filename="reverb_template.png", 
            config_prefix="reverb"
        )
        self.current_value = 36  # Giá trị mặc định
        
        # Load default values
        self.default_values = ConfigHelper.load_default_values()
        self.min_value = self.default_values.get('reverb_min', 30)
        self.max_value = self.default_values.get('reverb_max', 42)
        self.default_value = self.default_values.get('reverb_default', 36)
        
    def get_name(self):
        """Trả về tên hiển thị của detector."""
        return "Độ Vang"
    
    def _find_template_match(self, plugin_win):
        """Override để sử dụng reverb_template và click position đặc biệt cho Reverb."""
        import cv2
        import numpy as np
        import pyautogui
        import config
        from utils.helpers import ImageHelper, TemplateHelper
        
        # Chụ ảnh màn hình vùng plugin
        x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        print(f"📐 Reverb plugin window size: {w}x{h}")

        # Load reverb_template
        template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"❌ Không thể load template: {self.template_path}")
            return None, 0

        template_h, template_w = template.shape[:2]
        print(f"📐 Reverb template size: {template_w}x{template_h}")

        # Adaptive template matching
        best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
        
        print(f"🏆 Reverb best method: {best_result['method']}")
        print(f"🔍 Reverb confidence: {best_result['confidence']:.3f}")
        print(f"📏 Reverb scale: {best_result['scale']:.2f}")

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
        print(f"🖼 Reverb adaptive debug saved -> {debug_path}")

        if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
            print(f"❌ Reverb template not found. Confidence: {best_result['confidence']:.3f}")
            print(f"💡 Try resizing Reverb plugin window or update reverb template")
            return None, best_result['confidence']

        # Tính toán vị trí click (giữa template để match, sau đó sẽ click phía trên)
        scaled_w, scaled_h = best_result['template_size']
        click_x = x + best_result['location'][0] + scaled_w // 2
        click_y = y + best_result['location'][1] + scaled_h // 2

        print(f"✅ Reverb template found with confidence: {best_result['confidence']:.3f}")
        print(f"🎯 Reverb click position: ({click_x}, {click_y}) [Scale: {best_result['scale']:.2f}]")

        return (click_x, click_y), best_result['confidence']
    
    def _perform_action(self, click_pos, value):
        """Thực hiện click và nhập giá trị vào Reverb plugin."""
        try:
            click_x, click_y = click_pos
            
            # Lưu vị trí chuột hiện tại
            original_x, original_y = pyautogui.position()
            print(f"💾 Saving mouse position: ({original_x}, {original_y})")
            
            print(f"🎛️ Setting Reverb to: {value}")
            
            # Step 1: Click vào giữa template (matching area)
            print(f"👆 Clicking center position: ({click_x}, {click_y})")
            pyautogui.click(click_x, click_y)
            time.sleep(0.1)
            
            # Step 2: Đợi 0.5s
            print("⏰ Waiting 0.5s...")
            time.sleep(0.5)
            
            # Step 3: Click ngay phía trên template (bên ngoài template)
            # Estimate template height và tính vị trí trên đầu template
            estimated_template_height = 100  # Rough estimate
            # Tính vị trí top của template (center - half height)
            template_top_y = click_y - (estimated_template_height // 2)
            # Click ngay phía trên template (10-20px trên đầu template)
            top_click_y = template_top_y - 15  # Click 15px phía trên template
            print(f"👆 Double clicking above template (15px above template top): ({click_x}, {top_click_y})")
            pyautogui.doubleClick(click_x, top_click_y)
            time.sleep(0.2)
            
            # Step 4: Nhập value
            print(f"⌨️ Typing value: {value}")
            pyautogui.typewrite(str(value))
            time.sleep(0.1)
            
            # Step 5: Nhấn Enter
            print("↩️ Pressing Enter")
            pyautogui.press('enter')
            time.sleep(0.2)
            
            # Step 6: Trả chuột về vị trí ban đầu
            print(f"🔄 Restoring mouse position to: ({original_x}, {original_y})")
            pyautogui.moveTo(original_x, original_y)
            
            print(f"✅ Reverb set to {value} successfully")
            self.current_value = value
            return True
            
        except Exception as e:
            print(f"❌ Error setting Reverb: {e}")
            return False
    
    def set_reverb_value(self, value):
        """Đặt giá trị độ vang cụ thể."""
        # Clamp value trong range
        value = max(self.min_value, min(self.max_value, int(value)))
        
        print(f"🎤 Reverb Detector - Setting reverb to: {value}")
        
        if not self._find_cubase_process():
            return False
        
        # Find Reverb plugin window (sử dụng reverb template)
        plugin_win = self._find_reverb_window()
        if not plugin_win:
            return False
        
        # Find template match
        match_result = self._find_template_match(plugin_win)
        if not match_result or match_result[0] is None:
            return False
        
        click_pos, confidence = match_result
        
        # Perform action với value
        return self._perform_action(click_pos, value)
    
    def _find_reverb_window(self):
        """Tìm cửa sổ Reverb plugin."""
        from utils.window_manager import WindowManager
        
        # Try different possible window titles for Reverb
        possible_titles = ["Xvox", "XVOX", "xvox", "X-Vox", "X_Vox"]
        
        for title in possible_titles:
            plugin_win = WindowManager.find_window(title)
            if plugin_win:
                print(f"✅ Found Xvox window: {title}")
                return plugin_win

        print("❌ Xvox plugin window not found")
        print("💡 Make sure Xvox plugin is open and visible")
        return None
    
    def get_reverb_description(self, value):
        """Lấy mô tả cho giá trị độ vang."""
        if value <= 32:
            return "Khô"
        elif value <= 36:
            return "Vừa"
        elif value <= 40:
            return "Ướt"
        else:
            return "Rất ướt"
    
    def reset_to_default(self):
        """Reset về giá trị mặc định."""
        return self.set_reverb_value(self.default_value)
    
    def increase_reverb(self, step=2):
        """Tăng độ vang."""
        new_value = min(self.current_value + step, self.max_value)
        return self.set_reverb_value(new_value)
    
    def decrease_reverb(self, step=2):
        """Giảm độ vang."""
        new_value = max(self.current_value - step, self.min_value)
        return self.set_reverb_value(new_value)
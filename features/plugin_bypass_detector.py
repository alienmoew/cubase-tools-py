from features.auto_tune_detector import AutoTuneDetector
from utils.debug_helper import DebugHelper
from utils.shared_window_manager import SharedWindowManager
from utils.shared_screenshot_helper import SharedScreenshotHelper
import config


class PluginBypassDetector(AutoTuneDetector):
    """Tính năng Bật/Tắt plugin với AUTO-TUNE PRO plugin."""

    def __init__(self, plugin_name="AUTO-TUNE PRO"):
        # Sử dụng config dummy vì đây là toggle function
        super().__init__(
            feature_name="Plugin Bypass",
            template_filename="bypass_off_template.png",  # Default template
            config_prefix="plugin_bypass"  # Dummy config
        )
        self.plugin_name = plugin_name
        
        # Template paths cho cả 2 trạng thái
        self.off_template_path = config.TEMPLATE_PATHS['bypass_off']
        self.on_template_path = config.TEMPLATE_PATHS['bypass_on']
        
        # Override để không validate range vì đây là toggle
        self.is_toggle = True
        
        # Trạng thái hiện tại (None = unknown, True = ON, False = OFF)
        self.current_state = None
    
    def validate_range(self, value):
        """Override - không cần validate cho toggle."""
        return True
    
    def get_current_state(self, silent=False):
        """Phát hiện trạng thái hiện tại của plugin (ON/OFF)."""
        try:
            # 1. Tìm Cubase process
            proc = self._find_cubase_process_silent() if silent else self._find_cubase_process()
            if not proc:
                return None

            # 2. Focus Cubase window và tìm plugin
            plugin_win = self._focus_cubase_window_silent(proc) if silent else self._focus_cubase_window(proc)
            if not plugin_win:
                return None

            # 3. Thử match cả 2 template để xác định trạng thái
            off_pos, off_conf = self._find_template_match_by_path(plugin_win, self.off_template_path, silent)
            on_pos, on_conf = self._find_template_match_by_path(plugin_win, self.on_template_path, silent)
            
            if not silent:
                DebugHelper.print_template_debug(f"🔍 OFF template confidence: {off_conf:.2f}")
                DebugHelper.print_template_debug(f"🔍 ON template confidence: {on_conf:.2f}")
            
            # Xác định trạng thái dựa trên confidence cao hơn
            if off_conf > on_conf and off_conf > 0.7:
                self.current_state = False  # Plugin đang OFF (bypass)
                if not silent:
                    DebugHelper.print_template_debug(f"📴 {self.plugin_name} is currently OFF (bypassed)")
                return False, off_pos
            elif on_conf > off_conf and on_conf > 0.7:
                self.current_state = True   # Plugin đang ON (active)
                if not silent:
                    DebugHelper.print_template_debug(f"🔵 {self.plugin_name} is currently ON (active)")
                return True, on_pos
            else:
                if not silent:
                    DebugHelper.print_template_debug(f"❓ Cannot determine {self.plugin_name} state")
                return None, None

        except Exception as e:
            if not silent:
                DebugHelper.print_always(f"❌ Error detecting plugin state: {e}")
            return None, None

    def toggle_plugin_bypass(self):
        """Toggle bật/tắt plugin dựa trên trạng thái hiện tại."""
        print(f"🔄 Toggling {self.plugin_name} bypass...")
        
        try:
            # Phát hiện trạng thái hiện tại
            state_result = self.get_current_state()
            if state_result is None or state_result[0] is None:
                print("❌ Cannot detect current plugin state")
                return False
            
            current_state, click_pos = state_result
            
            # Click để toggle
            success = self._click_bypass_button(click_pos)
            if success:
                new_state = "ON" if not current_state else "OFF"
                print(f"✅ {self.plugin_name} toggled to {new_state}")
                self.current_state = not current_state  # Cập nhật trạng thái
                return True

            return False

        except Exception as e:
            print(f"❌ Error in plugin bypass toggle: {e}")
            return False
    
    def _find_template_match_by_path(self, plugin_win, template_path, silent=False):
        """Tìm template match với đường dẫn template cụ thể và adaptive matching."""
        import cv2
        import numpy as np
        import pyautogui
        import config
        from utils.helpers import ImageHelper, TemplateHelper
        import os
        
        try:
            # Chụp ảnh màn hình vùng plugin
            x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

            template_name = os.path.splitext(os.path.basename(template_path))[0]
            if not silent:
                DebugHelper.print_template_debug(f"🎯 Bypass plugin window size: {w}x{h} - Testing: {template_name}")

            # Load template với đường dẫn cụ thể
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                if not silent:
                    DebugHelper.print_always(f"❌ Không thể load template: {template_path}")
                return None, 0

            template_h, template_w = template.shape[:2]
            if not silent:
                DebugHelper.print_template_debug(f"🎯 Bypass template size: {template_w}x{template_h}")

            # Adaptive template matching
            best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
            
            if not silent:
                DebugHelper.print_template_debug(f"🏆 Bypass {template_name} best method: {best_result['method']}")
                DebugHelper.print_template_debug(f"🔍 Bypass {template_name} confidence: {best_result['confidence']:.3f}")
                DebugHelper.print_template_debug(f"📏 Bypass {template_name} scale: {best_result['scale']:.2f}")

            # Save debug image với adaptive result
            debug_filename = f"bypass_{template_name}_adaptive_debug.png"
            
            # Create scaled template for debug visualization
            if best_result['scale'] != 1.0:
                scaled_w, scaled_h = best_result['template_size']
                debug_template = cv2.resize(template, (scaled_w, scaled_h))
            else:
                debug_template = template
            
            # Save debug image only if not silent and debug is enabled
            if not silent and DebugHelper.should_save_debug_images():
                debug_path = ImageHelper.save_template_debug_image(
                    screenshot_np, debug_template, best_result['location'], 
                    best_result['confidence'], debug_filename
                )
                DebugHelper.print_template_debug(f"🖼 Bypass {template_name} adaptive debug saved -> {debug_path}")

            if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                if not silent:
                    DebugHelper.print_template_debug(f"❌ Bypass template not found: {template_name}. Confidence: {best_result['confidence']:.3f}")
                return None, best_result['confidence']

            # Tính toán vị trí click ở giữa scaled template
            scaled_w, scaled_h = best_result['template_size']
            click_x = x + best_result['location'][0] + scaled_w // 2
            click_y = y + best_result['location'][1] + scaled_h // 2

            if not silent:
                DebugHelper.print_template_debug(f"✅ Bypass template found: {template_name} with confidence: {best_result['confidence']:.3f}")
                DebugHelper.print_template_debug(f"🎯 Bypass click position: ({click_x}, {click_y}) [Scale: {best_result['scale']:.2f}]")

            return (click_x, click_y), best_result['confidence']
            
        except Exception as e:
            if not silent:
                DebugHelper.print_always(f"❌ Error finding bypass template {template_path}: {e}")
            return None, 0
    
    def _find_cubase_process_silent(self):
        """Tìm tiến trình Cubase mà không hiển thị popup error."""
        from utils.process_finder import CubaseProcessFinder
        
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Không tìm thấy tiến trình Cubase!")
        return proc

    def _focus_cubase_window_silent(self, proc):
        """Focus cửa sổ Cubase và tìm plugin window mà không hiển thị popup error."""
        plugin_key = self._get_plugin_key()
        return SharedWindowManager.focus_plugin_window_silent(plugin_key, proc)
    
    def _focus_cubase_window(self, proc):
        """Focus Cubase window và tìm plugin với error messages."""
        plugin_key = self._get_plugin_key()
        return SharedWindowManager.focus_plugin_window(plugin_key, proc, silent=False)
    
    def _get_plugin_key(self):
        """Get plugin key based on plugin name."""
        name_to_key = {
            'AUTO-TUNE PRO': 'autotune',
            'SoundShifter Pitch Stereo': 'soundshifter', 
            'Pro-Q 3': 'proq3',
            'AUTO-KEY': 'autokey'
        }
        return name_to_key.get(self.plugin_name, 'autotune')  # Default to autotune
    
    def _click_bypass_button(self, click_pos):
        """Click vào bypass button."""
        try:
            from utils.helpers import MouseHelper
            
            click_x, click_y = click_pos

            # Click vào giữa bypass button
            MouseHelper.safe_click(click_x, click_y, delay=config.UI_DELAYS['click_delay_short'])
            
            print(f"🔄 Clicked bypass button at ({click_x}, {click_y})")
            return True

        except Exception as e:
            print(f"❌ Error clicking bypass button: {e}")
            return False
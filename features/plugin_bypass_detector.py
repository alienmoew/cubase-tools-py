from features.auto_tune_detector import AutoTuneDetector


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
        self.off_template_path = "templates/bypass_off_template.png"
        self.on_template_path = "templates/bypass_on_template.png"
        
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
            off_pos, off_conf = self._find_template_match_by_path(plugin_win, self.off_template_path)
            on_pos, on_conf = self._find_template_match_by_path(plugin_win, self.on_template_path)
            
            print(f"🔍 OFF template confidence: {off_conf:.2f}")
            print(f"🔍 ON template confidence: {on_conf:.2f}")
            
            # Xác định trạng thái dựa trên confidence cao hơn
            if off_conf > on_conf and off_conf > 0.7:
                self.current_state = False  # Plugin đang OFF (bypass)
                print(f"📴 {self.plugin_name} is currently OFF (bypassed)")
                return False, off_pos
            elif on_conf > off_conf and on_conf > 0.7:
                self.current_state = True   # Plugin đang ON (active)
                print(f"🔵 {self.plugin_name} is currently ON (active)")
                return True, on_pos
            else:
                print(f"❓ Cannot determine {self.plugin_name} state")
                return None, None

        except Exception as e:
            print(f"❌ Error detecting plugin state: {e}")
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
    
    def _find_template_match_by_path(self, plugin_win, template_path):
        """Tìm template match với đường dẫn template cụ thể."""
        import cv2
        import numpy as np
        import pyautogui
        import config
        
        try:
            # Chụp ảnh màn hình vùng plugin
            x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

            # Load template với đường dẫn cụ thể
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"❌ Không thể load template: {template_path}")
                return None, 0

            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            print(f"🔍 Template matching confidence for {template_path}: {max_val:.2f}")

            if max_val < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ Template not found: {template_path}. Confidence: {max_val:.2f}")
                return None, max_val

            # Tính toán vị trí click ở giữa template
            template_height = template.shape[0]
            template_width = template.shape[1]
            click_x = x + max_loc[0] + template_width // 2
            click_y = y + max_loc[1] + template_height // 2

            print(f"✅ Template found: {template_path} with confidence: {max_val:.2f}")
            print(f"🎯 Click position: ({click_x}, {click_y})")

            return (click_x, click_y), max_val
            
        except Exception as e:
            print(f"❌ Error finding template {template_path}: {e}")
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
        from utils.window_manager import WindowManager
        import time
        
        # 1. Focus Cubase process
        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        if not hwnd:
            print("❌ Không thể focus cửa sổ Cubase!")
            return None
        
        time.sleep(0.3)
        
        # 2. Tìm cửa sổ AUTO-TUNE PRO mà không hiển thị popup
        plugin_win = WindowManager.find_window("AUTO-TUNE PRO")
        if not plugin_win:
            print("❌ Không tìm thấy cửa sổ AUTO-TUNE PRO!")
            return None

        print(f"✅ Đã tìm thấy cửa sổ AUTO-TUNE PRO")
        return plugin_win
    
    def _click_bypass_button(self, click_pos):
        """Click vào bypass button."""
        try:
            from utils.helpers import MouseHelper
            
            click_x, click_y = click_pos

            # Click vào giữa bypass button
            MouseHelper.safe_click(click_x, click_y, delay=0.3)
            
            print(f"🔄 Clicked bypass button at ({click_x}, {click_y})")
            return True

        except Exception as e:
            print(f"❌ Error clicking bypass button: {e}")
            return False
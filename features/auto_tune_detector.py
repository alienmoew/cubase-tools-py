import time
import cv2
import numpy as np
import pyautogui

import config
from features.base_feature import BaseFeature
from utils.helpers import ImageHelper, MessageHelper, ConfigHelper, MouseHelper
from utils.process_finder import CubaseProcessFinder
from utils.window_manager import WindowManager


class AutoTuneDetector(BaseFeature):
    """Base class cho tất cả Auto-Tune detector features."""

    def __init__(self, feature_name, template_filename, config_prefix):
        """
        Args:
            feature_name: Tên hiển thị của feature (ví dụ: "Return Speed")
            template_filename: Tên file template (ví dụ: "return_speed_template.png")
            config_prefix: Prefix trong config file (ví dụ: "return_speed")
        """
        super().__init__()
        self.feature_name = feature_name
        self.template_path = f"templates/{template_filename}"
        self.config_prefix = config_prefix
        
        # Load giá trị mặc định từ config
        self.default_values = ConfigHelper.load_default_values()
        self.current_value = self.default_values.get(f'{config_prefix}_default', 0)
        
        # Lấy range values từ config
        self.min_value = self.default_values.get(f'{config_prefix}_min', 0)
        self.max_value = self.default_values.get(f'{config_prefix}_max', 100)
        self.default_value = self.default_values.get(f'{config_prefix}_default', 0)

    def get_name(self):
        return f"Chỉnh {self.feature_name}"

    def get_current_value(self):
        """Lấy giá trị hiện tại."""
        return self.current_value

    def reset_value(self):
        """Reset giá trị về mặc định (chỉ counter)."""
        self.current_value = self.default_value
        print(f"🔄 {self.feature_name} value reset to {self.default_value}")

    def set_value(self, value):
        """Set giá trị cụ thể."""
        self.current_value = value
        print(f"🔢 {self.feature_name} value set to: {self.current_value}")

    def validate_range(self, value):
        """Validate giá trị trong range cho phép."""
        if value < self.min_value or value > self.max_value:
            print(f"❌ Giá trị {value} nằm ngoài khoảng cho phép ({self.min_value}-{self.max_value})")
            return False
        return True

    def _find_cubase_process(self):
        """Tìm tiến trình Cubase."""
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Không tìm thấy tiến trình Cubase!")
            MessageHelper.show_error(
                "Lỗi Cubase", 
                f"Không tìm thấy tiến trình Cubase!\n\nVui lòng:\n• Mở Cubase trước khi sử dụng\n• Đảm bảo Cubase đang chạy"
            )
        return proc

    def _focus_cubase_window(self, proc):
        """Focus cửa sổ Cubase và tìm plugin window."""
        # 1. Focus Cubase process
        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        if not hwnd:
            print("❌ Không thể focus cửa sổ Cubase!")
            MessageHelper.show_error(
                "Lỗi Focus Window", 
                "Không thể focus cửa sổ Cubase!"
            )
            return None
        
        time.sleep(0.3)
        
        # 2. Tìm cửa sổ AUTO-TUNE PRO
        plugin_win = WindowManager.find_window("AUTO-TUNE PRO")
        if not plugin_win:
            print("❌ Không tìm thấy cửa sổ AUTO-TUNE PRO!")
            MessageHelper.show_error(
                "Lỗi Plugin", 
                "Không tìm thấy cửa sổ AUTO-TUNE PRO!\n\nVui lòng:\n• Mở plugin AUTO-TUNE PRO trong Cubase\n• Đảm bảo cửa sổ plugin đang hiển thị"
            )
            return None

        # 3. Activate plugin window
        plugin_win.activate()
        time.sleep(0.3)
        return plugin_win

    def _find_template_match(self, plugin_win):
        """Tìm template match trong cửa sổ plugin."""
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

        # Tính toán vị trí click (90% từ top của template)
        template_height = template.shape[0]
        click_x = x + max_loc[0] + template.shape[1] // 2
        click_y = y + max_loc[1] + int(template_height * 0.9)

        print(f"✅ Template found for {self.feature_name.lower()} with confidence: {max_val:.2f}")
        print(f"🎯 {self.feature_name} click position: ({click_x}, {click_y})")

        return (click_x, click_y), max_val

    def _process_value_input(self, click_pos, value):
        """Xử lý việc click và nhập giá trị."""
        try:
            click_x, click_y = click_pos

            # Click vào vị trí template
            MouseHelper.safe_click(click_x, click_y, delay=0.2)
            
            # Select all và nhập giá trị mới
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.typewrite(str(value))
            time.sleep(0.1)
            pyautogui.press('enter')

            print(f"🔄 {self.feature_name}: Entered {value} and pressed Enter")
            return True

        except Exception as e:
            print(f"❌ Error in {self.feature_name.lower()} input process: {e}")
            return False

    def set_auto_tune_value(self, value):
        """Method chung để set giá trị trong AUTO-TUNE plugin."""
        if not self.validate_range(value):
            return False

        print(f"🎛️ Setting {self.feature_name} to: {value}")

        try:
            # 1. Tìm Cubase process
            proc = self._find_cubase_process()
            if not proc:
                return False

            # 2. Focus Cubase window
            plugin_win = self._focus_cubase_window(proc)
            if not plugin_win:
                return False

            # 3. Tìm template và click
            click_pos, confidence = self._find_template_match(plugin_win)
            if not click_pos:
                return False

            # 4. Xử lý input
            success = self._process_value_input(click_pos, value)
            if success:
                self.set_value(value)
                return True

            return False

        except Exception as e:
            print(f"❌ Error in {self.feature_name.lower()} process: {e}")
            return False

    def reset_to_default(self):
        """Reset về giá trị mặc định từ config."""
        return self.set_auto_tune_value(self.default_value)

    def execute(self):
        """Thực thi chức năng (legacy method)."""
        return self.set_auto_tune_value(self.current_value)
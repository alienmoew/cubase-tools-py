"""
Volume Detector - Điều chỉnh âm lượng nhạc trực tiếp trong Cubase
"""
import time
import pyautogui
import cv2
import numpy as np

import config
from features.base_feature import BaseFeature
from utils.helpers import ConfigHelper, ImageHelper, TemplateHelper, MessageHelper, MouseHelper
from utils.process_finder import CubaseProcessFinder
from utils.window_manager import WindowManager


class VolumeDetector(BaseFeature):
    """Tính năng điều chỉnh âm lượng nhạc trực tiếp trong Cubase."""
    
    def __init__(self):
        super().__init__()
        
        # Template path
        self.template_path = config.TEMPLATE_PATHS['volume_template']
        
        # Load default values
        default_values = ConfigHelper.load_default_values()
        self.min_value = default_values.get('volume_min', -7)
        self.max_value = default_values.get('volume_max', 0)
        self.default_value = default_values.get('volume_default', -3)
        self.current_value = self.default_value
        
    def get_name(self):
        """Trả về tên hiển thị của detector."""
        return "Volume Nhạc"
    
    def validate_range(self, value):
        """Kiểm tra value có trong range không."""
        return self.min_value <= value <= self.max_value
    
    def _find_cubase_process(self):
        """Tìm tiến trình Cubase."""
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Không tìm thấy tiến trình Cubase!")
            MessageHelper.show_error(
                "Lỗi Cubase", 
                "Không tìm thấy tiến trình Cubase!\n\nVui lòng:\n• Mở Cubase trước khi sử dụng\n• Đảm bảo Cubase đang chạy"
            )
        return proc
    
    def _focus_cubase_window(self, proc):
        """Focus cửa sổ Cubase chính."""
        # Focus Cubase process trước
        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        if not hwnd:
            print("❌ Không thể focus tiến trình Cubase!")
            return None
        
        time.sleep(0.3)
        
        # Tìm cửa sổ Cubase Pro chính
        cubase_window = WindowManager.find_window("Cubase Pro")
        if not cubase_window:
            print("❌ Không tìm thấy cửa sổ 'Cubase Pro'!")
            MessageHelper.show_error(
                "Lỗi Cubase Window", 
                "Không tìm thấy cửa sổ 'Cubase Pro'!\n\nVui lòng đảm bảo Cubase Pro đang mở và hiển thị trên màn hình."
            )
            return None
        
        # Activate cửa sổ Cubase Pro
        cubase_window.activate()
        time.sleep(0.5)  # Đợi focus ổn định
        
        print(f"✅ Focused Cubase Pro window: {cubase_window.title}")
        
        # Trả về handle của cửa sổ Cubase Pro để dùng cho screenshot
        return cubase_window
    
    def _find_template_match(self, cubase_window):
        """Tìm template match trong Cubase window."""
        try:
            # Lấy vùng Cubase window
            x, y = cubase_window.left, cubase_window.top
            w, h = cubase_window.width, cubase_window.height
            print(f"📐 Cubase Pro window: {x}, {y}, {w}x{h}")
            
            # Chụ ảnh chỉ vùng Cubase window
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            print(f"📐 Cubase Pro screenshot size: {screenshot.width}x{screenshot.height}")
            
            # Load template
            template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"❌ Không thể load template: {self.template_path}")
                return None, 0
            
            template_h, template_w = template.shape[:2]
            print(f"📐 Volume template size: {template_w}x{template_h}")
            
            # Adaptive template matching
            best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
            
            print(f"🏆 Volume best method: {best_result['method']}")
            print(f"🔍 Volume confidence: {best_result['confidence']:.3f}")
            print(f"📏 Volume scale: {best_result['scale']:.2f}")
            
            # Save debug image
            debug_filename = "volume_adaptive_debug.png"
            
            if best_result['scale'] != 1.0:
                scaled_w, scaled_h = best_result['template_size']
                debug_template = cv2.resize(template, (scaled_w, scaled_h))
            else:
                debug_template = template
            
            debug_path = ImageHelper.save_template_debug_image(
                screenshot_np, debug_template, best_result['location'], 
                best_result['confidence'], debug_filename
            )
            print(f"🖼 Volume adaptive debug saved -> {debug_path}")
            
            if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ Volume template not found. Confidence: {best_result['confidence']:.3f}")
                print(f"💡 Try adjusting Cubase layout or update volume template")
                return None, best_result['confidence']
            
            # Tính toán vị trí click (giữa template) - chuyển đổi từ relative sang absolute coordinates
            scaled_w, scaled_h = best_result['template_size']
            click_x = x + best_result['location'][0] + scaled_w // 2
            click_y = y + best_result['location'][1] + scaled_h // 2
            
            print(f"✅ Volume template found with confidence: {best_result['confidence']:.3f}")
            print(f"🎯 Volume click position: ({click_x}, {click_y}) [Scale: {best_result['scale']:.2f}]")
            
            return (click_x, click_y), best_result['confidence']
            
        except Exception as e:
            print(f"❌ Error finding volume template: {e}")
            return None, 0
    
    def _perform_action(self, click_pos, value):
        """Thực hiện double click và nhập giá trị."""
        try:
            click_x, click_y = click_pos
            
            # Lưu vị trí chuột hiện tại
            original_x, original_y = pyautogui.position()
            print(f"💾 Saving mouse position: ({original_x}, {original_y})")
            
            print(f"🔊 Setting volume to: {value}")
            
            # Step 1: Double click vào giữa template
            print(f"👆 Double clicking volume control: ({click_x}, {click_y})")
            pyautogui.doubleClick(click_x, click_y)
            time.sleep(0.3)
            
            # Step 2: Nhập giá trị
            print(f"⌨️ Typing value: {value}")
            pyautogui.typewrite(str(value))
            time.sleep(0.1)
            
            # Step 3: Nhấn Enter để xác nhận
            print("↩️ Pressing Enter")
            pyautogui.press('enter')
            time.sleep(0.2)
            
            # Step 4: Trả chuột về vị trí ban đầu
            print(f"🔄 Restoring mouse position to: ({original_x}, {original_y})")
            pyautogui.moveTo(original_x, original_y)
            
            print(f"✅ Volume set to {value} successfully")
            self.current_value = value
            return True
            
        except Exception as e:
            print(f"❌ Error setting volume: {e}")
            return False
    
    def set_volume(self, value):
        """Đặt giá trị âm lượng cụ thể."""
        # Validate và clamp value
        if not self.validate_range(value):
            print(f"⚠️ Volume value {value} out of range [{self.min_value}, {self.max_value}]")
            value = max(self.min_value, min(self.max_value, value))
        
        print(f"🔊 Volume Detector - Setting volume to: {value}")
        
        # 1. Find và focus Cubase process
        proc = self._find_cubase_process()
        if not proc:
            return False
        
        # 2. Focus Cubase window
        cubase_window = self._focus_cubase_window(proc)
        if not cubase_window:
            return False
        
        # 2.5. Nhấn tổ hợp phím Shift+T trước khi thao tác (nhanh)
        print("⌨️ Pressing Shift+T...")
        try:
            # Nhấn Shift+T nhanh
            pyautogui.keyDown('shift')
            pyautogui.keyDown('t')
            time.sleep(0.05)  # Giữ rất ngắn
            pyautogui.keyUp('t')
            pyautogui.keyUp('shift')
            time.sleep(0.2)  # Đợi ngắn hơn nhiều
            print("✅ Shift+T done")
        except Exception as e:
            print(f"❌ Hotkey error: {e}")
        
        # 3. Find volume template trong Cubase window
        match_result = self._find_template_match(cubase_window)
        if not match_result or match_result[0] is None:
            return False
        
        click_pos, confidence = match_result
        
        # 4. Perform action
        return self._perform_action(click_pos, value)
    
    def increase_volume(self, step=1):
        """Tăng âm lượng."""
        new_value = min(self.current_value + step, self.max_value)
        return self.set_volume(new_value)
    
    def decrease_volume(self, step=1):
        """Giảm âm lượng."""
        new_value = max(self.current_value - step, self.min_value)
        return self.set_volume(new_value)
    
    def reset_to_default(self):
        """Reset về giá trị mặc định."""
        return self.set_volume(self.default_value)
    
    def get_volume_description(self, value):
        """Lấy mô tả cho giá trị âm lượng."""
        if value >= -1:
            return "Rất to"
        elif value >= -3:
            return "To"
        elif value >= -5:
            return "Vừa"
        else:
            return "Nhỏ"
    
    def toggle_mute(self):
        """Toggle tắt/bật âm lượng nhạc."""
        print("🔇 Toggling music mute...")
        
        # 1. Find và focus Cubase process
        proc = self._find_cubase_process()
        if not proc:
            return False
        
        # 2. Focus Cubase window
        cubase_window = self._focus_cubase_window(proc)
        if not cubase_window:
            return False
        
        # 2.5. Nhấn tổ hợp phím Shift+T trước khi thao tác (nhanh)
        print("⌨️ Pressing Shift+T...")
        try:
            # Nhấn Shift+T nhanh
            pyautogui.keyDown('shift')
            pyautogui.keyDown('t')
            time.sleep(0.05)  # Giữ rất ngắn
            pyautogui.keyUp('t')
            pyautogui.keyUp('shift')
            time.sleep(0.2)  # Đợi ngắn hơn nhiều
            print("✅ Shift+T done")
        except Exception as e:
            print(f"❌ Hotkey error: {e}")
        
        # 3. Find mute template trong Cubase window
        match_result = self._find_mute_template_match(cubase_window)
        if not match_result or match_result[0] is None:
            return False
        
        click_pos, confidence = match_result
        
        # 4. Perform click
        return self._perform_mute_click(click_pos)
    
    def _find_mute_template_match(self, cubase_window):
        """Tìm mute template match trong Cubase window."""
        try:
            # Lấy vùng Cubase window
            x, y = cubase_window.left, cubase_window.top
            w, h = cubase_window.width, cubase_window.height
            print(f"📐 Cubase Pro window for mute: {x}, {y}, {w}x{h}")
            
            # Chụ ảnh chỉ vùng Cubase window
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            print(f"📐 Cubase Pro mute screenshot size: {screenshot.width}x{screenshot.height}")
            
            # Load mute template
            mute_template_path = config.TEMPLATE_PATHS['mute_music_template']
            template = cv2.imread(mute_template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"❌ Không thể load mute template: {mute_template_path}")
                return None, 0
            
            template_h, template_w = template.shape[:2]
            print(f"📐 Mute template size: {template_w}x{template_h}")
            
            # Adaptive template matching
            best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
            
            print(f"🏆 Mute best method: {best_result['method']}")
            print(f"🔍 Mute confidence: {best_result['confidence']:.3f}")
            print(f"📏 Mute scale: {best_result['scale']:.2f}")
            
            # Save debug image
            debug_filename = "mute_music_adaptive_debug.png"
            
            if best_result['scale'] != 1.0:
                scaled_w, scaled_h = best_result['template_size']
                debug_template = cv2.resize(template, (scaled_w, scaled_h))
            else:
                debug_template = template
            
            debug_path = ImageHelper.save_template_debug_image(
                screenshot_np, debug_template, best_result['location'], 
                best_result['confidence'], debug_filename
            )
            print(f"🖼 Mute adaptive debug saved -> {debug_path}")
            
            if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ Mute template not found. Confidence: {best_result['confidence']:.3f}")
                print(f"💡 Try adjusting Cubase layout or update mute template")
                return None, best_result['confidence']
            
            # Tính toán vị trí click (giữa template) - chuyển đổi từ relative sang absolute coordinates
            scaled_w, scaled_h = best_result['template_size']
            click_x = x + best_result['location'][0] + scaled_w // 2
            click_y = y + best_result['location'][1] + scaled_h // 2
            
            print(f"✅ Mute template found with confidence: {best_result['confidence']:.3f}")
            print(f"🎯 Mute click position: ({click_x}, {click_y}) [Scale: {best_result['scale']:.2f}]")
            
            return (click_x, click_y), best_result['confidence']
            
        except Exception as e:
            print(f"❌ Error finding mute template: {e}")
            return None, 0
    
    def _perform_mute_click(self, click_pos):
        """Thực hiện click vào nút mute."""
        try:
            click_x, click_y = click_pos
            
            # Lưu vị trí chuột hiện tại
            original_x, original_y = pyautogui.position()
            print(f"💾 Saving mouse position: ({original_x}, {original_y})")
            
            print(f"🔇 Clicking mute button: ({click_x}, {click_y})")
            
            # Click vào nút mute
            MouseHelper.safe_click(click_x, click_y)
            time.sleep(0.2)
            
            # Trả chuột về vị trí ban đầu
            print(f"🔄 Restoring mouse position to: ({original_x}, {original_y})")
            pyautogui.moveTo(original_x, original_y)
            
            print(f"✅ Mute button clicked successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error clicking mute button: {e}")
            return False

    def execute(self):
        """Abstract method từ BaseFeature - không sử dụng cho volume detector."""
        print("💡 Volume detector sử dụng GUI slider, không cần execute trực tiếp")
        return True
from features.auto_tune_detector import AutoTuneDetector
import pyautogui
import time


class SoundShifterDetector(AutoTuneDetector):
    """Tính năng Nâng/Hạ Tone với SoundShifter Pitch Stereo plugin."""

    def __init__(self):
        super().__init__(
            feature_name="SoundShifter Pitch",
            template_filename="soundshifter_pitch_template.png",
            config_prefix="soundshifter_pitch"
        )
        self.plugin_name = "SoundShifter Pitch Stereo"
        self.current_value = 0  # Giá trị hiện tại (-4 to +4)
        
    def raise_tone(self, num_tones=1):
        """Nâng tone lên (mỗi tone = +2)."""
        target_value = self.current_value + (num_tones * 2)
        return self.set_pitch_value(target_value)
    
    def lower_tone(self, num_tones=1):
        """Hạ tone xuống (mỗi tone = -2)."""
        target_value = self.current_value - (num_tones * 2)
        return self.set_pitch_value(target_value)
    
    def set_pitch_value(self, value):
        """Đặt giá trị pitch cho SoundShifter."""
        if not self.validate_range(value):
            print(f"❌ Giá trị {value} vượt quá giới hạn [{self.min_value}, {self.max_value}]")
            return False
            
        print(f"🎵 Setting SoundShifter pitch to: {value}")
        
        try:
            # 1. Tìm Cubase process
            proc = self._find_cubase_process()
            if not proc:
                return False

            # 2. Focus Cubase window và tìm plugin
            plugin_win = self._focus_cubase_window(proc)
            if not plugin_win:
                return False

            # 3. Tìm template và double-click
            click_pos, confidence = self._find_template_match(plugin_win)
            if not click_pos:
                return False

            # 4. Double-click để mở input field
            success = self._double_click_input_field(click_pos)
            if not success:
                return False

            # 5. Input giá trị mới
            success = self._input_pitch_value(value)
            if success:
                self.current_value = value
                print(f"✅ SoundShifter pitch set to {value}")
                return True

            return False

        except Exception as e:
            print(f"❌ Error setting SoundShifter pitch: {e}")
            return False
    
    def _double_click_input_field(self, click_pos):
        """Double-click vào input field để activate editing."""
        try:
            from utils.helpers import MouseHelper
            
            click_x, click_y = click_pos

            # Double-click vào input field
            MouseHelper.safe_double_click(click_x, click_y, delay=0.2)
            
            print(f"🖱️ Double-clicked input field at ({click_x}, {click_y})")
            return True

        except Exception as e:
            print(f"❌ Error double-clicking input field: {e}")
            return False
    
    def _input_pitch_value(self, value):
        """Nhập giá trị pitch vào field đã được activate."""
        try:
            # Đợi một chút để field activate
            time.sleep(0.3)
            
            # Clear field hiện tại (Ctrl+A để select all)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # Type giá trị mới
            pyautogui.typewrite(str(value))
            time.sleep(0.2)
            
            # Press Enter để confirm
            pyautogui.press('enter')
            
            print(f"⌨️ Typed pitch value: {value}")
            return True

        except Exception as e:
            print(f"❌ Error inputting pitch value: {e}")
            return False
    
    def get_tone_description(self, value):
        """Lấy mô tả tone dựa trên giá trị."""
        if value == 0:
            return "Bình thường"
        elif value > 0:
            tones = value // 2
            remainder = value % 2
            if remainder == 0:
                return f"+{tones} tone"
            else:
                if tones == 0:
                    return f"+{remainder}/2 tone"
                else:
                    return f"+{tones} tone +{remainder}/2"
        else:
            abs_val = abs(value)
            tones = abs_val // 2
            remainder = abs_val % 2
            if remainder == 0:
                return f"-{tones} tone"
            else:
                if tones == 0:
                    return f"-{remainder}/2 tone"
                else:
                    return f"-{tones} tone -{remainder}/2"
    
    def reset_pitch(self):
        """Reset pitch về 0."""
        return self.set_pitch_value(0)
    
    def _focus_cubase_window(self, proc):
        """Override để tìm SoundShifter plugin thay vì AUTO-TUNE PRO."""
        from utils.window_manager import WindowManager
        from utils.helpers import MessageHelper
        import time
        
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
        
        # 2. Tìm cửa sổ SoundShifter Pitch Stereo
        plugin_win = WindowManager.find_window("SoundShifter Pitch Stereo")
        if not plugin_win:
            print("❌ Không tìm thấy cửa sổ SoundShifter Pitch Stereo!")
            MessageHelper.show_error(
                "Lỗi Plugin Window", 
                f"Không tìm thấy cửa sổ {self.plugin_name}!\n\nVui lòng:\n• Mở plugin {self.plugin_name} trong Cubase\n• Đảm bảo cửa sổ plugin hiển thị trên màn hình"
            )
            return None

        print(f"✅ Đã tìm thấy cửa sổ {self.plugin_name}")
        
        # 3. Activate plugin window
        plugin_win.activate()
        time.sleep(0.3)
        print(f"🎯 Activated {self.plugin_name} window")
        
        return plugin_win
    
    def _find_template_match(self, plugin_win):
        """Override để sử dụng vị trí click 40% từ trên xuống với adaptive matching."""
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

        print(f"📜 SoundShifter plugin window size: {w}x{h}")

        # Load template
        template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"❌ Không thể load template: {self.template_path}")
            return None, 0

        template_h, template_w = template.shape[:2]
        print(f"📜 SoundShifter template size: {template_w}x{template_h}")

        # Adaptive template matching
        best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
        
        print(f"🏆 SoundShifter best method: {best_result['method']}")
        print(f"🔍 SoundShifter confidence: {best_result['confidence']:.3f}")
        print(f"📏 SoundShifter scale: {best_result['scale']:.2f}")

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
        print(f"🖼 SoundShifter adaptive debug saved -> {debug_path}")

        if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
            print(f"❌ SoundShifter template not found. Confidence: {best_result['confidence']:.3f}")
            print(f"💡 Try resizing SoundShifter plugin window or update template")
            return None, best_result['confidence']

        # Tính toán vị trí click (40% từ top của scaled template)
        scaled_w, scaled_h = best_result['template_size']
        click_x = x + best_result['location'][0] + scaled_w // 2
        click_y = y + best_result['location'][1] + int(scaled_h * 0.4)  # 40% từ trên xuống

        print(f"✅ SoundShifter template found with confidence: {best_result['confidence']:.3f}")
        print(f"🎯 SoundShifter click position: ({click_x}, {click_y}) - 40% from top [Scale: {best_result['scale']:.2f}]")

        return (click_x, click_y), best_result['confidence']
"""
XVox Detector - Điều chỉnh tất cả controls của plugin XVox
Bao gồm: COMP, Reverb, Bass (LOW), Treble (HIGH)
"""
import time
import pyautogui
import cv2
import numpy as np

import config
from features.base_feature import BaseFeature
from utils.helpers import ImageHelper, TemplateHelper, MessageHelper, MouseHelper, OCRHelper, ConfigHelper

class XVoxDetector(BaseFeature):
    """Tính năng điều chỉnh tất cả controls của XVox plugin."""
    
    def __init__(self):
        super().__init__()
        self.feature_name = "XVox Controls"
        
        # Setup Tesseract for OCR (like original)
        OCRHelper.setup_tesseract()
        
        # Template paths
        self.comp_template_path = config.TEMPLATE_PATHS['comp_template']
        self.reverb_template_path = config.TEMPLATE_PATHS['reverb_template'] 
        self.tone_mic_template_path = config.TEMPLATE_PATHS['tone_mic_template']
        
        # Load default values
        self.default_values = ConfigHelper.load_default_values()
        
        # COMP settings
        self.comp_min = self.default_values.get('xvox_volume_min', 30)
        self.comp_max = self.default_values.get('xvox_volume_max', 60)
        self.comp_default = self.default_values.get('xvox_volume_default', 45)
        self.current_comp = self.comp_default
        
        # Reverb settings
        self.reverb_min = self.default_values.get('reverb_min', 30)
        self.reverb_max = self.default_values.get('reverb_max', 42)
        self.reverb_default = self.default_values.get('reverb_default', 36)
        self.current_reverb = self.reverb_default
        
        # Bass settings
        self.bass_min = self.default_values.get('bass_min', -30)
        self.bass_max = self.default_values.get('bass_max', 30)
        self.bass_default = self.default_values.get('bass_default', 0)
        self.current_bass = self.bass_default
        
        # Treble settings  
        self.treble_min = self.default_values.get('treble_min', -20)
        self.treble_max = self.default_values.get('treble_max', 30)
        self.treble_default = self.default_values.get('treble_default', 0)
        self.current_treble = self.treble_default
        
        self.LOW_REL_X_POS = 0.15  # LOW ở gần bên trái
        self.LOW_REL_Y_POS = 0.90  # LOW ở giữa chiều dọc
        self.HIGH_REL_X_POS = 0.60 # HIGH ở gần bên phải
        self.HIGH_REL_Y_POS = 0.90 # HIGH ở giữa chiều dọc
        
    def get_name(self):
        """Trả về tên hiển thị của detector."""
        return "XVox Controls"
    
    def _find_cubase_process(self):
        """Tìm Cubase process."""
        from utils.process_finder import CubaseProcessFinder
        proc = CubaseProcessFinder.find()
        if not proc:
            print("❌ Cubase process not found!")
            MessageHelper.show_error("Lỗi Process", "Không tìm thấy Cubase process!")
        return proc
    
    def _find_xvox_window(self):
        """Tìm cửa sổ XVox plugin."""
        from utils.window_manager import WindowManager
        import pygetwindow as gw
        
        # Try different possible window titles for XVox
        possible_titles = ["Xvox", "XVOX", "xvox", "X-Vox", "X_Vox", "XVox", "X Vox"]
        
        for title in possible_titles:
            plugin_win = WindowManager.find_window(title)
            if plugin_win:
                print(f"✅ Found XVox window: {title}")
                return plugin_win
        
        # Debug: Print all available windows
        print("❌ XVox plugin window not found")
        print("💡 Searching for windows containing 'vox' or 'x-vox'...")
        all_windows = gw.getAllWindows()
        vox_windows = [w for w in all_windows if 'vox' in w.title.lower()]
        
        if vox_windows:
            print(f"📋 Found {len(vox_windows)} window(s) with 'vox' in title:")
            for w in vox_windows:
                print(f"   • '{w.title}'")
        else:
            print("💡 No windows with 'vox' in title found")
        
        print("💡 Make sure XVox plugin is open and visible")
        return None
    
    def _focus_cubase_window(self, proc):
        """Focus cửa sổ Cubase."""
        from utils.window_manager import WindowManager
        
        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
        if not hwnd:
            print("❌ Không thể focus cửa sổ Cubase!")
            MessageHelper.show_error("Lỗi Focus Window", "Không thể focus cửa sổ Cubase!")
            return None
        
        time.sleep(0.1)  # Giảm từ 0.3 xuống 0.1
        return hwnd
    
    def _find_template_match(self, plugin_win, template_path, control_name):
        """Tìm template match cho control cụ thể."""
        # Chụ ảnh màn hình vùng plugin
        x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        print(f"📐 XVox plugin window size: {w}x{h}")

        # Load template
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"❌ Không thể load template: {template_path}")
            return None, 0

        template_h, template_w = template.shape[:2]
        print(f"📐 {control_name} template size: {template_w}x{template_h}")

        # Adaptive template matching
        best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
        
        print(f"🏆 {control_name} best method: {best_result['method']}")
        print(f"🔍 {control_name} confidence: {best_result['confidence']:.3f}")
        print(f"📏 {control_name} scale: {best_result['scale']:.2f}")

        # Save debug image
        debug_filename = f"{control_name.lower()}_adaptive_debug.png"
        
        if best_result['scale'] != 1.0:
            scaled_w, scaled_h = best_result['template_size']
            debug_template = cv2.resize(template, (scaled_w, scaled_h))
        else:
            debug_template = template
        
        debug_path = ImageHelper.save_template_debug_image(
            screenshot_np, debug_template, best_result['location'], 
            best_result['confidence'], debug_filename
        )
        print(f"🖼 {control_name} debug saved -> {debug_path}")

        if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
            print(f"❌ {control_name} template not found. Confidence: {best_result['confidence']:.3f}")
            return None, best_result['confidence']

        # Tính toán vị trí click
        scaled_w, scaled_h = best_result['template_size']
        click_x = x + best_result['location'][0] + scaled_w // 2
        click_y = y + best_result['location'][1] + scaled_h // 2

        print(f"✅ {control_name} template found with confidence: {best_result['confidence']:.3f}")
        print(f"🎯 {control_name} click position: ({click_x}, {click_y}) [Scale: {best_result['scale']:.2f}]")

        return {'click_pos': (click_x, click_y), 'template_match': best_result}, best_result['confidence']
    
    # ==================== COMP METHODS ====================
    
    def set_comp_value(self, value):
        """Đặt giá trị COMP."""
        value = max(self.comp_min, min(self.comp_max, int(value)))
        
        print(f"🎛️ XVox COMP - Setting value to: {value}")
        
        # Store original cursor position
        original_pos = pyautogui.position()
        
        try:
            # 1. Find và focus Cubase process
            proc = self._find_cubase_process()
            if not proc:
                return False
                
            # 2. Focus Cubase window
            if not self._focus_cubase_window(proc):
                return False
            
            # 3. Find XVox plugin window
            plugin_win = self._find_xvox_window()
            if not plugin_win:
                return False
            
            # 4. Focus plugin window
            plugin_win.activate()
            time.sleep(0.1)  # Giảm từ 0.3 xuống 0.1
            
            # 5. Find COMP template match
            match_result = self._find_template_match(plugin_win, self.comp_template_path, "COMP")
            if not match_result or match_result[0] is None:
                return False
            
            result_data, confidence = match_result
            click_x, click_y = result_data['click_pos']
            
            # 6. Perform COMP action
            print(f"👆 Clicking COMP center: ({click_x}, {click_y})")
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            
            print("⏰ Waiting 0.2s...")  # Giảm từ 0.5s xuống 0.2s
            time.sleep(0.2)
            
            # Click above template for input field
            estimated_template_height = 100
            template_top_y = click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            print(f"👆 Double clicking above template: ({click_x}, {top_click_y})")
            pyautogui.doubleClick(click_x, top_click_y)
            time.sleep(0.1)  # Giảm từ 0.2 xuống 0.1
            
            print(f"⌨️ Typing COMP value: {value}")
            pyautogui.typewrite(str(value))
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            
            print("↩️ Pressing Enter")
            pyautogui.press('enter')
            time.sleep(0.1)  # Giảm từ 0.2 xuống 0.1
            
            print(f"✅ COMP set to {value} successfully")
            self.current_comp = value
            return True
            
        except Exception as e:
            print(f"❌ Error setting COMP value: {e}")
            return False
        finally:
            # Restore cursor position
            pyautogui.moveTo(original_pos[0], original_pos[1])
    
    # ==================== REVERB METHODS ====================
    
    def set_reverb_value(self, value):
        """Đặt giá trị Reverb."""
        value = max(self.reverb_min, min(self.reverb_max, int(value)))
        
        print(f"🌊 XVox Reverb - Setting value to: {value}")
        
        # Store original cursor position
        original_pos = pyautogui.position()
        
        try:
            # 1-4. Same setup as COMP
            proc = self._find_cubase_process()
            if not proc:
                return False
                
            if not self._focus_cubase_window(proc):
                return False
            
            plugin_win = self._find_xvox_window()
            if not plugin_win:
                return False
            
            plugin_win.activate()
            time.sleep(0.1)  # Giảm từ 0.3 xuống 0.1
            
            # 5. Find Reverb template match
            match_result = self._find_template_match(plugin_win, self.reverb_template_path, "Reverb")
            if not match_result or match_result[0] is None:
                return False
            
            result_data, confidence = match_result
            click_x, click_y = result_data['click_pos']
            
            # 6. Perform Reverb action (similar to COMP)
            print(f"👆 Clicking Reverb center: ({click_x}, {click_y})")
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            
            print("⏰ Waiting 0.2s...")  # Giảm từ 0.5s xuống 0.2s
            time.sleep(0.2)
            
            estimated_template_height = 100
            template_top_y = click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            print(f"👆 Double clicking above template: ({click_x}, {top_click_y})")
            pyautogui.doubleClick(click_x, top_click_y)
            time.sleep(0.1)  # Giảm từ 0.2 xuống 0.1
            
            print(f"⌨️ Typing Reverb value: {value}")
            pyautogui.typewrite(str(value))
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            
            print("↩️ Pressing Enter")
            pyautogui.press('enter')
            time.sleep(0.1)  # Giảm từ 0.2 xuống 0.1
            
            print(f"✅ Reverb set to {value} successfully")
            self.current_reverb = value
            return True
            
        except Exception as e:
            print(f"❌ Error setting Reverb value: {e}")
            return False
        finally:
            # Restore cursor position
            pyautogui.moveTo(original_pos[0], original_pos[1])
    
    # ==================== BASS/TREBLE METHODS ====================
    
    def set_bass_value(self, value):
        """Đặt giá trị Bass (LOW)."""
        value = max(self.bass_min, min(self.bass_max, int(value)))
        
        print(f"🔉 XVox Bass (LOW) - Setting value to: {value}")
        
        # Store original cursor position
        original_pos = pyautogui.position()
        
        try:
            # 1-4. Same setup
            proc = self._find_cubase_process()
            if not proc:
                return False
                
            if not self._focus_cubase_window(proc):
                return False
            
            plugin_win = self._find_xvox_window()
            if not plugin_win:
                return False
            
            plugin_win.activate()
            time.sleep(0.1)  # Giảm từ 0.3 xuống 0.1
            
            # 4. Find tone mic template và OCR để tìm LOW text (like original)
            result = self._find_tone_mic_template(plugin_win)
            if not result or not result.get('low_pos'):
                print("❌ Could not find LOW text position")
                return False
            
            low_pos = result['low_pos']
            print(f"✅ Found LOW text at: {low_pos}")
            
            # 5. Click vào LOW text
            pyautogui.click(low_pos[0], low_pos[1])
            time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
            print(f"🖱 Clicked on LOW text at {low_pos}")
            
            # 6. Click ở vị trí chiều dọc 10% từ trên xuống (convert to absolute coordinates)
            template_match = result['template_match']
            template_top = template_match['location'][1]  # Relative Y in plugin window
            template_height = template_match['template_size'][1]
            
            # Convert to absolute screen coordinates
            click_y = plugin_win.top + template_top + (template_height * 0.10)  # <<< THAY ĐỔI Ở ĐÂY
            click_x = low_pos[0]
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
            print(f"🖱 Clicked at 10% position: ({click_x}, {click_y})") # <<< THAY ĐỔI Ở ĐÂY
            
            # 7. Select text and input value
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            print("🖱 Triple-clicked to select text")
            
            pyautogui.typewrite(str(value))
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            print(f"⌨️ Typed value: {value}")
            
            pyautogui.press('enter')
            time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
            print("⌨️ Pressed Enter to confirm")
            
            print(f"✅ Successfully set Bass (LOW) to {value}")
            self.current_bass = value
            return True
            
        except Exception as e:
            print(f"❌ Error setting Bass value: {e}")
            return False
        finally:
            # Restore cursor position
            pyautogui.moveTo(original_pos[0], original_pos[1])
    
    def set_treble_value(self, value):
        """Đặt giá trị Treble (HIGH)."""
        value = max(self.treble_min, min(self.treble_max, int(value)))
        
        print(f"🔊 XVox Treble (HIGH) - Setting value to: {value}")
        
        # Store original cursor position
        original_pos = pyautogui.position()
        
        try:
            # 1-4. Same setup
            proc = self._find_cubase_process()
            if not proc:
                return False
                
            if not self._focus_cubase_window(proc):
                return False
            
            plugin_win = self._find_xvox_window()
            if not plugin_win:
                return False
            
            plugin_win.activate()
            time.sleep(0.1)  # Giảm từ 0.3 xuống 0.1
            
            # 4. Find tone mic template và OCR để tìm HIGH text (like original)
            result = self._find_tone_mic_template(plugin_win)
            if not result or not result.get('high_pos'):
                print("❌ Could not find HIGH text position")
                return False
            
            high_pos = result['high_pos']
            print(f"✅ Found HIGH text at: {high_pos}")
            
            # 5. Click vào HIGH text
            pyautogui.click(high_pos[0], high_pos[1])
            time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
            print(f"🖱 Clicked on HIGH text at {high_pos}")
            
            # 6. Click ở vị trí chiều dọc 10% từ trên xuống (convert to absolute coordinates)
            template_match = result['template_match']
            template_top = template_match['location'][1]  # Relative Y in plugin window
            template_height = template_match['template_size'][1]
            
            # Convert to absolute screen coordinates
            click_y = plugin_win.top + template_top + (template_height * 0.10)  # <<< THAY ĐỔI Ở ĐÂY
            click_x = high_pos[0]
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
            print(f"🖱 Clicked at 10% position: ({click_x}, {click_y})") # <<< THAY ĐỔI Ở ĐÂY
            
            # 7. Select text and input value
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            print("🖱 Triple-clicked to select text")
            
            pyautogui.typewrite(str(value))
            time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
            print(f"⌨️ Typed value: {value}")
            
            pyautogui.press('enter')
            time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
            print("⌨️ Pressed Enter to confirm")
            
            print(f"✅ Successfully set Treble (HIGH) to {value}")
            self.current_treble = value
            return True
            
        except Exception as e:
            print(f"❌ Error setting Treble value: {e}")
            return False
        finally:
            # Restore cursor position
            pyautogui.moveTo(original_pos[0], original_pos[1])
    
    def _find_tone_mic_template(self, xvox_window):
        """
        Tìm vị trí LOW và HIGH trong XVox plugin bằng cách tính toán vị trí dựa trên template.
        Phương pháp này nhanh, ổn định và không phụ thuộc vào OCR.
        """
        try:
            # Lấy thông tin cửa sổ XVox
            x, y, w, h = xvox_window.left, xvox_window.top, xvox_window.width, xvox_window.height
            print(f"📐 XVox window: {x}, {y}, {w}x{h}")
            
            # Screenshot XVox window
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Load template
            template = cv2.imread(self.tone_mic_template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"❌ Cannot load tone mic template: {self.tone_mic_template_path}")
                return None
                
            # Adaptive template matching
            best_result = TemplateHelper.adaptive_template_match(screenshot_gray, template)
            
            if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ Tone Mic template confidence too low: {best_result['confidence']:.3f}")
                return None
            
            # Template match coordinates
            match_x, match_y = best_result['location']
            scaled_w, scaled_h = best_result['template_size']
            
            print(f"✅ Tone Mic template found at: ({match_x}, {match_y}) with size {scaled_w}x{scaled_h}")

            # --- TÍNH TOÁN VỊ TRÍ LOW VÀ HIGH ---
            print("🎯 Calculating LOW and HIGH positions...")
            
            # Tính toán vị trí LOW
            low_x = x + match_x + int(scaled_w * self.LOW_REL_X_POS)
            low_y = y + match_y + int(scaled_h * self.LOW_REL_Y_POS)
            low_pos = (low_x, low_y)
            print(f"🔉 LOW position calculated: ({low_x}, {low_y})")

            # Tính toán vị trí HIGH
            high_x = x + match_x + int(scaled_w * self.HIGH_REL_X_POS)
            high_y = y + match_y + int(scaled_h * self.HIGH_REL_Y_POS)
            high_pos = (high_x, high_y)
            print(f"🔊 HIGH position calculated: ({high_x}, {high_y})")
            
            # Save debug image 
            debug_filename = "tone_mic_ocr_debug.png"
            debug_path = ImageHelper.save_template_debug_image(
                screenshot_np, template, (match_x, match_y), 
                best_result['confidence'], debug_filename
            )
            print(f"🖼 Tone mic template debug saved -> {debug_path}")
            
            return {
                'low_pos': low_pos,
                'high_pos': high_pos,
                'template_match': best_result
            }
            
        except Exception as e:
            print(f"❌ Error in tone mic template detection: {e}")
            return None
            
    def _perform_ocr_workflow(self, plugin_win, template_match, target_text, value, control_name):
        """Thực hiện OCR workflow cho Bass/Treble."""
        x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        
        # Convert to PIL for OCR (like the original code)
        from PIL import Image
        screenshot_pil = Image.fromarray(screenshot_gray, mode='L')
        
        # OCR to find LOW/HIGH text
        print("📖 OCR on grayscale region...")
        ocr_data = OCRHelper.extract_text_data(screenshot_pil)
        words = OCRHelper.get_text_words(ocr_data)
        print(f"📜 OCR text in tone mic region: {words}")
        
        target_pos = None
        
        # Look for exact target text first (like original code)
        for i, text in enumerate(ocr_data["text"]):
            if text and text.strip():
                text_clean = text.strip().upper()
                
                if target_text in text_clean:
                    # Calculate absolute position (like original)
                    target_x = x + ocr_data["left"][i] + ocr_data["width"][i] // 2
                    target_y = y + ocr_data["top"][i] + ocr_data["height"][i] // 2
                    target_pos = (target_x, target_y)
                    print(f"   ✅ Found {target_text} text at position {i}: {target_pos}")
                    break
        
        # Fallback: use position-based detection (like original)
        if not target_pos and len(ocr_data["text"]) >= 3:
            if target_text == "LOW":
                i = 0  # First element
            else:  # HIGH
                i = 2  # Third element
            
            if i < len(ocr_data["text"]):
                target_x = x + ocr_data["left"][i] + ocr_data["width"][i] // 2
                target_y = y + ocr_data["top"][i] + ocr_data["height"][i] // 2
                target_pos = (target_x, target_y)
                print(f"   🔄 Using fallback position for {target_text}: {target_pos}")
        
        if not target_pos:
            print(f"❌ Could not find {target_text} position")
            return False
        
        # Calculate click position (10% down from template top)
        template_top = template_match['location'][1]
        template_height = template_match['template_size'][1]
        
        click_y = template_top + (template_height * 0.10)  # <<< THAY ĐỔI Ở ĐÂY
        click_x = target_pos[0]
        
        pyautogui.click(click_x, click_y)
        time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
        print(f"🖱 Clicked at 10% position: ({click_x}, {click_y})") # <<< THAY ĐỔI Ở ĐÂY
        
        # Select text and input value
        pyautogui.tripleClick(click_x, click_y)
        time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
        print("🖱 Triple-clicked to select text")
        
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
        print("⌨️ Also tried Ctrl+A")
        
        pyautogui.typewrite(str(value))
        time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
        print(f"⌨️ Typed value: {value}")
        
        pyautogui.press('enter')
        time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
        print("⌨️ Pressed Enter to confirm")
        
        print(f"✅ Successfully set {control_name} ({target_text}) to {value}")
        
        if target_text == "LOW":
            self.current_bass = value
        else:
            self.current_treble = value
            
        return True
    
    def execute(self):
        """Execute XVox detection."""
        return self._find_xvox_window() is not None

    # Thêm vào cuối class XVoxDetector trong file xvox_detector.py

    # ==================== ULTRA OPTIMIZED BATCH RESET ====================
    
    def batch_reset_all_xvox_parameters(self, plugin_win, comp_value, reverb_value, bass_value, treble_value):
        """
        ULTRA OPTIMIZED: Reset tất cả XVox parameters với chỉ 1 lần OCR/CV cho tất cả.
        Thực hiện template matching một lần cho tất cả controls, sau đó set value tuần tự.
        """
        try:
            print("⚡ ULTRA OPTIMIZED: Batch reset all XVox parameters...")
            
            # Validate values
            comp_value = max(self.comp_min, min(self.comp_max, int(comp_value)))
            reverb_value = max(self.reverb_min, min(self.reverb_max, int(reverb_value)))
            bass_value = max(self.bass_min, min(self.bass_max, int(bass_value)))
            treble_value = max(self.treble_min, min(self.treble_max, int(treble_value)))
            
            # --- BƯỚC 1: Template matching MỘT LẦN cho tất cả controls ---
            print("📸 Taking ONE screenshot and finding ALL templates...")
            
            # Screenshot plugin window một lần
            x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Find COMP template
            comp_template = cv2.imread(self.comp_template_path, cv2.IMREAD_GRAYSCALE)
            comp_result = TemplateHelper.adaptive_template_match(screenshot_gray, comp_template)
            if comp_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ COMP template not found")
                return False
            comp_click_x = x + comp_result['location'][0] + comp_result['template_size'][0] // 2
            comp_click_y = y + comp_result['location'][1] + comp_result['template_size'][1] // 2
            print(f"✅ COMP found at ({comp_click_x}, {comp_click_y})")
            
            # Find Reverb template
            reverb_template = cv2.imread(self.reverb_template_path, cv2.IMREAD_GRAYSCALE)
            reverb_result = TemplateHelper.adaptive_template_match(screenshot_gray, reverb_template)
            if reverb_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ Reverb template not found")
                return False
            reverb_click_x = x + reverb_result['location'][0] + reverb_result['template_size'][0] // 2
            reverb_click_y = y + reverb_result['location'][1] + reverb_result['template_size'][1] // 2
            print(f"✅ Reverb found at ({reverb_click_x}, {reverb_click_y})")
            
            # Find Tone Mic template (for Bass & Treble)
            tone_template = cv2.imread(self.tone_mic_template_path, cv2.IMREAD_GRAYSCALE)
            tone_result = TemplateHelper.adaptive_template_match(screenshot_gray, tone_template)
            if tone_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                print(f"❌ Tone Mic template not found")
                return False
            
            # Calculate LOW and HIGH positions
            match_x, match_y = tone_result['location']
            scaled_w, scaled_h = tone_result['template_size']
            low_x = x + match_x + int(scaled_w * self.LOW_REL_X_POS)
            low_y = y + match_y + int(scaled_h * self.LOW_REL_Y_POS)
            high_x = x + match_x + int(scaled_w * self.HIGH_REL_X_POS)
            high_y = y + match_y + int(scaled_h * self.HIGH_REL_Y_POS)
            
            # Calculate click Y position (10% from top)
            template_top = match_y
            template_height = scaled_h
            bass_click_y = y + template_top + int(template_height * 0.10)
            treble_click_y = bass_click_y  # Same Y position
            
            print(f"✅ Bass (LOW) found at ({low_x}, {low_y}), click Y: {bass_click_y}")
            print(f"✅ Treble (HIGH) found at ({high_x}, {high_y}), click Y: {treble_click_y}")
            
            # --- BƯỚC 2: Set values tuần tự (KHÔNG cần OCR/CV lại) ---
            
            # Set COMP
            print(f"🎛️ Setting COMP to {comp_value}...")
            pyautogui.click(comp_click_x, comp_click_y)
            time.sleep(0.05)
            time.sleep(0.2)
            estimated_template_height = 100
            template_top_y = comp_click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            pyautogui.doubleClick(comp_click_x, top_click_y)
            time.sleep(0.1)
            pyautogui.typewrite(str(comp_value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.1)
            self.current_comp = comp_value
            print(f"✅ COMP set to {comp_value}")
            
            # Set Reverb
            print(f"🌊 Setting Reverb to {reverb_value}...")
            pyautogui.click(reverb_click_x, reverb_click_y)
            time.sleep(0.05)
            time.sleep(0.2)
            template_top_y = reverb_click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            pyautogui.doubleClick(reverb_click_x, top_click_y)
            time.sleep(0.1)
            pyautogui.typewrite(str(reverb_value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.1)
            self.current_reverb = reverb_value
            print(f"✅ Reverb set to {reverb_value}")
            
            # Set Bass
            print(f"🔉 Setting Bass to {bass_value}...")
            pyautogui.click(low_x, low_y)
            time.sleep(0.05)
            pyautogui.click(low_x, bass_click_y)
            time.sleep(0.05)
            pyautogui.tripleClick(low_x, bass_click_y)
            time.sleep(0.05)
            pyautogui.typewrite(str(bass_value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.05)
            self.current_bass = bass_value
            print(f"✅ Bass set to {bass_value}")
            
            # Set Treble
            print(f"🔊 Setting Treble to {treble_value}...")
            pyautogui.click(high_x, high_y)
            time.sleep(0.05)
            pyautogui.click(high_x, treble_click_y)
            time.sleep(0.05)
            pyautogui.tripleClick(high_x, treble_click_y)
            time.sleep(0.05)
            pyautogui.typewrite(str(treble_value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.05)
            self.current_treble = treble_value
            print(f"✅ Treble set to {treble_value}")
            
            print("✅ ULTRA OPTIMIZED: All XVox parameters set successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error in batch reset all XVox parameters: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ==================== INTERNAL METHODS FOR BATCH RESET ====================
    # Các hàm mới nhận plugin_win từ bên ngoài (tối ưu hơn - không tìm window lại)
    
    def _batch_set_comp_value(self, plugin_win, value):
        """Batch method to set COMP value with pre-found plugin window."""
        value = max(self.comp_min, min(self.comp_max, int(value)))
        try:
            match_result = self._find_template_match(plugin_win, self.comp_template_path, "COMP")
            if not match_result or match_result[0] is None:
                return False
            
            result_data, _ = match_result
            click_x, click_y = result_data['click_pos']
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            time.sleep(0.2)
            
            estimated_template_height = 100
            template_top_y = click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            pyautogui.doubleClick(click_x, top_click_y)
            time.sleep(0.1)
            
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.1)
            
            self.current_comp = value
            return True
        except Exception as e:
            print(f"❌ Error setting COMP value: {e}")
            return False

    def _batch_set_reverb_value(self, plugin_win, value):
        """Batch method to set Reverb value with pre-found plugin window."""
        value = max(self.reverb_min, min(self.reverb_max, int(value)))
        try:
            match_result = self._find_template_match(plugin_win, self.reverb_template_path, "Reverb")
            if not match_result or match_result[0] is None:
                return False
            
            result_data, _ = match_result
            click_x, click_y = result_data['click_pos']
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            time.sleep(0.2)
            
            estimated_template_height = 100
            template_top_y = click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            pyautogui.doubleClick(click_x, top_click_y)
            time.sleep(0.1)
            
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.1)
            
            self.current_reverb = value
            return True
        except Exception as e:
            print(f"❌ Error setting Reverb value: {e}")
            return False

    def _batch_set_bass_value(self, plugin_win, value):
        """Batch method to set Bass value with pre-found plugin window."""
        value = max(self.bass_min, min(self.bass_max, int(value)))
        try:
            result = self._find_tone_mic_template(plugin_win)
            if not result or not result.get('low_pos'):
                return False
            
            low_pos = result['low_pos']
            pyautogui.click(low_pos[0], low_pos[1])
            time.sleep(0.05)
            
            template_match = result['template_match']
            template_top = template_match['location'][1]
            template_height = template_match['template_size'][1]
            
            click_y = plugin_win.top + template_top + (template_height * 0.10)
            click_x = low_pos[0]
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.05)
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.05)
            
            self.current_bass = value
            return True
        except Exception as e:
            print(f"❌ Error setting Bass value: {e}")
            return False

    def _batch_set_treble_value(self, plugin_win, value):
        """Batch method to set Treble value with pre-found plugin window."""
        value = max(self.treble_min, min(self.treble_max, int(value)))
        try:
            result = self._find_tone_mic_template(plugin_win)
            if not result or not result.get('high_pos'):
                return False
            
            high_pos = result['high_pos']
            pyautogui.click(high_pos[0], high_pos[1])
            time.sleep(0.05)
            
            template_match = result['template_match']
            template_top = template_match['location'][1]
            template_height = template_match['template_size'][1]
            
            click_y = plugin_win.top + template_top + (template_height * 0.10)
            click_x = high_pos[0]
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.05)
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.05)
            
            self.current_treble = value
            return True
        except Exception as e:
            print(f"❌ Error setting Treble value: {e}")
            return False

    # ==================== OLD INTERNAL METHODS (DEPRECATED) ====================
    # Các hàm này không trả về vị trí chuột, dùng cho batch reset
    # DEPRECATED: Sử dụng _batch_set_* thay thế

    def _set_comp_value_no_restore(self, value):
        """Internal method to set COMP value without restoring cursor."""
        value = max(self.comp_min, min(self.comp_max, int(value)))
        try:
            proc = self._find_cubase_process()
            if not proc: return False
            if not self._focus_cubase_window(proc): return False
            plugin_win = self._find_xvox_window()
            if not plugin_win: return False
            plugin_win.activate()
            time.sleep(0.1)
            
            match_result = self._find_template_match(plugin_win, self.comp_template_path, "COMP")
            if not match_result or match_result[0] is None: return False
            
            result_data, _ = match_result
            click_x, click_y = result_data['click_pos']
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            time.sleep(0.2)
            
            estimated_template_height = 100
            template_top_y = click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            pyautogui.doubleClick(click_x, top_click_y)
            time.sleep(0.1)
            
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.1)
            
            self.current_comp = value
            return True
        except Exception as e:
            print(f"❌ Error setting COMP value: {e}")
            return False

    def _set_reverb_value_no_restore(self, value):
        """Internal method to set Reverb value without restoring cursor."""
        value = max(self.reverb_min, min(self.reverb_max, int(value)))
        try:
            proc = self._find_cubase_process()
            if not proc: return False
            if not self._focus_cubase_window(proc): return False
            plugin_win = self._find_xvox_window()
            if not plugin_win: return False
            plugin_win.activate()
            time.sleep(0.1)
            
            match_result = self._find_template_match(plugin_win, self.reverb_template_path, "Reverb")
            if not match_result or match_result[0] is None: return False
            
            result_data, _ = match_result
            click_x, click_y = result_data['click_pos']
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            time.sleep(0.2)
            
            estimated_template_height = 100
            template_top_y = click_y - (estimated_template_height // 2)
            top_click_y = template_top_y - 15
            pyautogui.doubleClick(click_x, top_click_y)
            time.sleep(0.1)
            
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.1)
            
            self.current_reverb = value
            return True
        except Exception as e:
            print(f"❌ Error setting Reverb value: {e}")
            return False

    def _set_bass_value_no_restore(self, value):
        """Internal method to set Bass value without restoring cursor."""
        value = max(self.bass_min, min(self.bass_max, int(value)))
        try:
            proc = self._find_cubase_process()
            if not proc: return False
            if not self._focus_cubase_window(proc): return False
            plugin_win = self._find_xvox_window()
            if not plugin_win: return False
            plugin_win.activate()
            time.sleep(0.1)
            
            result = self._find_tone_mic_template(plugin_win)
            if not result or not result.get('low_pos'): return False
            
            low_pos = result['low_pos']
            pyautogui.click(low_pos[0], low_pos[1])
            time.sleep(0.05)
            
            template_match = result['template_match']
            template_top = template_match['location'][1]
            template_height = template_match['template_size'][1]
            
            click_y = plugin_win.top + template_top + (template_height * 0.10)
            click_x = low_pos[0]
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.05)
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.05)
            
            self.current_bass = value
            return True
        except Exception as e:
            print(f"❌ Error setting Bass value: {e}")
            return False

    def _set_treble_value_no_restore(self, value):
        """Internal method to set Treble value without restoring cursor."""
        value = max(self.treble_min, min(self.treble_max, int(value)))
        try:
            proc = self._find_cubase_process()
            if not proc: return False
            if not self._focus_cubase_window(proc): return False
            plugin_win = self._find_xvox_window()
            if not plugin_win: return False
            plugin_win.activate()
            time.sleep(0.1)
            
            result = self._find_tone_mic_template(plugin_win)
            if not result or not result.get('high_pos'): return False
            
            high_pos = result['high_pos']
            pyautogui.click(high_pos[0], high_pos[1])
            time.sleep(0.05)
            
            template_match = result['template_match']
            template_top = template_match['location'][1]
            template_height = template_match['template_size'][1]
            
            click_y = plugin_win.top + template_top + (template_height * 0.10)
            click_x = high_pos[0]
            
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            pyautogui.tripleClick(click_x, click_y)
            time.sleep(0.05)
            pyautogui.typewrite(str(value))
            time.sleep(0.05)
            pyautogui.press('enter')
            time.sleep(0.05)
            
            self.current_treble = value
            return True
        except Exception as e:
            print(f"❌ Error setting Treble value: {e}")
            return False
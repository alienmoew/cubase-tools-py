"""
Footer Component - Version, Theme, Debug buttons và Copyright.
"""
import customtkinter as CTK
import config
from gui.components.base_component import BaseComponent


class Footer(BaseComponent):
    """Component cho footer với controls và thông tin."""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        
        # UI element references
        self.theme_button = None
        self.debug_button = None
        self.reset_button = None
        self.copyright_label = None
        
    def create(self):
        """Tạo footer."""
        # Footer container - minimal height
        self.container = CTK.CTkFrame(self.parent, fg_color="#1F1F1F", corner_radius=0, height=25)
        self.container.pack_propagate(False)
        
        footer_frame = CTK.CTkFrame(self.container, fg_color="transparent")
        footer_frame.pack(fill="both", expand=True, padx=8, pady=3)     
        
        # Debug button
        self.debug_button = CTK.CTkButton(
            footer_frame,
            text="D",
            command=self._show_debug_window,
            width=25,
            height=18,
            font=("Arial", 10),
            corner_radius=3,
            fg_color="#000000",
            hover_color="#F57C00"
        )
        self.debug_button.pack(side="left", padx=(2, 0))
        
        # Reset button
        self.reset_button = CTK.CTkButton(
            footer_frame,
            text="Reset",
            command=self._reset_all_parameters,
            width=25,
            height=18,
            font=("Arial", 12),
            corner_radius=3,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.reset_button.pack(side="left", padx=(2, 0))
        
        # Copyright (right side)
        self.copyright_label = CTK.CTkLabel(
            footer_frame,
            text=config.COPYRIGHT,
            font=("Arial", 12, "bold"),
            text_color="#FF6B6B",
            cursor="hand2"
        )
        self.copyright_label.pack(side="right")
        
        # Make copyright clickable (copy phone to clipboard)
        self.copyright_label.bind("<Button-1>", self._copy_phone)
        
        return self.container
    
    # ==================== EVENT HANDLERS ====================
    
    def _toggle_theme(self):
        """Toggle theme."""
        self.main_window._toggle_theme()
    
    def _show_debug_window(self):
        """Hiển thị debug window."""
        self.main_window._show_debug_window()
    
    def _reset_all_parameters(self):
        """Reset tất cả parameters về giá trị mặc định."""
        # Pause auto-detect during operation
        self.main_window.pause_auto_detect_for_manual_action()
        
        try:
            print("🔄 Resetting all parameters to defaults...")
            
            # Sử dụng cùng một phương thức reset như trong MainWindow
            self._batch_reset_autotune_parameters()
            
            # Reset SoundShifter (Tone nhạc) về giá trị mặc định
            self._reset_soundshifter()
            
            # Sử dụng batch reset cho vocal parameters
            self._batch_reset_vocal_parameters()
            
            print("✅ All parameters reset completed")
        except Exception as e:
            print(f"❌ Error resetting parameters: {e}")
        finally:
            # Resume auto-detect
            self.main_window.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self.main_window._minimize_plugins_after_action()
    
    
    def _reset_soundshifter(self):
        """Reset SoundShifter (Tone nhạc) về giá trị mặc định từ file config."""
        try:
            # Lấy giá trị mặc định từ file config
            default_values = self.main_window.default_values
            soundshifter_default = default_values.get('soundshifter_pitch_default', 0)
            
            print(f"🔄 Resetting SoundShifter to {soundshifter_default}...")
            success = self.main_window.soundshifter_detector.reset_pitch()
            
            if success:
                # Update display
                self.main_window._update_soundshifter_display()
                print(f"✅ SoundShifter reset to {soundshifter_default}")
            else:
                print(f"❌ Failed to reset SoundShifter to {soundshifter_default}")
        except Exception as e:
            print(f"❌ Error resetting SoundShifter: {e}")
    
    def _batch_reset_vocal_parameters(self):
        """Ultra fast batch reset tất cả vocal parameters (Volume Mic, Reverb, Bass, Treble)."""
        try:
            print("⚡ Ultra fast batch reset vocal parameters starting...")
            
            # Lấy giá trị mặc định từ file config
            default_values = self.main_window.default_values
            
            # Tìm cửa sổ XVox một lần duy nhất
            from utils.window_manager import WindowManager
            import pygetwindow as gw
            
            # Try different possible window titles for XVox
            possible_titles = ["Xvox", "XVOX", "xvox", "X-Vox", "X_Vox", "XVox", "X Vox"]
            xvox_win = None
            
            for title in possible_titles:
                xvox_win = WindowManager.find_window(title)
                if xvox_win:
                    print(f"✅ Found XVox window: {title}")
                    break
            
            if not xvox_win:
                print("❌ XVox plugin window not found")
                return False
            
            # Focus XVox window
            xvox_win.activate()
            import time
            time.sleep(0.1)  # Giảm từ 0.3 xuống 0.1
            
            # Lấy thông tin cửa sổ XVox
            x, y, w, h = xvox_win.left, xvox_win.top, xvox_win.width, xvox_win.height
            print(f"📐 XVox window: {x}, {y}, {w}x{h}")
            
            # Screenshot toàn bộ cửa sổ XVox một lần
            import pyautogui
            import cv2
            import numpy as np
            from PIL import Image
            
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Chuẩn bị các giá trị mặc định
            xvox_volume_default = default_values.get('xvox_volume_default', 40)
            reverb_default = default_values.get('reverb_default', 36)
            bass_default = default_values.get('bass_default', -10)
            treble_default = default_values.get('treble_default', 20)
            
            # Reset Volume Mic (COMP)
            print(f"🔄 Resetting Volume Mic to {xvox_volume_default}...")
            try:
                # Load template
                comp_template = cv2.imread(config.TEMPLATE_PATHS['comp_template'], cv2.IMREAD_GRAYSCALE)
                if comp_template is None:
                    print(f"❌ Cannot load COMP template")
                    return False
                
                # Template matching
                from utils.helpers import TemplateHelper
                best_result = TemplateHelper.adaptive_template_match(screenshot_gray, comp_template)
                
                if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                    print(f"❌ COMP template confidence too low: {best_result['confidence']:.3f}")
                    return False
                
                # Tính toán vị trí click
                scaled_w, scaled_h = best_result['template_size']
                click_x = x + best_result['location'][0] + scaled_w // 2
                click_y = y + best_result['location'][1] + scaled_h // 2
                
                # Thực hiện click và nhập giá trị - GIẢM DELAY
                pyautogui.click(click_x, click_y)
                time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                time.sleep(0.1)  # Giảm từ 0.5 xuống 0.1
                
                estimated_template_height = 100
                template_top_y = click_y - (estimated_template_height // 2)
                top_click_y = template_top_y - 15
                pyautogui.doubleClick(click_x, top_click_y)
                time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                
                pyautogui.typewrite(str(xvox_volume_default))
                time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                pyautogui.press('enter')
                time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                
                print(f"✅ Volume Mic reset to {xvox_volume_default}")
                
                # Update UI
                if self.main_window.vocal_section and self.main_window.vocal_section.volume_mic_slider:
                    self.main_window.vocal_section.volume_mic_slider.set(xvox_volume_default)
                    self.main_window.vocal_section.volume_mic_value_label.configure(text=str(xvox_volume_default))
            except Exception as e:
                print(f"❌ Failed to reset Volume Mic: {e}")
            
            # Reset Reverb
            print(f"🔄 Resetting Reverb to {reverb_default}...")
            try:
                # Load template
                reverb_template = cv2.imread(config.TEMPLATE_PATHS['reverb_template'], cv2.IMREAD_GRAYSCALE)
                if reverb_template is None:
                    print(f"❌ Cannot load Reverb template")
                    return False
                
                # Template matching
                best_result = TemplateHelper.adaptive_template_match(screenshot_gray, reverb_template)
                
                if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                    print(f"❌ Reverb template confidence too low: {best_result['confidence']:.3f}")
                    return False
                
                # Tính toán vị trí click
                scaled_w, scaled_h = best_result['template_size']
                click_x = x + best_result['location'][0] + scaled_w // 2
                click_y = y + best_result['location'][1] + scaled_h // 2
                
                # Thực hiện click và nhập giá trị - GIẢM DELAY
                pyautogui.click(click_x, click_y)
                time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                time.sleep(0.1)  # Giảm từ 0.5 xuống 0.1
                
                estimated_template_height = 100
                template_top_y = click_y - (estimated_template_height // 2)
                top_click_y = template_top_y - 15
                pyautogui.doubleClick(click_x, top_click_y)
                time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                
                pyautogui.typewrite(str(reverb_default))
                time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                pyautogui.press('enter')
                time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                
                print(f"✅ Reverb reset to {reverb_default}")
                
                # Update UI
                if self.main_window.vocal_section and self.main_window.vocal_section.reverb_mic_slider:
                    self.main_window.vocal_section.reverb_mic_slider.set(reverb_default)
                    self.main_window.vocal_section.reverb_mic_value_label.configure(text=str(reverb_default))
            except Exception as e:
                print(f"❌ Failed to reset Reverb: {e}")
            
            # Reset Bass và Treble bằng OCR một lần
            print(f"🔄 Resetting Bass to {bass_default} and Treble to {treble_default}...")
            try:
                # Load template
                tone_mic_template = cv2.imread(config.TEMPLATE_PATHS['tone_mic_template'], cv2.IMREAD_GRAYSCALE)
                if tone_mic_template is None:
                    print(f"❌ Cannot load tone mic template")
                    return False
                
                # Template matching
                best_result = TemplateHelper.adaptive_template_match(screenshot_gray, tone_mic_template)
                
                if best_result['confidence'] < config.TEMPLATE_MATCH_THRESHOLD:
                    print(f"❌ Tone mic template confidence too low: {best_result['confidence']:.3f}")
                    return False
                
                # Template match coordinates
                match_x, match_y = best_result['location']
                scaled_w, scaled_h = best_result['template_size']
                
                # Define OCR region
                ocr_x, ocr_y = match_x, match_y
                ocr_w, ocr_h = scaled_w, scaled_h
                
                # Direct capture OCR region
                absolute_ocr_x = x + ocr_x
                absolute_ocr_y = y + ocr_y
                ocr_region_pil = pyautogui.screenshot(region=(absolute_ocr_x, absolute_ocr_y, ocr_w, ocr_h))
                
                # Convert OCR region to grayscale
                ocr_region_np = np.array(ocr_region_pil)
                ocr_region_gray = cv2.cvtColor(ocr_region_np, cv2.COLOR_RGB2GRAY)
                
                # Convert back to PIL for OCR
                ocr_region_gray_pil = Image.fromarray(ocr_region_gray, mode='L')
                
                # OCR
                from utils.helpers import OCRHelper
                ocr_data = OCRHelper.extract_text_data(ocr_region_gray_pil)
                words = OCRHelper.get_text_words(ocr_data)
                print(f"📜 OCR text in tone mic region: {words}")
                
                # Tìm vị trí LOW và HIGH
                low_pos = None
                high_pos = None
                low_index = -1
                
                # Tìm vị trí LOW
                for i, text in enumerate(ocr_data["text"]):
                    if text and text.strip():
                        text_clean = text.strip().upper()
                        
                        if "LOW" in text_clean:
                            # Tính vị trí absolute của LOW
                            low_x = x + ocr_x + ocr_data["left"][i] + ocr_data["width"][i] // 2
                            low_y = y + ocr_y + ocr_data["top"][i] + ocr_data["height"][i] // 2
                            low_pos = (low_x, low_y)
                            low_index = i
                            print(f"🔉 Found LOW at index {i}: ({low_x}, {low_y})")
                            break
                
                # Tìm vị trí HIGH
                # Thử tìm trực tiếp từ OCR
                for i, text in enumerate(ocr_data["text"]):
                    if text and text.strip():
                        text_clean = text.strip().upper()
                        
                        if "HIGH" in text_clean:
                            # Tính vị trí absolute của HIGH
                            high_x = x + ocr_x + ocr_data["left"][i] + ocr_data["width"][i] // 2
                            high_y = y + ocr_y + ocr_data["top"][i] + ocr_data["height"][i] // 2
                            high_pos = (high_x, high_y)
                            print(f"🔊 Found HIGH at index {i}: ({high_x}, {high_y})")
                            break
                
                # Nếu không tìm thấy HIGH, sử dụng vị trí cách LOW hai đơn vị
                if not high_pos and low_index >= 0:
                    high_index = low_index + 2
                    
                    # Kiểm tra xem index có hợp lệ không
                    if high_index < len(ocr_data["text"]):
                        high_text = ocr_data["text"][high_index]
                        if high_text and high_text.strip():
                            # Tính vị trí absolute của HIGH
                            high_x = x + ocr_x + ocr_data["left"][high_index] + ocr_data["width"][high_index] // 2
                            high_y = y + ocr_y + ocr_data["top"][high_index] + ocr_data["height"][high_index] // 2
                            high_pos = (high_x, high_y)
                            print(f"🔊 Found HIGH at index {high_index} (text: '{high_text}'): ({high_x}, {high_y})")
                
                # Reset Bass - GIẢM DELAY
                if low_pos:
                    # Click vào LOW text
                    pyautogui.click(low_pos[0], low_pos[1])
                    time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                    
                    # Click ở vị trí chiều dọc 35% từ trên xuống
                    template_top = match_y
                    template_height = scaled_h
                    
                    click_y = y + template_top + (template_height * 0.35)
                    click_x = low_pos[0]
                    
                    pyautogui.click(click_x, click_y)
                    time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                    
                    # Select text and input value
                    pyautogui.tripleClick(click_x, click_y)
                    time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                    
                    pyautogui.typewrite(str(bass_default))
                    time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                    pyautogui.press('enter')
                    time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                    
                    print(f"✅ Bass reset to {bass_default}")
                    
                    # Update UI
                    if self.main_window.vocal_section and self.main_window.vocal_section.bass_slider:
                        self.main_window.vocal_section.bass_slider.set(bass_default)
                        self.main_window.vocal_section.bass_value_label.configure(text=str(bass_default))
                
                # Reset Treble - GIẢM DELAY
                if high_pos:
                    # Click vào HIGH text
                    pyautogui.click(high_pos[0], high_pos[1])
                    time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                    
                    # Click ở vị trí chiều dọc 35% từ trên xuống
                    template_top = match_y
                    template_height = scaled_h
                    
                    click_y = y + template_top + (template_height * 0.35)
                    click_x = high_pos[0]
                    
                    pyautogui.click(click_x, click_y)
                    time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                    
                    # Select text and input value
                    pyautogui.tripleClick(click_x, click_y)
                    time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                    
                    pyautogui.typewrite(str(treble_default))
                    time.sleep(0.05)  # Giảm từ 0.1 xuống 0.05
                    pyautogui.press('enter')
                    time.sleep(0.05)  # Giảm từ 0.2 xuống 0.05
                    
                    print(f"✅ Treble reset to {treble_default}")
                    
                    # Update UI
                    if self.main_window.vocal_section and self.main_window.vocal_section.treble_slider:
                        self.main_window.vocal_section.treble_slider.set(treble_default)
                        self.main_window.vocal_section.treble_value_label.configure(text=str(treble_default))
                
                print("✅ Bass and Treble reset completed")
            except Exception as e:
                print(f"❌ Failed to reset Bass and Treble: {e}")
            
            print("✅ Ultra fast batch reset vocal parameters completed")
            return True
            
        except Exception as e:
            print(f"❌ Error in batch reset vocal parameters: {e}")
            return False
    
    def _copy_phone(self, event):
        """Copy phone number to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(config.CONTACT_INFO['phone'])
            # Temporary feedback
            original_text = self.copyright_label.cget("text")
            self.copyright_label.configure(text="Đã copy số!", text_color="#00aa00")
            self.main_window.root.after(2000, lambda: self.copyright_label.configure(
                text=original_text, text_color="#FF6B6B"))
            print(f"📞 Copied phone number to clipboard: {config.CONTACT_INFO['phone']}")
        except ImportError:
            print(f"📞 Phone: {config.CONTACT_INFO['phone']}")
            
    def _batch_reset_autotune_parameters(self):
        """Ultra fast batch reset tất cả parameters Auto-Tune."""
        # Prepare ultra fast batch parameters
        reset_configs = [
            ('Return Speed', self.main_window.autotune_controls_detector.return_speed_detector,
            'return_speed_default', 30),
            ('Flex Tune', self.main_window.autotune_controls_detector.flex_tune_detector,
            'flex_tune_default', 40),
            ('Transpose', self.main_window.transpose_detector, 'transpose_default', 0)
        ]

        # Build parameters list for ultra fast processor
        parameters_list = []

        for name, detector, default_key, default_fallback in reset_configs:
            default_value = self.main_window.default_values.get(
                default_key, default_fallback)
            parameters_list.append({
                'detector': detector,
                'value': default_value,
                'name': name
            })

        # Execute ultra fast batch
        try:
            print("⚡ Ultra fast batch reset starting...")

            from utils.ultra_fast_processor import UltraFastAutoTuneProcessor
            ultra_processor = UltraFastAutoTuneProcessor()
            success_count, total_count = ultra_processor.execute_ultra_fast_batch(
                parameters_list)
            
            # Update UI for transpose - SỬA LỖI
            if self.main_window.music_section and self.main_window.music_section.pitch_slider:
                default_transpose = self.main_window.default_values.get(
                    'transpose_default', 0)
                self.main_window.music_section.pitch_slider.set(default_transpose)
                self.main_window.music_section.update_transpose_value(default_transpose)

            print(
                f"✅ Ultra fast batch reset completed: {success_count}/{total_count} success")

        except Exception as e:
            print(f"❌ Ultra fast batch reset error: {e}")
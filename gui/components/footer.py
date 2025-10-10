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
    
    # Thay thế hàm _batch_reset_vocal_parameters trong file footer.py

    def _batch_reset_vocal_parameters(self):
        """
        Reset tất cả vocal parameters (Volume Mic, Reverb, Bass, Treble) 
        ULTRA OPTIMIZED: Chỉ screenshot và template matching MỘT LẦN cho tất cả controls.
        """
        # Lưu vị trí chuột ban đầu ngay từ đầu
        import pyautogui
        original_pos = pyautogui.position()
        
        try:
            print("⚡⚡⚡ ULTRA OPTIMIZED batch reset vocal parameters starting...")
            
            # --- BƯỚC 1: Tìm và focus window CHỈ MỘT LẦN ---
            print("🔍 Finding Cubase and XVox windows (once)...")
            proc = self.main_window.xvox_detector._find_cubase_process()
            if not proc:
                print("❌ Cubase process not found")
                return False
                
            if not self.main_window.xvox_detector._focus_cubase_window(proc):
                print("❌ Cannot focus Cubase window")
                return False
            
            plugin_win = self.main_window.xvox_detector._find_xvox_window()
            if not plugin_win:
                print("❌ XVox window not found")
                return False
            
            plugin_win.activate()
            import time
            time.sleep(0.1)
            print("✅ XVox window focused (once)")
            
            # --- BƯỚC 2: Lấy giá trị mặc định ---
            default_values = self.main_window.default_values
            xvox_volume_default = default_values.get('xvox_volume_default', 40)
            reverb_default = default_values.get('reverb_default', 36)
            bass_default = default_values.get('bass_default', -10)
            treble_default = default_values.get('treble_default', 20)
            
            # --- BƯỚC 3: ULTRA OPTIMIZED - Gọi hàm batch reset tất cả cùng lúc ---
            print("⚡ Calling ultra optimized batch reset (1 screenshot, 1 OCR/CV)...")
            success = self.main_window.xvox_detector.batch_reset_all_xvox_parameters(
                plugin_win, 
                xvox_volume_default, 
                reverb_default, 
                bass_default, 
                treble_default
            )
            
            if success:
                # Update UI for all controls
                if self.main_window.vocal_section:
                    if self.main_window.vocal_section.volume_mic_slider:
                        self.main_window.vocal_section.volume_mic_slider.set(xvox_volume_default)
                        self.main_window.vocal_section.volume_mic_value_label.configure(text=str(xvox_volume_default))
                    
                    if self.main_window.vocal_section.reverb_mic_slider:
                        self.main_window.vocal_section.reverb_mic_slider.set(reverb_default)
                        self.main_window.vocal_section.reverb_mic_value_label.configure(text=str(reverb_default))
                    
                    if self.main_window.vocal_section.bass_slider:
                        self.main_window.vocal_section.bass_slider.set(bass_default)
                        self.main_window.vocal_section.bass_value_label.configure(text=str(bass_default))
                    
                    if self.main_window.vocal_section.treble_slider:
                        self.main_window.vocal_section.treble_slider.set(treble_default)
                        self.main_window.vocal_section.treble_value_label.configure(text=str(treble_default))
                
                print("✅✅✅ ULTRA OPTIMIZED batch reset vocal parameters completed successfully!")
            else:
                print("❌ ULTRA OPTIMIZED batch reset failed")
            
            return success
                
        except Exception as e:
            print(f"❌ Error in ULTRA OPTIMIZED batch reset vocal parameters: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Chỉ trả về vị trí chuột một lần duy nhất ở cuối cùng
            pyautogui.moveTo(original_pos[0], original_pos[1])
            print("🖱️ Mouse cursor returned to original position.")
    
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

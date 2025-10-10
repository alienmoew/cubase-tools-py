"""
Main Window - Coordinator chính cho Cubase Auto Tool GUI.
Quản lý tất cả components và business logic.
"""
import os, sys
import customtkinter as CTK
import threading

import config
from features.tone_detector import ToneDetector
from features.transpose_detector import TransposeDetector
from features.autotune_controls_detector import AutoTuneControlsDetector
from features.plugin_bypass_detector import PluginBypassDetector
from features.soundshifter_detector import SoundShifterDetector
from features.soundshifter_bypass_detector import SoundShifterBypassDetector
from features.proq3_bypass_detector import ProQ3BypassDetector
from features.xvox_detector import XVoxDetector
from features.system_volume_detector import SystemVolumeDetector
from utils.settings_manager import SettingsManager
from utils.helpers import ConfigHelper, MessageHelper
from utils.bypass_toggle_manager import BypassToggleManager
from utils.debug_helper import DebugHelper
from utils.music_presets_manager import MusicPresetsManager
from utils.debug_window import DebugWindow
from utils.fast_batch_processor import FastBatchProcessor
from utils.ultra_fast_processor import UltraFastAutoTuneProcessor

# Import components
from gui.components.autotune_section import AutoTuneSection
from gui.components.music_section import MusicSection
from gui.components.vocal_section import VocalSection
from gui.components.footer import Footer


class MainWindow:
    """
    Main Window - Coordinator chính của ứng dụng.
    Quản lý tất cả components, detectors, và business logic.
    """

    def __init__(self):
        """Initialize main window và tất cả resources."""
        # --- Fix icon taskbar (Windows only) ---
        import ctypes
        myappid = 'ktstudio.autotools'  # tên app tùy ý
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
        # ---------------------------------------
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.default_values = ConfigHelper.load_default_values()

        # Load saved theme
        saved_theme = self.settings_manager.get_theme()
        CTK.set_appearance_mode(saved_theme)

        # Create root window
        self.root = CTK.CTk()
        self.root.title(f"{config.APP_NAME} {config.APP_VERSION}")
        self.root.geometry("1000x320")  # Increased height for larger fonts
        self.root.resizable(False, False)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "icon.ico")

        try:
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"⚠️ Could not set window icon: {e}")

        # Window state
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.is_topmost = True

        # Bind shortcuts
        self.root.bind("<Control-t>", lambda event: self._toggle_theme())
        self.root.bind("<Control-Shift-T>",
                       lambda event: self._toggle_topmost_mode())

        # Initialize detectors
        self.tone_detector = ToneDetector()
        self.transpose_detector = TransposeDetector()
        self.autotune_controls_detector = AutoTuneControlsDetector()
        self.plugin_bypass_detector = PluginBypassDetector()
        self.soundshifter_detector = SoundShifterDetector()
        self.soundshifter_bypass_detector = SoundShifterBypassDetector()
        self.proq3_bypass_detector = ProQ3BypassDetector()
        self.xvox_detector = XVoxDetector()

        # System Volume Detector (Windows Audio Session)
        app_name = self.default_values.get(
            'system_volume_app_name', 'chrome.exe')
        self.system_volume_detector = SystemVolumeDetector(app_name)

        # Initialize managers
        self.bypass_manager = BypassToggleManager(self)
        self.music_presets_manager = MusicPresetsManager()

        # Auto-detect state
        self.current_detected_tone = "--"

        # Theme state
        try:
            self.current_theme_index = config.GUI_THEMES.index(saved_theme)
        except ValueError:
            self.current_theme_index = 0

        # Debug window
        self.debug_window = DebugWindow(self)
        self._setup_debug_logging()

        # Components (will be created in _setup_ui)
        self.autotune_section = None
        self.music_section = None
        self.vocal_section = None
        self.footer = None

        # Plugin window references (for auto-minimize after actions)
        self.autokey_win = None
        self.autotune_win = None
        self.xvox_win = None
        self.soundshifter_win = None
        self.proq3_win = None

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Thiết lập UI với component-based architecture."""
        # Main container
        main_frame = CTK.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Content frame cho 3 sections
        content_frame = CTK.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Configure grid layout - 3 columns
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)

        # Create components
        self.autotune_section = AutoTuneSection(content_frame, self)
        autotune_container = self.autotune_section.create()
        autotune_container.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.music_section = MusicSection(content_frame, self)
        music_container = self.music_section.create()
        music_container.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        self.vocal_section = VocalSection(content_frame, self)
        vocal_container = self.vocal_section.create()
        vocal_container.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        # Footer
        self.footer = Footer(self.root, self)
        footer_container = self.footer.create()
        footer_container.pack(side="bottom", fill="x", padx=0, pady=0)

        # Initialize plugin toggle states
        self._initialize_plugin_toggle_state()

        # Initialize system volume display
        self._initialize_system_volume_display()

        # Disable topmost after UI setup
        self.root.after(1000, self._disable_topmost_mode)

        # Check all plugins after UI is ready
        self.root.after(1500, self._check_all_plugins_on_startup)

    def _check_all_plugins_on_startup(self):
        """Kiểm tra tất cả plugin khi khởi động ứng dụng."""
        print("🔍 Checking all plugins on startup...")
        print("=" * 60)

        missing_plugins = []
        from utils.window_manager import WindowManager

        # Check AUTO-KEY (Tone Detection)
        print("\n🔍 Checking AUTO-KEY...")
        autokey_win = WindowManager.find_window_containing("AUTO-KEY")
        if not autokey_win:
            missing_plugins.append("AUTO-KEY")
            print("❌ AUTO-KEY plugin not found")
        else:
            print(f"✅ AUTO-KEY plugin found: {autokey_win.title}")
            self.autokey_win = autokey_win  # Save reference

        # Check AUTO-TUNE PRO
        print("\n🔍 Checking AUTO-TUNE PRO...")
        autotune_win = WindowManager.find_window_containing("AUTO-TUNE PRO")
        if not autotune_win:
            missing_plugins.append("AUTO-TUNE PRO")
            print("❌ AUTO-TUNE PRO plugin not found")
        else:
            print(f"✅ AUTO-TUNE PRO plugin found: {autotune_win.title}")
            self.autotune_win = autotune_win  # Save reference

        # Check XVox
        print("\n🔍 Checking XVox...")
        xvox_win = WindowManager.find_window_containing("vox")
        if not xvox_win:
            missing_plugins.append("XVox")
            print("❌ XVox plugin not found")
        else:
            print(f"✅ XVox plugin found: {xvox_win.title}")
            self.xvox_win = xvox_win  # Save reference

        # Check SoundShifter
        print("\n🔍 Checking SoundShifter...")
        soundshifter_win = WindowManager.find_window_containing("SoundShifter")
        if not soundshifter_win:
            missing_plugins.append("SoundShifter Pitch Stereo")
            print("❌ SoundShifter plugin not found")
        else:
            print(f"✅ SoundShifter plugin found: {soundshifter_win.title}")
            self.soundshifter_win = soundshifter_win  # Save reference

        # Check ProQ3
        print("\n🔍 Checking ProQ3...")
        proq3_win = WindowManager.find_window_containing("Pro-Q")
        if not proq3_win:
            missing_plugins.append("Pro-Q 3")
            print("❌ ProQ3 plugin not found")
        else:
            print(f"✅ ProQ3 plugin found: {proq3_win.title}")
            self.proq3_win = proq3_win  # Save reference

        print("\n" + "=" * 60)

        # If any plugins are missing, show popup
        if missing_plugins:
            missing_list = "\n• ".join(missing_plugins)
            message = f"⚠️ Các plugin sau chưa được mở:\n\n• {missing_list}\n\nVui lòng mở tất cả plugin trong Cubase để sử dụng đầy đủ tính năng."

            MessageHelper.show_warning("Plugin chưa đầy đủ", message)
            print(f"⚠️ Missing plugins: {', '.join(missing_plugins)}")
        else:
            print("✅ All plugins are ready!")

            # Minimize all plugins except AUTO-KEY
            print("\n🔽 Minimizing plugins (keeping AUTO-KEY visible)...")
            self._minimize_all_plugins_except_autokey(
                autokey_win, autotune_win, xvox_win, soundshifter_win, proq3_win
            )


    def _minimize_all_plugins_except_autokey(self, autokey_win, autotune_win, xvox_win, soundshifter_win, proq3_win):
        """Minimize tất cả plugin trừ AUTO-KEY, và minimize Cubase window."""
        import win32gui
        import win32con
        import win32process
        from utils.window_manager import WindowManager
        from utils.process_finder import CubaseProcessFinder

        def minimize_all_windows_by_pid(pid):
            """Minimize all visible windows belonging to process"""
            import win32gui, win32process, win32con

            def callback(hwnd, hwnds):
                try:
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                        # Minimize without activating to avoid window title flash
                        win32gui.ShowWindow(hwnd, win32con.SW_SHOWMINNOACTIVE)
                        hwnds.append(hwnd)
                except Exception:
                    pass
                return True

            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            return hwnds


        # 🔽 Minimize Cubase
        print("   🔽 Minimizing Cubase...")
        try:
            proc = CubaseProcessFinder.find()
            if proc:
                hwnds = minimize_all_windows_by_pid(proc.info["pid"])
                print(f"   � Minimized {len(hwnds)} Cubase window(s)")
            else:
                print("   ⚠️ Cubase process not found")
        except Exception as e:
            print(f"   ⚠️ Could not minimize Cubase: {e}")

        # 🔽 Minimize other plugins
        plugins_to_minimize = [
            ("AUTO-TUNE PRO", autotune_win),
            ("XVox", xvox_win),
            ("SoundShifter", soundshifter_win),
            ("ProQ3", proq3_win)
        ]

        for plugin_name, plugin_win in plugins_to_minimize:
            if plugin_win:
                try:
                    plugin_win.minimize()
                    print(f"   🔽 Minimized: {plugin_name}")
                except Exception as e:
                    print(f"   ⚠️ Could not minimize {plugin_name}: {e}")

        # 👁️ Restore AUTO-KEY
        if autokey_win:
            try:
                import time
                time.sleep(0.2)
                autokey_win.restore()
                autokey_win.activate()
                print(f"   👁️ Restored and activated: AUTO-KEY")
            except Exception as e:
                print(f"   ⚠️ Could not restore AUTO-KEY: {e}")

        print("✅ Plugin windows organized!")

    def _minimize_plugins_after_action(self):
        """Minimize tất cả plugin trừ AUTO-KEY sau khi thực hiện action."""
        try:
            from utils.window_manager import WindowManager
            from utils.process_finder import CubaseProcessFinder
            import win32gui, win32con, win32process
            
            # Minimize Cubase windows
            try:
                proc = CubaseProcessFinder.find()
                if proc:
                    def minimize_callback(hwnd, hwnds):
                        try:
                            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                            if found_pid == proc.info["pid"] and win32gui.IsWindowVisible(hwnd):
                                # Use SW_SHOWMINNOACTIVE to minimize without activation/focus
                                win32gui.ShowWindow(hwnd, win32con.SW_SHOWMINNOACTIVE)
                                hwnds.append(hwnd)
                        except Exception:
                            pass
                        return True
                    
                    hwnds = []
                    win32gui.EnumWindows(minimize_callback, hwnds)
            except Exception:
                pass
            
            # Minimize plugins (using saved references)
            plugins = [
                ("AUTO-TUNE PRO", self.autotune_win),
                ("XVox", self.xvox_win),
                ("SoundShifter", self.soundshifter_win),
                ("ProQ3", self.proq3_win)
            ]
            
            for plugin_name, plugin_win in plugins:
                if plugin_win:
                    try:
                        plugin_win.minimize()
                    except Exception:
                        pass
            
            # Restore AUTO-KEY
            if self.autokey_win:
                try:
                    import time
                    time.sleep(0.1)  # Shorter delay for faster response
                    self.autokey_win.restore()
                    self.autokey_win.activate()
                except Exception:
                    pass
                    
        except Exception as e:
            # Silent fail - không làm gián đoạn workflow
            pass

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()

    # ==================== TONE DETECTION ====================

    def _execute_tone_detector(self):
        """Thực thi tính năng dò tone."""
        # Pause auto-detect
        self.pause_auto_detect_for_manual_action()

        try:
            # Truyền callback để cập nhật UI - sử dụng fast mode cho batch reset
            success = self.tone_detector.execute(
                tone_callback=self.update_current_tone, fast_mode=True)
            if success:
                print("✅ Tone detector completed successfully")

                # Batch reset tất cả về giá trị mặc định - nhanh và mượt hơn
                print("🔄 Batch resetting all Auto-Tune parameters to defaults...")
                self._batch_reset_autotune_parameters()

            else:
                print("❌ Tone detector failed")
        except Exception as e:
            print(f"❌ Error in tone detector: {e}")
        finally:
            # Luôn resume auto-detect
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _batch_reset_autotune_parameters(self):
        """Ultra fast batch reset tất cả parameters Auto-Tune."""
        # Prepare ultra fast batch parameters
        reset_configs = [
            ('Return Speed', self.autotune_controls_detector.return_speed_detector,
             'return_speed_default', 200),
            ('Flex Tune', self.autotune_controls_detector.flex_tune_detector,
             'flex_tune_default', 0)
            # ('Natural Vibrato', self.autotune_controls_detector.natural_vibrato_detector,
            #  'natural_vibrato_default', 0),
            # ('Humanize', self.autotune_controls_detector.humanize_detector,
            #  'humanize_default', 0),
            # ('Transpose', self.transpose_detector, 'transpose_default', 0)
        ]

        # Build parameters list for ultra fast processor
        parameters_list = []

        for name, detector, default_key, default_fallback in reset_configs:
            default_value = self.default_values.get(
                default_key, default_fallback)
            parameters_list.append({
                'detector': detector,
                'value': default_value,
                'name': name
            })

        # Execute ultra fast batch
        try:
            print("⚡ Ultra fast batch reset starting...")

            ultra_processor = UltraFastAutoTuneProcessor()
            success_count, total_count = ultra_processor.execute_ultra_fast_batch(
                parameters_list)

            # # Update UI for transpose
            # if self.autotune_section and self.autotune_section.pitch_slider:
            #     default_transpose = self.default_values.get(
            #         'transpose_default', 0)
            #     self.autotune_section.pitch_slider.set(default_transpose)
            #     self.autotune_section.update_transpose_value(default_transpose)

            print(
                f"✅ Ultra fast batch reset completed: {success_count}/{total_count} success")

        except Exception as e:
            print(f"❌ Ultra fast batch reset error: {e}")

    def update_current_tone(self, tone_text):
        """Cập nhật hiển thị tone hiện tại."""
        if self.autotune_section:
            self.autotune_section.update_current_tone(tone_text)
        self.current_detected_tone = tone_text

    def _toggle_auto_detect(self):
        """Bật/tắt chế độ auto detect."""
        is_enabled = self.autotune_section.auto_detect_switch.get()

        # Save auto-detect preference
        self.settings_manager.set_auto_detect(is_enabled)

        if is_enabled:
            print("🔄 Auto Detect ON")
            self.tone_detector.start_auto_detect(
                tone_callback=self.update_current_tone,
                current_tone_getter=lambda: self.current_detected_tone
            )
        else:
            print("⏹️ Auto Detect OFF")
            self.tone_detector.stop_auto_detect()

    def _start_auto_detect_from_saved_state(self):
        """Khởi động auto-detect từ trạng thái đã lưu."""
        try:
            self.tone_detector.start_auto_detect(
                tone_callback=self.update_current_tone,
                current_tone_getter=lambda: self.current_detected_tone
            )
        except Exception as e:
            print(f"❌ Lỗi khởi động auto-detect: {e}")

    def pause_auto_detect_for_manual_action(self):
        """Tạm dừng auto-detect khi có manual action."""
        self.tone_detector.pause_auto_detect()

    def resume_auto_detect_after_manual_action(self):
        """Khôi phục auto-detect sau khi manual action hoàn thành."""
        self.tone_detector.resume_auto_detect()

    # ==================== TRANSPOSE ====================

    def _apply_pitch_old(self):
        """Áp dụng pitch Già."""
        pitch_value = self.default_values.get('transpose_old', -7)
        self._apply_pitch(pitch_value)

    def _apply_pitch_normal(self):
        """Áp dụng pitch Bình thường (0)."""
        self._apply_pitch(0)

    def _apply_pitch_young(self):
        """Áp dụng pitch Trẻ."""
        pitch_value = self.default_values.get('transpose_young', 12)
        self._apply_pitch(pitch_value)

    def _apply_pitch(self, pitch_value):
        """Áp dụng pitch value."""
        self.pause_auto_detect_for_manual_action()

        try:
            # Update slider - THAY ĐỔI TỪ autotune_section SANG music_section
            if self.music_section and self.music_section.pitch_slider:
                self.music_section.pitch_slider.set(pitch_value)
                self.music_section.update_transpose_value(pitch_value)

            # Apply to Cubase
            success = self.transpose_detector.set_pitch_value(pitch_value)

            if success:
                print(f"✅ Đã set transpose: {pitch_value}")
            else:
                print(f"❌ Không thể set transpose: {pitch_value}")

        except Exception as e:
            print(f"❌ Lỗi khi set transpose: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    # ==================== MUSIC SECTION ====================

    def _raise_tone(self):
        """Nâng tone lên (+2)."""
        self.pause_auto_detect_for_manual_action()

        try:
            success = self.soundshifter_detector.raise_tone(1)  # 1 tone = +2
            if success:
                self._update_soundshifter_display()
                print("✅ Raised tone successfully")
            else:
                print("❌ Failed to raise tone")
        except Exception as e:
            print(f"❌ Error raising tone: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _lower_tone(self):
        """Hạ tone xuống (-2)."""
        self.pause_auto_detect_for_manual_action()

        try:
            success = self.soundshifter_detector.lower_tone(1)  # 1 tone = -2
            if success:
                self._update_soundshifter_display()
                print("✅ Lowered tone successfully")
            else:
                print("❌ Failed to lower tone")
        except Exception as e:
            print(f"❌ Error lowering tone: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _reset_soundshifter(self):
        """Reset SoundShifter về 0."""
        self.pause_auto_detect_for_manual_action()

        try:
            success = self.soundshifter_detector.reset_pitch()
            if success:
                self._update_soundshifter_display()
                print("✅ Reset SoundShifter successfully")
            else:
                print("❌ Failed to reset SoundShifter")
        except Exception as e:
            print(f"❌ Error resetting SoundShifter: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _update_soundshifter_display(self):
        """Cập nhật hiển thị giá trị Tone nhạc (delegate cho MusicSection để format)."""
        try:
            current_value = self.soundshifter_detector.current_value  # units, 2 units = 1 tone
            if self.music_section:
                # Let MusicSection format the value (shows 0 / +1 Tone / -0.5 Tone, ...)
                self.music_section.update_soundshifter_display(current_value)
            else:
                # Fallback: format here if music_section missing
                val = int(round(current_value))
                if val == 0:
                    text = "0 Tone"
                else:
                    tone = val / 2.0
                    sign = "+" if tone > 0 else ""
                    text = f"{sign}{int(tone)} Tone" if val % 2 == 0 else f"{sign}{tone:.1f} Tone"
                # Try to update label if exists
                try:
                    self.music_section.soundshifter_value_label.configure(text=text)
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ Error updating soundshifter display: {e}")


    def _apply_volume(self):
        """Áp dụng thay đổi Volume khi nhấn nút Áp Dụng."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()

        try:
            # Lấy giá trị từ slider
            volume_value = int(round(self.music_section.volume_slider.get()))

            print(f"🔊 Applying music volume: {volume_value}")

            # Thực hiện chỉnh Volume
            success = self.volume_detector.set_volume(volume_value)

            if success:
                print(f"✅ Music volume set to {volume_value} successfully")
            else:
                print(f"❌ Failed to set music volume to {volume_value}")

        except Exception as e:
            print(f"❌ Error in volume adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _toggle_mute(self):
        """Toggle mute âm lượng nhạc."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()

        try:
            print("🔇 Toggling music mute...")

            # Thực hiện toggle mute
            success = self.volume_detector.toggle_mute()

            if success:
                print("✅ Music mute toggled successfully")
                # Update button text để phản ánh trạng thái
                if self.music_section and self.music_section.mute_toggle_btn:
                    current_text = self.music_section.mute_toggle_btn.cget(
                        "text")
                    if "M" == current_text:
                        self.music_section.mute_toggle_btn.configure(text="U")
                    else:
                        self.music_section.mute_toggle_btn.configure(text="M")
            else:
                print("❌ Failed to toggle music mute")

        except Exception as e:
            print(f"❌ Error in mute toggle: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    # ==================== MUSIC PRESETS ====================

    def _adjust_music_preset(self, music_type, direction):
        """Điều chỉnh mức preset của loại nhạc (direction: +1 hoặc -1)."""
        try:
            if direction > 0:
                success = self.music_presets_manager.increase_level(music_type)
            else:
                success = self.music_presets_manager.decrease_level(music_type)

            if success:
                self.autotune_section._update_music_preset_display(music_type)
                current_level = self.music_presets_manager.get_current_level(
                    music_type)
                level_str = self.music_presets_manager.get_level_string(
                    current_level)
                print(f"🎵 {music_type} level: {level_str}")
            else:
                print(f"⚠️ Cannot adjust {music_type} level further")

        except Exception as e:
            print(f"❌ Error adjusting {music_type} preset: {e}")

    def _apply_music_preset(self, music_type):
        """Áp dụng preset hiện tại của loại nhạc."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()

        try:
            success = self.music_presets_manager.apply_preset(music_type, self)

            if success:
                current_level = self.music_presets_manager.get_current_level(
                    music_type)
                level_str = self.music_presets_manager.get_level_string(
                    current_level)
                level_desc = self.music_presets_manager.get_level_description(
                    current_level)
                print(
                    f"✅ Applied {music_type} preset level {level_str} ({level_desc})")
            else:
                print(f"❌ Failed to apply {music_type} preset")

        except Exception as e:
            print(f"❌ Error applying {music_type} preset: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    # ==================== VOCAL/MIC CONTROLS ====================

    def _adjust_bass_instant(self, direction):
        """Điều chỉnh bass và áp dụng ngay lập tức."""
        self.pause_auto_detect_for_manual_action()

        try:
            current_value = int(round(self.vocal_section.bass_slider.get()))
            step = self.default_values.get('bass_step', 5)
            min_value = self.default_values.get('bass_min', -30)
            max_value = self.default_values.get('bass_max', 30)

            # Tính giá trị mới
            new_value = current_value + (step * direction)

            # Giới hạn trong range
            new_value = max(min_value, min(max_value, new_value))

            # Cập nhật slider và label
            self.vocal_section.bass_slider.set(new_value)
            self.vocal_section.bass_value_label.configure(text=str(new_value))

            print(f"🎚️ Adjusting Bass to: {new_value} (step: {step})")

            # Áp dụng ngay lập tức
            success = self.xvox_detector.set_bass_value(new_value)

            if success:
                print(f"✅ Bass applied successfully: {new_value}")
            else:
                print(f"❌ Failed to apply bass: {new_value}")

        except Exception as e:
            print(f"❌ Error in bass adjustment: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _adjust_treble_instant(self, direction):
        """Điều chỉnh treble và áp dụng ngay lập tức."""
        self.pause_auto_detect_for_manual_action()

        try:
            current_value = int(round(self.vocal_section.treble_slider.get()))
            step = self.default_values.get('treble_step', 5)
            min_value = self.default_values.get('treble_min', -20)
            max_value = self.default_values.get('treble_max', 30)

            # Tính giá trị mới
            new_value = current_value + (step * direction)

            # Giới hạn trong range
            new_value = max(min_value, min(max_value, new_value))

            # Cập nhật slider và label
            self.vocal_section.treble_slider.set(new_value)
            self.vocal_section.treble_value_label.configure(
                text=str(new_value))

            print(f"🎚️ Adjusting Treble to: {new_value} (step: {step})")

            # Áp dụng ngay lập tức
            success = self.xvox_detector.set_treble_value(new_value)

            if success:
                print(f"✅ Treble applied successfully: {new_value}")
            else:
                print(f"❌ Failed to apply treble: {new_value}")

        except Exception as e:
            print(f"❌ Error in treble adjustment: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _adjust_volume_mic_instant(self, direction):
        """Điều chỉnh volume mic (COMP) và áp dụng ngay lập tức."""
        self.pause_auto_detect_for_manual_action()

        try:
            current_value = int(
                round(self.vocal_section.volume_mic_slider.get()))
            step = self.default_values.get('xvox_volume_step', 5)
            min_value = self.default_values.get('xvox_volume_min', 30)
            max_value = self.default_values.get('xvox_volume_max', 60)

            # Tính giá trị mới
            new_value = current_value + (step * direction)

            # Giới hạn trong range
            new_value = max(min_value, min(max_value, new_value))

            # Cập nhật slider và label
            self.vocal_section.volume_mic_slider.set(new_value)
            self.vocal_section.volume_mic_value_label.configure(
                text=str(new_value))

            print(f"🎚️ Adjusting Volume Mic to: {new_value} (step: {step})")

            # Áp dụng ngay lập tức
            success = self.xvox_detector.set_comp_value(new_value)

            if success:
                print(f"✅ Volume Mic applied successfully: {new_value}")
            else:
                print(f"❌ Failed to apply volume mic: {new_value}")

        except Exception as e:
            print(f"❌ Error in volume mic adjustment: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _adjust_reverb_mic_instant(self, direction):
        """Điều chỉnh reverb mic và áp dụng ngay lập tức."""
        self.pause_auto_detect_for_manual_action()

        try:
            current_value = int(
                round(self.vocal_section.reverb_mic_slider.get()))
            step = self.default_values.get('reverb_step', 2)
            min_value = self.default_values.get('reverb_min', 30)
            max_value = self.default_values.get('reverb_max', 42)

            # Tính giá trị mới
            new_value = current_value + (step * direction)

            # Giới hạn trong range
            new_value = max(min_value, min(max_value, new_value))

            # Cập nhật slider và label
            self.vocal_section.reverb_mic_slider.set(new_value)
            self.vocal_section.reverb_mic_value_label.configure(
                text=str(new_value))

            print(f"🎚️ Adjusting Reverb Mic to: {new_value} (step: {step})")

            # Áp dụng ngay lập tức
            success = self.xvox_detector.set_reverb_value(new_value)

            if success:
                print(f"✅ Reverb Mic applied successfully: {new_value}")
            else:
                print(f"❌ Failed to apply reverb mic: {new_value}")

        except Exception as e:
            print(f"❌ Error in reverb mic adjustment: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()
            # Minimize plugins after action
            self._minimize_plugins_after_action()

    def _toggle_mic_mute(self):
        """Toggle mute mic trong Cubase (Ctrl+M)."""
        self.pause_auto_detect_for_manual_action()

        try:
            from utils.process_finder import CubaseProcessFinder
            from utils.window_manager import WindowManager
            import pyautogui
            import time
            import win32gui
            import win32process

            print("=" * 60)
            print("🎤 [MIC MUTE] Starting toggle mic mute...")

            # 1. Tìm Cubase process
            cubase_proc = CubaseProcessFinder.find()
            if not cubase_proc:
                print("❌ [MIC MUTE] Không tìm thấy Cubase process!")
                return
            
            pid = cubase_proc.info['pid']
            print(f"✅ [MIC MUTE] Found Cubase process: PID={pid}")

            # 2. Tìm MAIN Cubase project window (không phải plugin window)
            print(f"🔍 [MIC MUTE] Finding main Cubase project window...")
            
            main_hwnd = None
            
            def find_main_window(hwnd, extra):
                nonlocal main_hwnd
                try:
                    if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                        if found_pid == pid:
                            title = win32gui.GetWindowText(hwnd)
                            # Tìm window có title chứa "Cubase" và "Project" (cửa sổ chính)
                            # Và KHÔNG phải là plugin window (Ins., AUTO-TUNE, XVox, etc.)
                            if title and 'cubase' in title.lower() and 'project' in title.lower():
                                if not any(x in title.lower() for x in ['ins.', 'auto-tune', 'xvox', 'soundshifter', 'pro-q']):
                                    print(f"   🎯 Found main window: '{title}'")
                                    main_hwnd = hwnd
                                    return False  # Stop enumeration
                except Exception:
                    pass
                return True
            
            win32gui.EnumWindows(find_main_window, None)
            
            if not main_hwnd:
                print("⚠️ [MIC MUTE] Không tìm thấy main Cubase window, thử fallback...")
                # Fallback: Tìm bất kỳ window nào có "Cubase" và không phải plugin
                def find_any_cubase_window(hwnd, extra):
                    nonlocal main_hwnd
                    try:
                        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                            if found_pid == pid:
                                title = win32gui.GetWindowText(hwnd)
                                if title and 'cubase' in title.lower():
                                    if not any(x in title.lower() for x in ['ins.', 'auto-tune', 'xvox', 'soundshifter', 'pro-q']):
                                        print(f"   🎯 Found fallback window: '{title}'")
                                        main_hwnd = hwnd
                                        return False
                    except Exception:
                        pass
                    return True
                
                win32gui.EnumWindows(find_any_cubase_window, None)
            
            if not main_hwnd:
                print("❌ [MIC MUTE] Không thể tìm main Cubase window!")
                return
            
            # 3. Focus main Cubase window
            try:
                title = win32gui.GetWindowText(main_hwnd)
                print(f"✅ [MIC MUTE] Focusing main window: '{title}' (HWND={main_hwnd})")
                
                win32gui.ShowWindow(main_hwnd, 9)  # SW_RESTORE
                win32gui.BringWindowToTop(main_hwnd)
                win32gui.SetForegroundWindow(main_hwnd)
            except Exception as e:
                print(f"❌ [MIC MUTE] Lỗi khi focus window: {e}")
                return

            # 4. Đợi window được focus
            time.sleep(0.3)

            # 5. Nhấn Ctrl+M
            print(f"⌨️ [MIC MUTE] Sending Ctrl+M...")
            pyautogui.keyDown('ctrl')
            time.sleep(0.05)
            pyautogui.press('m')
            time.sleep(0.05)
            pyautogui.keyUp('ctrl')
            
            print("✅ [MIC MUTE] Đã nhấn Ctrl+M để toggle mute mic")
            print("=" * 60)

        except Exception as e:
            print(f"❌ [MIC MUTE] Lỗi khi toggle mic mute: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.resume_auto_detect_after_manual_action()
            self._minimize_plugins_after_action()

    # ==================== PLUGIN TOGGLE ====================

    def _initialize_plugin_toggle_state(self):
        """Initialize plugin toggle states using bypass_manager."""
        try:
            # Register all bypass toggles with the manager
            if self.autotune_section:
                self.bypass_manager.register_toggle('plugin', self.plugin_bypass_detector,
                                                    self.autotune_section.plugin_bypass_toggle,
                                                    self.autotune_section.plugin_state_label)

            if self.music_section:
                self.bypass_manager.register_toggle('soundshifter', self.soundshifter_bypass_detector,
                                                    self.music_section.soundshifter_bypass_toggle,
                                                    self.music_section.soundshifter_bypass_status_label)

            if self.vocal_section:
                self.bypass_manager.register_toggle('proq3', self.proq3_bypass_detector,
                                                    self.vocal_section.proq3_bypass_toggle,
                                                    self.vocal_section.proq3_bypass_status_label)

            # Initialize all toggles using the manager
            self.bypass_manager.initialize_all_toggles()

        except Exception as e:
            print(f"❌ Lỗi khởi tạo toggle states: {e}")

    # ==================== THEME & UI ====================

    def _toggle_theme(self):
        """Toggle theme."""
        self.current_theme_index = (
            self.current_theme_index + 1) % len(config.GUI_THEMES)
        new_theme = config.GUI_THEMES[self.current_theme_index]

        CTK.set_appearance_mode(new_theme)
        self.settings_manager.set_theme(new_theme)

        print(f"🎨 Theme changed to: {new_theme}")

    def _toggle_topmost_mode(self):
        """Toggle always on top mode."""
        self.is_topmost = not self.is_topmost
        self.root.attributes('-topmost', self.is_topmost)

        status = "ON" if self.is_topmost else "OFF"
        print(f"📌 Always on top: {status}")

    def _disable_topmost_mode(self):
        """Disable topmost mode sau khi khởi động."""
        self.is_topmost = False
        self.root.attributes('-topmost', False)

    def _show_debug_window(self):
        """Hiển thị debug window."""
        if self.debug_window:
            self.debug_window.show()

    def _setup_debug_logging(self):
        """Setup debug logging để capture print statements."""
        import sys
        import builtins

        original_print = builtins.print

        def custom_print(*args, **kwargs):
            # Call original print
            original_print(*args, **kwargs)

            # Also log to debug window
            if self.debug_window:
                message = ' '.join(str(arg) for arg in args)

                # Determine log level based on message content
                if '❌' in message or 'ERROR' in message or 'Error' in message:
                    level = 'ERROR'
                elif '⚠️' in message or 'WARNING' in message or 'Warning' in message:
                    level = 'WARNING'
                elif '✅' in message or 'SUCCESS' in message or 'Success' in message:
                    level = 'SUCCESS'
                else:
                    level = 'INFO'

                try:
                    self.debug_window.add_log(message, level)
                except:
                    pass  # Ignore errors in debug logging

        builtins.print = custom_print

    # ==================== SYSTEM VOLUME CONTROL (NEW) ====================

    def _increase_system_volume(self):
        """Tăng volume của app (Chrome, etc.) qua Windows Audio API."""
        self.pause_auto_detect_for_manual_action()
        try:
            step = int(self.default_values.get('system_volume_step', 5))
            success = self.system_volume_detector.increase_volume(step)

            if success:
                # Update display
                current_percent = self.system_volume_detector.get_volume_percent()
                self._update_system_volume_display(current_percent)
                print(f"✅ Increased system volume to {current_percent}%")
            else:
                print(f"⚠️ Failed to increase system volume (app may not be running)")
        except Exception as e:
            print(f"❌ Error increasing system volume: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()

    def _decrease_system_volume(self):
        """Giảm volume của app (Chrome, etc.) qua Windows Audio API."""
        self.pause_auto_detect_for_manual_action()
        try:
            step = int(self.default_values.get('system_volume_step', 5))
            success = self.system_volume_detector.decrease_volume(step)

            if success:
                # Update display
                current_percent = self.system_volume_detector.get_volume_percent()
                self._update_system_volume_display(current_percent)
                print(f"✅ Decreased system volume to {current_percent}%")
            else:
                print(f"⚠️ Failed to decrease system volume (app may not be running)")
        except Exception as e:
            print(f"❌ Error decreasing system volume: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()

    def _toggle_system_mute(self):
        """Toggle mute/unmute của app qua Windows Audio API."""
        self.pause_auto_detect_for_manual_action()
        try:
            success = self.system_volume_detector.toggle_mute()

            if success:
                is_muted = self.system_volume_detector.is_muted()
                current_percent = self.system_volume_detector.get_volume_percent()

                # Update display
                self._update_system_volume_display(current_percent)
                self._update_mute_button(is_muted)

                status = "muted" if is_muted else "unmuted"
                print(f"✅ System volume {status}")
            else:
                print(f"⚠️ Failed to toggle mute (app may not be running)")
        except Exception as e:
            print(f"❌ Error toggling mute: {e}")
        finally:
            self.resume_auto_detect_after_manual_action()

    def _update_system_volume_display(self, percent):
        """Cập nhật hiển thị volume (phần trăm)."""
        try:
            if self.music_section and self.music_section.volume_value_label:
                self.music_section.volume_value_label.configure(
                    text=f"{percent}%")
        except Exception as e:
            print(f"❌ Error updating volume display: {e}")

    def _update_mute_button(self, is_muted):
        """Cập nhật text của mute button."""
        try:
            if self.music_section and self.music_section.mute_toggle_btn:
                if is_muted:
                    self.music_section.mute_toggle_btn.configure(
                        text="Tắt",
                        fg_color="#E91E63",
                        hover_color="#C2185B"
                    )
                else:
                    self.music_section.mute_toggle_btn.configure(
                        text="Bật",
                        fg_color="#4CAF50",
                        hover_color="#388E3C"
                    )
        except Exception as e:
            print(f"❌ Error updating mute button: {e}")

    def _initialize_system_volume_display(self):
        """Khởi tạo hiển thị volume khi app start."""
        try:
            current_percent = self.system_volume_detector.get_volume_percent()
            is_muted = self.system_volume_detector.is_muted()

            self._update_system_volume_display(current_percent)
            self._update_mute_button(is_muted)

            print(
                f"🔊 Initial system volume: {current_percent}% (muted: {is_muted})")
        except Exception as e:
            print(f"⚠️ Could not initialize system volume display: {e}")
            # Set default display
            self._update_system_volume_display(0)
            self._update_mute_button(False)

    # ==================== CLEANUP ====================

    def __del__(self):
        """Cleanup khi destroy window."""
        # Stop auto-detect
        try:
            self.tone_detector.stop_auto_detect()
        except:
            pass

        # Destroy debug window
        if hasattr(self, 'debug_window') and self.debug_window and self.debug_window.window:
            try:
                self.debug_window.window.destroy()
            except:
                pass

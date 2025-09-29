import customtkinter as CTK

import config
from features.tone_detector import ToneDetector
from utils.settings_manager import SettingsManager

class CubaseAutoToolGUI:
    """GUI chính của ứng dụng."""
    
    def __init__(self):
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Load saved theme
        saved_theme = self.settings_manager.get_theme()
        CTK.set_appearance_mode(saved_theme)
        
        self.root = CTK.CTk()
        self.root.title(f"{config.APP_NAME} {config.APP_VERSION}")
        self.root.geometry("1000x450")
        self.root.resizable(False, False)  # Disable resizing
        
        # Bind theme shortcut key (Ctrl+T)
        self.root.bind("<Control-t>", lambda event: self._toggle_theme())
        
        self.tone_detector = ToneDetector()
        self.current_tone_label = None  # Để lưu reference tới label hiển thị tone
        self.auto_detect_switch = None  # Toggle switch
        self.current_detected_tone = "--"  # Lưu tone hiện tại để so sánh
        
        # Set current theme index based on saved theme
        try:
            self.current_theme_index = config.GUI_THEMES.index(saved_theme)
        except ValueError:
            self.current_theme_index = 0
            
        self.theme_button = None  # Reference to theme button
        self._setup_ui()
    
    def _setup_ui(self):

        # Main container frame
        main_frame = CTK.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid columns with equal weight
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1) 
        main_frame.grid_columnconfigure(2, weight=1)
        
        # Auto-Tune Section
        self._create_section(main_frame, "Auto-Tune", 0, self._setup_autotune_section)
        
        # Nhạc Section  
        self._create_section(main_frame, "Nhạc", 1, self._setup_music_section)
        
        # Giọng hát Section
        self._create_section(main_frame, "Giọng hát", 2, self._setup_vocal_section)
        
        # Setup footer after main content
        self._setup_footer()
    
    def _create_section(self, parent, title, column, setup_func):
        """Tạo một section với tiêu đề và nội dung."""
        # Section frame
        section_frame = CTK.CTkFrame(parent, corner_radius=10)
        section_frame.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)
        
        # Section title
        title_label = CTK.CTkLabel(
            section_frame,
            text=title,
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(15, 20))
        
        # Content frame
        content_frame = CTK.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Setup section content
        setup_func(content_frame)
    
    def _setup_autotune_section(self, parent):
        """Thiết lập nội dung cho section Auto-Tune."""
        # Current Tone Display
        self.current_tone_label = CTK.CTkLabel(
            parent,
            text="Tone hiện tại: --",
            font=("Arial", 18, "bold"),
            text_color="#2CC985"  # Màu xanh lá
        )
        self.current_tone_label.pack(pady=(0, 10))
        
        # Auto Detect Toggle
        auto_detect_frame = CTK.CTkFrame(parent, fg_color="transparent")
        auto_detect_frame.pack(pady=(0, 15))
        
        auto_detect_label = CTK.CTkLabel(
            auto_detect_frame,
            text="Tự động dò Tone:",
            font=("Arial", 16, "bold")
        )
        auto_detect_label.pack(side="left", padx=(0, 10))
        
        self.auto_detect_switch = CTK.CTkSwitch(
            auto_detect_frame,
            text="",
            command=self._toggle_auto_detect,
            width=50,
            height=25
        )
        
        # Load saved auto-detect state
        saved_auto_detect = self.settings_manager.get_auto_detect()
        
        if saved_auto_detect:
            self.auto_detect_switch.select()
        
        self.auto_detect_switch.pack(side="left")
        
        # Auto-start if previously enabled
        if saved_auto_detect:
            print("� Auto-detect đã được bật từ lần trước")
            # Use after_idle to ensure UI is fully initialized
            self.root.after_idle(lambda: self._start_auto_detect_from_saved_state())
        
        # Tone Detector Button
        btn_tone = CTK.CTkButton(
            parent,
            text=self.tone_detector.get_name(),
            font=("Arial", 16, "bold"),
            command=self._execute_tone_detector,
            width=200,
            height=45
        )
        btn_tone.pack(pady=5)
        
        # Placeholder for more auto-tune features
        placeholder = CTK.CTkLabel(
            parent,
            text="Thêm tính năng\nAuto-Tune khác...",
            font=("Arial", 12),
            text_color="gray"
        )
        placeholder.pack(pady=20)
    
    def _setup_music_section(self, parent):
        """Thiết lập nội dung cho section Nhạc."""
        # Example button cho tương lai
        btn_example = CTK.CTkButton(
            parent,
            text="Tính năng Nhạc\n(Demo)",
            command=self._example_music_feature,
            height=50,
            font=("Arial", 16, "bold")
        )
        btn_example.pack(pady=5)
        
        placeholder = CTK.CTkLabel(
            parent,
            text="Các tính năng\nxử lý nhạc\nsẽ có ở đây",
            font=("Arial", 14),
            text_color="gray"
        )
        placeholder.pack(pady=20)
    
    def _setup_vocal_section(self, parent):
        """Thiết lập nội dung cho section Giọng hát."""
        placeholder = CTK.CTkLabel(
            parent,
            text="Các tính năng\nxử lý giọng hát\nsẽ có ở đây", 
            font=("Arial", 14),
            text_color="gray"
        )
        placeholder.pack(expand=True)
    
    def _setup_footer(self):
        """Thiết lập footer với thông tin bản quyền."""
        # Separator line
        separator = CTK.CTkFrame(self.root, height=2, fg_color="#404040")
        separator.pack(fill="x", padx=20, pady=(15, 5))
        
        footer_frame = CTK.CTkFrame(self.root, fg_color="transparent", height=40)
        footer_frame.pack(fill="x", padx=25, pady=(0, 15))
        
        # App version (left side)
        version_label = CTK.CTkLabel(
            footer_frame,
            text=f"{config.APP_NAME} {config.APP_VERSION}",
            font=("Arial", 12),
            text_color="gray"
        )
        version_label.pack(side="left")
        
        # Theme switcher (center)
        theme_icons = {"dark": "🌙", "light": "☀️"}
        current_theme = config.GUI_THEMES[self.current_theme_index]
        icon = theme_icons.get(current_theme, "🎨")
        
        self.theme_button = CTK.CTkButton(
            footer_frame,
            text=icon,
            command=self._toggle_theme,
            width=30,
            height=25,
            font=("Arial", 16),
            corner_radius=6
        )
        self.theme_button.pack(side="left", padx=(15, 0))
        
        # Copyright information (right side) - clickable
        copyright_label = CTK.CTkLabel(
            footer_frame,
            text=config.COPYRIGHT,
            font=("Arial", 14, "bold"),
            text_color="#FF0000",
            cursor="hand2"
        )
        copyright_label.pack(side="right")
        
        # Make copyright clickable (copy phone to clipboard)
        def copy_phone(event):
            try:
                import pyperclip
                pyperclip.copy("0948999892")
                # Temporary feedback
                original_text = copyright_label.cget("text")
                copyright_label.configure(text="📞 Đã sao chép số điện thoại!", text_color="#00aa00")
                self.root.after(2000, lambda: copyright_label.configure(
                    text=original_text, text_color="#666666"))
                print("📞 Copied phone number to clipboard: 0948999892")
            except ImportError:
                print("📞 Phone: 0948999892")
        
        copyright_label.bind("<Button-1>", copy_phone)
    
    def update_current_tone(self, tone_text):
        """Cập nhật hiển thị tone hiện tại."""
        if self.current_tone_label:
            self.current_tone_label.configure(text=f"Tone hiện tại: {tone_text}")
        # Cập nhật tone hiện tại để so sánh trong auto detect
        self.current_detected_tone = tone_text
    
    def _toggle_auto_detect(self):
        """Bật/tắt chế độ auto detect."""
        is_enabled = self.auto_detect_switch.get()
        
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
    
    def _execute_tone_detector(self):
        """Thực thi tính năng dò tone."""
        # Pause auto-detect
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Truyền callback để cập nhật UI
            success = self.tone_detector.execute(tone_callback=self.update_current_tone)
            if success:
                print("✅ Tone detector completed successfully")
            else:
                print("❌ Tone detector failed")
        except Exception as e:
            print(f"❌ Error in tone detector: {e}")
        finally:
            # Luôn resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def run(self):
        """Chạy ứng dụng."""
        # Đặt protocol để cleanup khi đóng
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Cleanup khi đóng ứng dụng."""
        # Dừng auto detect nếu đang chạy
        if self.auto_detect_switch and self.auto_detect_switch.get():
            self.tone_detector.stop_auto_detect()
        
        self.root.destroy()
    
    def pause_auto_detect_for_manual_action(self):
        """Tạm dừng auto-detect khi có manual action."""
        self.tone_detector.pause_auto_detect()
    
    def resume_auto_detect_after_manual_action(self):
        """Khôi phục auto-detect sau khi manual action hoàn thành."""
        self.tone_detector.resume_auto_detect()
    
    def _toggle_theme(self):
        """Chuyển đổi theme giữa dark và light."""
        # Cycle through themes (dark <-> light)
        self.current_theme_index = (self.current_theme_index + 1) % len(config.GUI_THEMES)
        new_theme = config.GUI_THEMES[self.current_theme_index]
        
        # Apply theme
        CTK.set_appearance_mode(new_theme)
        
        # Save theme preference
        self.settings_manager.set_theme(new_theme)
        
        # Theme-specific icons (only dark/light)
        theme_icons = {"dark": "🌙", "light": "☀️"}
        icon = theme_icons.get(new_theme, "🎨")
        
        # Update button icon
        if self.theme_button:
            self.theme_button.configure(text=icon)
        
        print(f"🎨 Theme switched to: {new_theme}")
    
    def _start_auto_detect_from_saved_state(self):
        """Khởi động auto-detect từ trạng thái đã lưu."""
        try:
            self.tone_detector.start_auto_detect(
                tone_callback=self.update_current_tone,
                current_tone_getter=lambda: self.current_detected_tone
            )
        except Exception as e:
            print(f"❌ Lỗi khởi động auto-detect: {e}")
    
    def _example_music_feature(self):
        """Example chức năng để demo auto-pause system."""
        import time
        
        # Pause auto-detect
        self.pause_auto_detect_for_manual_action()
        
        try:
            print("🎵 Chức năng Nhạc bắt đầu...")
            # Giả lập làm việc 3 giây
            for i in range(3):
                time.sleep(1)
                print(f"🎵 Đang xử lý... {i+1}/3")
            print("✅ Chức năng Nhạc hoàn thành!")
        except Exception as e:
            print(f"❌ Lỗi chức năng Nhạc: {e}")
        finally:
            # Luôn resume auto-detect
            self.resume_auto_detect_after_manual_action()



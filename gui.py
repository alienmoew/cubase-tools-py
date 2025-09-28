import customtkinter as CTK
from features.tone_detector import ToneDetector
from utils.auto_pause_decorator import pause_auto_on_manual

class CubaseAutoToolGUI:
    """GUI chính của ứng dụng."""
    
    def __init__(self):
        self.root = CTK.CTk()
        self.root.title("Cubase Auto Tools")
        self.root.geometry("1000x400")
        
        self.tone_detector = ToneDetector()
        self.current_tone_label = None  # Để lưu reference tới label hiển thị tone
        self.auto_detect_switch = None  # Toggle switch
        self.current_detected_tone = "--"  # Lưu tone hiện tại để so sánh
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
    
    def _create_section(self, parent, title, column, setup_func):
        """Tạo một section với tiêu đề và nội dung."""
        # Section frame
        section_frame = CTK.CTkFrame(parent, corner_radius=10)
        section_frame.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)
        
        # Section title
        title_label = CTK.CTkLabel(
            section_frame,
            text=title,
            font=("Arial", 16, "bold")
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
            font=("Arial", 14, "bold"),
            text_color="#2CC985"  # Màu xanh lá
        )
        self.current_tone_label.pack(pady=(0, 10))
        
        # Auto Detect Toggle
        auto_detect_frame = CTK.CTkFrame(parent, fg_color="transparent")
        auto_detect_frame.pack(pady=(0, 15))
        
        auto_detect_label = CTK.CTkLabel(
            auto_detect_frame,
            text="Auto Detect:",
            font=("Arial", 12)
        )
        auto_detect_label.pack(side="left", padx=(0, 10))
        
        self.auto_detect_switch = CTK.CTkSwitch(
            auto_detect_frame,
            text="",
            command=self._toggle_auto_detect,
            width=50,
            height=25
        )
        self.auto_detect_switch.pack(side="left")
        
        # Tone Detector Button
        btn_tone = CTK.CTkButton(
            parent,
            text=self.tone_detector.get_name(),
            font=("Arial", 12),
            command=self._execute_tone_detector,
            width=180,
            height=35
        )
        btn_tone.pack(pady=5)
        
        # Placeholder for more auto-tune features
        placeholder = CTK.CTkLabel(
            parent,
            text="Thêm tính năng\nAuto-Tune khác...",
            font=("Arial", 10),
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
            height=40,
            font=("Arial", 12, "bold")
        )
        btn_example.pack(pady=5)
        
        placeholder = CTK.CTkLabel(
            parent,
            text="Các tính năng\nxử lý nhạc\nsẽ có ở đây",
            font=("Arial", 10),
            text_color="gray"
        )
        placeholder.pack(pady=20)
    
    def _setup_vocal_section(self, parent):
        """Thiết lập nội dung cho section Giọng hát."""
        placeholder = CTK.CTkLabel(
            parent,
            text="Các tính năng\nxử lý giọng hát\nsẽ có ở đây", 
            font=("Arial", 12),
            text_color="gray"
        )
        placeholder.pack(expand=True)
    
    def update_current_tone(self, tone_text):
        """Cập nhật hiển thị tone hiện tại."""
        if self.current_tone_label:
            self.current_tone_label.configure(text=f"Tone hiện tại: {tone_text}")
        # Cập nhật tone hiện tại để so sánh trong auto detect
        self.current_detected_tone = tone_text
    
    def _toggle_auto_detect(self):
        """Bật/tắt chế độ auto detect."""
        if self.auto_detect_switch.get():
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



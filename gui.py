import customtkinter as CTK
from features.tone_detector import ToneDetector

class CubaseAutoToolGUI:
    """GUI chính của ứng dụng."""
    
    def __init__(self):
        self.root = CTK.CTk()
        self.root.title("Cubase Auto Tools")
        self.root.geometry("1000x400")
        
        self.tone_detector = ToneDetector()
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
        placeholder = CTK.CTkLabel(
            parent,
            text="Các tính năng\nxử lý nhạc\nsẽ có ở đây",
            font=("Arial", 12),
            text_color="gray"
        )
        placeholder.pack(expand=True)
    
    def _setup_vocal_section(self, parent):
        """Thiết lập nội dung cho section Giọng hát."""
        placeholder = CTK.CTkLabel(
            parent,
            text="Các tính năng\nxử lý giọng hát\nsẽ có ở đây", 
            font=("Arial", 12),
            text_color="gray"
        )
        placeholder.pack(expand=True)
    
    def _execute_tone_detector(self):
        """Thực thi tính năng dò tone."""
        try:
            success = self.tone_detector.execute()
            if success:
                print("✅ Tone detector completed successfully")
            else:
                print("❌ Tone detector failed")
        except Exception as e:
            print(f"❌ Error in tone detector: {e}")
    
    def run(self):
        """Chạy ứng dụng."""
        self.root.mainloop()



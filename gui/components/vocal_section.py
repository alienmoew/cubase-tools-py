"""
Vocal/Mic Section Component - Bass, Treble, COMP, Reverb controls.
"""
import customtkinter as CTK
from gui.components.base_component import BaseComponent


class VocalSection(BaseComponent):
    """Component cho Vocal/Mic section với Bass, Treble, COMP, Reverb controls."""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        
        # UI element references
        self.proq3_bypass_toggle = None
        self.proq3_bypass_status_label = None
        
        # Mic controls
        self.bass_value_label = None
        self.bass_decrease_btn = None
        self.bass_increase_btn = None
        self.bass_slider = None
        
        self.treble_value_label = None
        self.treble_decrease_btn = None
        self.treble_increase_btn = None
        self.treble_slider = None
        
        self.volume_mic_value_label = None
        self.volume_mic_decrease_btn = None
        self.volume_mic_increase_btn = None
        self.volume_mic_slider = None
        
        self.reverb_mic_value_label = None
        self.reverb_mic_decrease_btn = None
        self.reverb_mic_increase_btn = None
        self.reverb_mic_slider = None
        
    def create(self):
        """Tạo Vocal section với tất cả controls."""
        # Section frame - minimal
        self.container = CTK.CTkFrame(self.parent, corner_radius=6, border_width=1, border_color="#404040")
        
        # Header với title và toggle
        self._create_header()
        
        # Content frame - minimal
        content_frame = CTK.CTkFrame(self.container, fg_color="transparent")
        # GIẢM PADDING XUỐNG 2 ĐỂ LOẠI BỎ KHOẢNG CÁCH THỪA 2 BÊN
        content_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        
        # Mic controls grid (2x2 layout)
        self._create_mic_controls(content_frame)
        
        return self.container
    
    def _create_header(self):
        """Tạo header với title và bypass toggle."""
        header_frame = CTK.CTkFrame(self.container, fg_color="#1E1E1E", corner_radius=4)
        header_frame.pack(fill="x", padx=4, pady=4)
        
        # Title
        title_label = CTK.CTkLabel(
            header_frame,
            text="Giọng hát",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(side="left", padx=8, pady=4)
        
        # Lofi (ProQ3) Toggle (right side)
        toggle_container = CTK.CTkFrame(header_frame, fg_color="transparent")
        toggle_container.pack(side="right", padx=8)
        
        self.proq3_bypass_toggle = CTK.CTkSwitch(
            toggle_container,
            text="",
            command=lambda: self.main_window.bypass_manager.toggle_bypass('proq3'),
            width=35,
            height=18,
            fg_color="#666666",
            progress_color="#4CAF50"
        )
        self.proq3_bypass_toggle.pack(side="left", padx=(0, 5))
        
        self.proq3_bypass_status_label = CTK.CTkLabel(
            toggle_container,
            text="ProQ3",
            font=("Arial", 11, "bold"),
            text_color="#4CAF50",
            width=30
        )
        self.proq3_bypass_status_label.pack(side="left")
    
    def _create_mic_controls(self, parent):
        """Tạo mic controls grid (2x2 layout)."""
        mic_controls_grid = CTK.CTkFrame(parent, fg_color="transparent")
        # ĐẢM BẢO GRID LẤP ĐẦY KHÔNG GIAN
        mic_controls_grid.pack(fill="both", expand=True, pady=0, padx=0)
        
        # Configure grid for 2x2 layout
        mic_controls_grid.grid_columnconfigure(0, weight=1)
        mic_controls_grid.grid_columnconfigure(1, weight=1)
        mic_controls_grid.grid_rowconfigure(0, weight=1)
        mic_controls_grid.grid_rowconfigure(1, weight=1)
        
        # Bass (Top Left)
        self._create_bass_control(mic_controls_grid)
        
        # Treble (Top Right)
        self._create_treble_control(mic_controls_grid)
        
        # COMP (Bottom Left)
        self._create_volume_mic_control(mic_controls_grid)
        
        # Reverb (Bottom Right)
        self._create_reverb_control(mic_controls_grid)
    
    def _create_bass_control(self, parent):
        """Tạo Bass control với màu cam."""
        bass_frame = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#FF9800")
        # SỬ DỤNG PADDING ĐỒNG ĐỀU VÀ NHỎ HƠN
        bass_frame.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Label ở trên
        bass_label = CTK.CTkLabel(
            bass_frame,
            text="Bass",
            font=("Arial", 11, "bold"),
            text_color="#FFB74D"
        )
        bass_label.pack(pady=(4, 1))
        
        # Buttons ở dưới
        bass_inner = CTK.CTkFrame(bass_frame, fg_color="transparent")
        bass_inner.pack(pady=(1, 4))
        
        # Decrease button
        self.bass_decrease_btn = CTK.CTkButton(
            bass_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_bass_instant(-1),
            width=35,
            height=26,
            fg_color="#F57C00",
            hover_color="#E65100"
        )
        self.bass_decrease_btn.pack(side="left", padx=2)
        
        # Bass value display
        self.bass_value_label = CTK.CTkLabel(
            bass_inner,
            text="0",
            font=("Arial", 11, "bold"),
            text_color="#FFB74D",
            width=40
        )
        self.bass_value_label.pack(side="left", padx=2)
        
        # Increase button
        self.bass_increase_btn = CTK.CTkButton(
            bass_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_bass_instant(1),
            width=35,
            height=26,
            fg_color="#F57C00",
            hover_color="#E65100"
        )
        self.bass_increase_btn.pack(side="left", padx=2)
        
        # Hidden slider for internal state
        self.bass_slider = CTK.CTkSlider(bass_frame, width=0, height=0)
        self.bass_slider.configure(
            from_=self.default_values.get('bass_min', -30),
            to=self.default_values.get('bass_max', 30)
        )
        self.bass_slider.set(self.default_values.get('bass_default', 0))
    
    def _create_treble_control(self, parent):
        """Tạo Treble control với màu xanh lá."""
        treble_frame = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#4CAF50")
        # SỬ DỤNG PADDING ĐỒNG ĐỀU VÀ NHỎ HƠN
        treble_frame.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        
        # Label ở trên
        treble_label = CTK.CTkLabel(
            treble_frame,
            text="Treble",
            font=("Arial", 11, "bold"),
            text_color="#81C784"
        )
        treble_label.pack(pady=(4, 1))
        
        # Buttons ở dưới
        treble_inner = CTK.CTkFrame(treble_frame, fg_color="transparent")
        treble_inner.pack(pady=(1, 4))
        
        # Decrease button
        self.treble_decrease_btn = CTK.CTkButton(
            treble_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_treble_instant(-1),
            width=35,
            height=26,
            fg_color="#388E3C",
            hover_color="#2E7D32"
        )
        self.treble_decrease_btn.pack(side="left", padx=2)
        
        # Treble value display
        self.treble_value_label = CTK.CTkLabel(
            treble_inner,
            text="0",
            font=("Arial", 11, "bold"),
            text_color="#81C784",
            width=40
        )
        self.treble_value_label.pack(side="left", padx=2)
        
        # Increase button
        self.treble_increase_btn = CTK.CTkButton(
            treble_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_treble_instant(1),
            width=35,
            height=26,
            fg_color="#388E3C",
            hover_color="#2E7D32"
        )
        self.treble_increase_btn.pack(side="left", padx=2)
        
        # Hidden slider for internal state
        self.treble_slider = CTK.CTkSlider(treble_frame, width=0, height=0)
        self.treble_slider.configure(
            from_=self.default_values.get('treble_min', -20),
            to=self.default_values.get('treble_max', 30)
        )
        self.treble_slider.set(self.default_values.get('treble_default', 0))
    
    def _create_volume_mic_control(self, parent):
        """Tạo COMP (Volume Mic) control với màu đỏ."""
        volume_mic_frame = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#F44336")
        # SỬ DỤNG PADDING ĐỒNG ĐỀU VÀ NHỎ HƠN
        volume_mic_frame.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        
        # Label ở trên
        comp_label = CTK.CTkLabel(
            volume_mic_frame,
            text="Âm lượng Mic",
            font=("Arial", 11, "bold"),
            text_color="#EF9A9A"
        )
        comp_label.pack(pady=(4, 1))
        
        # Buttons ở dưới
        volume_mic_inner = CTK.CTkFrame(volume_mic_frame, fg_color="transparent")
        volume_mic_inner.pack(pady=(1, 4))
        
        # Decrease button
        self.volume_mic_decrease_btn = CTK.CTkButton(
            volume_mic_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_volume_mic_instant(-1),
            width=35,
            height=26,
            fg_color="#D32F2F",
            hover_color="#C62828"
        )
        self.volume_mic_decrease_btn.pack(side="left", padx=2)
        
        # COMP value display
        self.volume_mic_value_label = CTK.CTkLabel(
            volume_mic_inner,
            text="45",
            font=("Arial", 11, "bold"),
            text_color="#EF9A9A",
            width=40
        )
        self.volume_mic_value_label.pack(side="left", padx=2)
        
        # Increase button
        self.volume_mic_increase_btn = CTK.CTkButton(
            volume_mic_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_volume_mic_instant(1),
            width=35,
            height=26,
            fg_color="#D32F2F",
            hover_color="#C62828"
        )
        self.volume_mic_increase_btn.pack(side="left", padx=2)
        
        # Hidden slider for internal state
        self.volume_mic_slider = CTK.CTkSlider(volume_mic_frame, width=0, height=0)
        self.volume_mic_slider.configure(
            from_=self.default_values.get('xvox_volume_min', 30),
            to=self.default_values.get('xvox_volume_max', 60)
        )
        self.volume_mic_slider.set(self.default_values.get('xvox_volume_default', 45))
    
    def _create_reverb_control(self, parent):
        """Tạo Reverb control với màu cyan."""
        reverb_mic_frame = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#00BCD4")
        # SỬ DỤNG PADDING ĐỒNG ĐỀU VÀ NHỎ HƠN
        reverb_mic_frame.grid(row=1, column=1, sticky="nsew", padx=1, pady=1)
        
        # Label ở trên
        reverb_label = CTK.CTkLabel(
            reverb_mic_frame,
            text="Độ vang",
            font=("Arial", 11, "bold"),
            text_color="#80DEEA"
        )
        reverb_label.pack(pady=(4, 1))
        
        # Buttons ở dưới
        reverb_mic_inner = CTK.CTkFrame(reverb_mic_frame, fg_color="transparent")
        reverb_mic_inner.pack(pady=(1, 4))
        
        # Decrease button
        self.reverb_mic_decrease_btn = CTK.CTkButton(
            reverb_mic_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_reverb_mic_instant(-1),
            width=35,
            height=26,
            fg_color="#0097A7",
            hover_color="#00838F"
        )
        self.reverb_mic_decrease_btn.pack(side="left", padx=2)
        
        # Reverb value display
        self.reverb_mic_value_label = CTK.CTkLabel(
            reverb_mic_inner,
            text="36",
            font=("Arial", 11, "bold"),
            text_color="#80DEEA",
            width=40
        )
        self.reverb_mic_value_label.pack(side="left", padx=2)
        
        # Increase button
        self.reverb_mic_increase_btn = CTK.CTkButton(
            reverb_mic_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_reverb_mic_instant(1),
            width=35,
            height=26,
            fg_color="#0097A7",
            hover_color="#00838F"
        )
        self.reverb_mic_increase_btn.pack(side="left", padx=2)
        
        # Hidden slider for internal state
        self.reverb_mic_slider = CTK.CTkSlider(reverb_mic_frame, width=0, height=0)
        self.reverb_mic_slider.configure(
            from_=self.default_values.get('reverb_min', 30),
            to=self.default_values.get('reverb_max', 42)
        )
        self.reverb_mic_slider.set(self.default_values.get('reverb_default', 36))
    
    # ==================== EVENT HANDLERS ====================
    
    def _adjust_bass_instant(self, direction):
        """Điều chỉnh Bass ngay lập tức."""
        self.main_window._adjust_bass_instant(direction)
    
    def _adjust_treble_instant(self, direction):
        """Điều chỉnh Treble ngay lập tức."""
        self.main_window._adjust_treble_instant(direction)
    
    def _adjust_volume_mic_instant(self, direction):
        """Điều chỉnh COMP ngay lập tức."""
        self.main_window._adjust_volume_mic_instant(direction)
    
    def _adjust_reverb_mic_instant(self, direction):
        """Điều chỉnh Reverb ngay lập tức."""
        self.main_window._adjust_reverb_mic_instant(direction)
"""
Auto-Tune Section Component - Bao gồm tone detection, transpose, và music presets.
"""
import customtkinter as CTK
from gui.components.base_component import BaseComponent
from utils.debug_helper import DebugHelper


class AutoTuneSection(BaseComponent):
    """Component cho Auto-Tune section với tone detection, transpose và music presets."""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        
        # UI element references
        self.current_tone_label = None
        self.auto_detect_switch = None
        self.plugin_bypass_toggle = None
        self.plugin_state_label = None
        self.transpose_value_label = None
        self.btn_pitch_old = None
        self.btn_pitch_normal = None
        self.btn_pitch_young = None
        self.pitch_slider = None
        
        # Music presets references
        self.bolero_container = None
        self.bolero_level_label = None
        self.bolero_minus_btn = None
        self.bolero_plus_btn = None
        self.bolero_apply_circle = None
        self.nhac_tre_container = None
        self.nhac_tre_level_label = None
        self.nhac_tre_minus_btn = None
        self.nhac_tre_plus_btn = None
        self.nhac_tre_apply_circle = None
        
        # Track which preset is currently active
        self.active_music_preset = None
        
    def create(self):
        """Tạo Auto-Tune section với tất cả controls."""
        # Section frame - minimal padding
        self.container = CTK.CTkFrame(self.parent, corner_radius=6, border_width=1, border_color="#404040")
        
        # Header với title và toggle
        self._create_header()
        
        # Content frame - minimal
        content_frame = CTK.CTkFrame(self.container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        
        # Tone detection
        self._create_tone_detection(content_frame)
        
        # Chuyển Giọng
        self._create_transpose_controls(content_frame)
        
        # Music Presets
        self._create_music_presets(content_frame)
        
        return self.container
    
    def _create_header(self):
        """Tạo header với title và bypass toggle."""
        header_frame = CTK.CTkFrame(self.container, fg_color="#1E1E1E", corner_radius=4)
        header_frame.pack(fill="x", padx=4, pady=4)
        
        # Title
        title_label = CTK.CTkLabel(
            header_frame,
            text="Auto-Tune",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(side="left", padx=8, pady=4)
        
        # Auto-Tune Toggle (right side)
        toggle_container = CTK.CTkFrame(header_frame, fg_color="transparent")
        toggle_container.pack(side="right", padx=8)
        
        self.plugin_bypass_toggle = CTK.CTkSwitch(
            toggle_container,
            text="",
            command=lambda: self.main_window.bypass_manager.toggle_bypass('plugin'),
            width=35,
            height=18,
            fg_color="#666666",
            progress_color="#4CAF50"
        )
        self.plugin_bypass_toggle.pack(side="left", padx=(0, 5))
        
        self.plugin_state_label = CTK.CTkLabel(
            toggle_container,
            text="ON",
            font=("Arial", 9, "bold"),
            text_color="#4CAF50",
            width=25
        )
        self.plugin_state_label.pack(side="left")
    
    def _create_tone_detection(self, parent):
        """Tạo tone detection controls với màu xanh lá."""
        tone_row = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#4CAF50")
        tone_row.pack(fill="x", pady=2, padx=4)
        
        # Top row: Label + Key value
        top_row = CTK.CTkFrame(tone_row, fg_color="transparent")
        top_row.pack(fill="x", pady=(4, 2), padx=8)
        
        tone_title = CTK.CTkLabel(
            top_row,
            text="Tone Hiện Tại",
            font=("Arial", 11, "bold"),
            text_color="#81C784"
        )
        tone_title.pack(side="left", padx=(0, 4))
        
        self.current_tone_label = CTK.CTkLabel(
            top_row,
            text="--",
            font=("Arial", 14, "bold"),
            text_color="#A5D6A7",
            width=50
        )
        self.current_tone_label.pack(side="left")
        
        # Auto toggle ở bên phải
        self.auto_detect_switch = CTK.CTkSwitch(
            top_row,
            text="Tự động dò",
            command=self._toggle_auto_detect,
            width=40,
            height=18,
            font=("Arial", 10),
            fg_color="#666666",
            progress_color="#4CAF50"
        )
        self.auto_detect_switch.pack(side="right", padx=0)
        
        # Bottom row: Dò button
        btn_tone = CTK.CTkButton(
            tone_row,
            text="DÒ",
            font=("Arial", 11, "bold"),
            command=self._execute_tone_detector,
            width=80,
            height=26,
            fg_color="#388E3C",
            hover_color="#2E7D32"
        )
        btn_tone.pack(pady=(2, 4), padx=8)
        
        saved_auto_detect = self.settings_manager.get_auto_detect()
        if saved_auto_detect:
            self.auto_detect_switch.select()
        
        if saved_auto_detect:
            DebugHelper.print_init_debug("🔄 Auto-detect đã được bật từ lần trước")
            self.main_window.root.after_idle(lambda: self.main_window._start_auto_detect_from_saved_state())
    
    def _create_transpose_controls(self, parent):
        """Tạo transpose controls với màu tím."""
        transpose_frame = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#9C27B0")
        transpose_frame.pack(fill="x", pady=2, padx=4)
        
        # Label ở trên
        label = CTK.CTkLabel(
            transpose_frame, 
            text="Chuyển Giọng", 
            font=("Arial", 11, "bold"), 
            text_color="#BA68C8"
        )
        label.pack(pady=(6, 2))
        
        # Buttons ở dưới
        btn_frame = CTK.CTkFrame(transpose_frame, fg_color="transparent")
        btn_frame.pack(pady=(2, 6))
        
        self.btn_pitch_old = CTK.CTkButton(
            btn_frame,
            text="GIÀ",
            font=("Arial", 11, "bold"),
            command=self._apply_pitch_old,
            width=60,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.btn_pitch_old.pack(side="left", padx=3)
        
        self.btn_pitch_normal = CTK.CTkButton(
            btn_frame,
            text="BÌNH THƯỜNG",
            font=("Arial", 11, "bold"),
            command=self._apply_pitch_normal,
            width=120,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.btn_pitch_normal.pack(side="left", padx=3)
        
        self.btn_pitch_young = CTK.CTkButton(
            btn_frame,
            text="TRẺ",
            font=("Arial", 11, "bold"),
            command=self._apply_pitch_young,
            width=60,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.btn_pitch_young.pack(side="left", padx=3)
        
        # Ẩn label giá trị (không cần hiển thị số nữa)
        self.transpose_value_label = CTK.CTkLabel(
            btn_frame,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF",
            width=0  # Ẩn đi
        )
        # Không pack nữa - self.transpose_value_label.pack(side="left", padx=(0, 0))
        
        # Keep hidden slider for compatibility with batch reset code
        self.pitch_slider = CTK.CTkSlider(
            transpose_frame,
            from_=self.default_values.get('transpose_min', -12),
            to=self.default_values.get('transpose_max', 12),
            number_of_steps=abs(self.default_values.get('transpose_min', -12)) + abs(self.default_values.get('transpose_max', 12)),
            command=self._on_pitch_slider_change,
            width=0,
            height=0
        )
        self.pitch_slider.set(self.default_values.get('transpose_default', 0))
    
    def _create_music_presets(self, parent):
        """Tạo music presets controls."""
        presets_frame = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=4)
        presets_frame.pack(fill="x", pady=2, padx=4)
        
        content_frame = CTK.CTkFrame(presets_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Configure grid layout - 2 columns
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Bolero (Left)
        self._create_bolero_preset(content_frame)
        
        # Nhạc Trẻ (Right)
        self._create_nhac_tre_preset(content_frame)
        
        # Update initial display
        self._update_music_preset_display('bolero')
        self._update_music_preset_display('nhac_tre')
    
    def _create_bolero_preset(self, parent):
        """Tạo Bolero preset controls với màu hồng."""
        self.bolero_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#E91E63")
        self.bolero_container.grid(row=0, column=0, sticky="nsew", padx=(0, 3), pady=0)
        
        # Bind click event để apply preset khi click vào container
        self.bolero_container.bind("<Button-1>", lambda e: self._apply_preset_on_click('bolero'))
        
        # Nút apply preset với tên "Bolero" (ở trên đầu)
        self.bolero_apply_circle = CTK.CTkButton(
            self.bolero_container,
            text="Bolero",
            font=("Arial", 11, "bold"),
            command=lambda: self._apply_preset_on_click('bolero'),
            width=100,
            height=26,
            corner_radius=6,
            fg_color="#C2185B",
            hover_color="#AD1457",
            border_width=0
        )
        self.bolero_apply_circle.pack(pady=(4, 2))
        
        bolero_inner = CTK.CTkFrame(self.bolero_container, fg_color="transparent")
        bolero_inner.pack(pady=5, padx=6)
        
        # Minus button - tự động apply khi bấm
        self.bolero_minus_btn = CTK.CTkButton(
            bolero_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_and_apply_preset('bolero', -1),
            width=28,
            height=24,
            fg_color="#C2185B",
            hover_color="#AD1457"
        )
        self.bolero_minus_btn.pack(side="left", padx=(0, 3))
        
        # Level display
        self.bolero_level_label = CTK.CTkLabel(
            bolero_inner,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#F48FB1",
            width=25
        )
        self.bolero_level_label.pack(side="left", padx=(0, 3))
        
        # Plus button - tự động apply khi bấm
        self.bolero_plus_btn = CTK.CTkButton(
            bolero_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_and_apply_preset('bolero', 1),
            width=28,
            height=24,
            fg_color="#C2185B",
            hover_color="#AD1457"
        )
        self.bolero_plus_btn.pack(side="left", padx=(0, 0))
    
    def _create_nhac_tre_preset(self, parent):
        """Tạo Nhạc Trẻ preset controls với màu xanh tím/indigo."""
        self.nhac_tre_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#3F51B5")
        self.nhac_tre_container.grid(row=0, column=1, sticky="nsew", padx=(3, 0), pady=0)
        
        # Bind click event để apply preset khi click vào container
        self.nhac_tre_container.bind("<Button-1>", lambda e: self._apply_preset_on_click('nhac_tre'))
        
        # Nút apply preset với tên "Nhạc Trẻ" (ở trên đầu)
        self.nhac_tre_apply_circle = CTK.CTkButton(
            self.nhac_tre_container,
            text="Nhạc Trẻ",
            font=("Arial", 11, "bold"),
            command=lambda: self._apply_preset_on_click('nhac_tre'),
            width=100,
            height=26,
            corner_radius=6,
            fg_color="#303F9F",
            hover_color="#283593",
            border_width=0
        )
        self.nhac_tre_apply_circle.pack(pady=(4, 2))
        
        nhac_tre_inner = CTK.CTkFrame(self.nhac_tre_container, fg_color="transparent")
        nhac_tre_inner.pack(pady=5, padx=6)
        
        # Minus button - tự động apply khi bấm
        self.nhac_tre_minus_btn = CTK.CTkButton(
            nhac_tre_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_and_apply_preset('nhac_tre', -1),
            width=28,
            height=24,
            fg_color="#303F9F",
            hover_color="#283593"
        )
        self.nhac_tre_minus_btn.pack(side="left", padx=(0, 3))
        
        # Level display
        self.nhac_tre_level_label = CTK.CTkLabel(
            nhac_tre_inner,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#9FA8DA",
            width=25
        )
        self.nhac_tre_level_label.pack(side="left", padx=(0, 3))
        
        # Plus button - tự động apply khi bấm
        self.nhac_tre_plus_btn = CTK.CTkButton(
            nhac_tre_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_and_apply_preset('nhac_tre', 1),
            width=28,
            height=24,
            fg_color="#303F9F",
            hover_color="#283593"
        )
        self.nhac_tre_plus_btn.pack(side="left", padx=(0, 0))
    
    # ==================== EVENT HANDLERS ====================
    
    def _execute_tone_detector(self):
        """Execute tone detector."""
        self.main_window._execute_tone_detector()
    
    def _toggle_auto_detect(self):
        """Toggle auto-detect."""
        self.main_window._toggle_auto_detect()
    
    def _on_pitch_slider_change(self, value):
        """Callback khi pitch slider thay đổi."""
        pitch_value = int(value)
        self.transpose_value_label.configure(text=str(pitch_value))
    
    def _apply_pitch_old(self):
        """Áp dụng pitch Già."""
        self._highlight_pitch_button('old')
        self.main_window._apply_pitch_old()
    
    def _apply_pitch_normal(self):
        """Áp dụng pitch Bình thường."""
        self._highlight_pitch_button('normal')
        self.main_window._apply_pitch_normal()
    
    def _apply_pitch_young(self):
        """Áp dụng pitch Trẻ."""
        self._highlight_pitch_button('young')
        self.main_window._apply_pitch_young()
    
    def _highlight_pitch_button(self, selected):
        """Highlight nút pitch đang được chọn với màu tím."""
        default_color = "#7B1FA2"  # Tím đậm (base)
        active_color = "#BA68C8"   # Tím sáng (active)
        
        # Reset tất cả về màu base
        if self.btn_pitch_old:
            self.btn_pitch_old.configure(fg_color=default_color)
        if self.btn_pitch_normal:
            self.btn_pitch_normal.configure(fg_color=default_color)
        if self.btn_pitch_young:
            self.btn_pitch_young.configure(fg_color=default_color)
        
        # Highlight nút được chọn
        if selected == 'old' and self.btn_pitch_old:
            self.btn_pitch_old.configure(fg_color=active_color)
        elif selected == 'normal' and self.btn_pitch_normal:
            self.btn_pitch_normal.configure(fg_color=active_color)
        elif selected == 'young' and self.btn_pitch_young:
            self.btn_pitch_young.configure(fg_color=active_color)
    
    def _adjust_music_preset(self, music_type, direction):
        """Điều chỉnh music preset level."""
        self.main_window._adjust_music_preset(music_type, direction)
    
    def _apply_music_preset(self, music_type):
        """Áp dụng music preset."""
        # Highlight preset đang được apply
        self._highlight_active_preset(music_type)
        self.main_window._apply_music_preset(music_type)
    
    def _highlight_active_preset(self, active_preset):
        """Highlight preset đang được sử dụng bằng cách thay đổi màu border và nút."""
        self.active_music_preset = active_preset
        
        # Màu cho Bolero (hồng)
        bolero_default_border = "#E91E63"
        bolero_active_border = "#FF4081"  # Hồng sáng
        bolero_default_btn = "#C2185B"
        bolero_active_btn = "#FF4081"
        
        # Màu cho Nhạc Trẻ (xanh tím/indigo)
        nhac_tre_default_border = "#3F51B5"
        nhac_tre_active_border = "#5C6BC0"  # Xanh tím sáng
        nhac_tre_default_btn = "#303F9F"
        nhac_tre_active_btn = "#5C6BC0"
        
        if active_preset == 'bolero':
            if self.bolero_container:
                self.bolero_container.configure(border_color=bolero_active_border)
            if self.bolero_apply_circle:
                self.bolero_apply_circle.configure(fg_color=bolero_active_btn)
            if self.nhac_tre_container:
                self.nhac_tre_container.configure(border_color=nhac_tre_default_border)
            if self.nhac_tre_apply_circle:
                self.nhac_tre_apply_circle.configure(fg_color=nhac_tre_default_btn)
        elif active_preset == 'nhac_tre':
            if self.bolero_container:
                self.bolero_container.configure(border_color=bolero_default_border)
            if self.bolero_apply_circle:
                self.bolero_apply_circle.configure(fg_color=bolero_default_btn)
            if self.nhac_tre_container:
                self.nhac_tre_container.configure(border_color=nhac_tre_active_border)
            if self.nhac_tre_apply_circle:
                self.nhac_tre_apply_circle.configure(fg_color=nhac_tre_active_btn)
        else:
            # Reset cả hai về màu default
            if self.bolero_container:
                self.bolero_container.configure(border_color=bolero_default_border)
            if self.bolero_apply_circle:
                self.bolero_apply_circle.configure(fg_color=bolero_default_btn)
            if self.nhac_tre_container:
                self.nhac_tre_container.configure(border_color=nhac_tre_default_border)
            if self.nhac_tre_apply_circle:
                self.nhac_tre_apply_circle.configure(fg_color=nhac_tre_default_btn)
    
    def _adjust_and_apply_preset(self, music_type, direction):
        """Điều chỉnh và tự động apply preset ngay lập tức."""
        # Bước 1: Điều chỉnh level
        self.main_window._adjust_music_preset(music_type, direction)
        
        # Bước 2: Apply preset luôn
        self._highlight_active_preset(music_type)
        self.main_window._apply_music_preset(music_type)
    
    def _apply_preset_on_click(self, music_type):
        """Apply preset hiện tại khi click vào container."""
        # Nếu preset này đang active rồi thì không làm gì
        if self.active_music_preset == music_type:
            return
        
        # Highlight preset này là active
        self._highlight_active_preset(music_type)
        
        # Apply preset với level hiện tại
        self.main_window._apply_music_preset(music_type)
    
    def _update_music_preset_display(self, music_type):
        """Cập nhật hiển thị music preset level."""
        try:
            music_presets_manager = self.main_window.music_presets_manager
            current_level = music_presets_manager.get_current_level(music_type)
            level_str = music_presets_manager.get_level_string(current_level)
            
            display_text = str(level_str)
            
            if music_type == 'bolero' and self.bolero_level_label:
                self.bolero_level_label.configure(text=display_text)
            elif music_type == 'nhac_tre' and self.nhac_tre_level_label:
                self.nhac_tre_level_label.configure(text=display_text)
                
        except Exception as e:
            print(f"❌ Error updating {music_type} display: {e}")
    
    def update_current_tone(self, tone_text):
        """Cập nhật hiển thị tone hiện tại."""
        if self.current_tone_label:
            self.current_tone_label.configure(text=tone_text)
    
    def update_transpose_value(self, value):
        """Cập nhật hiển thị transpose value và highlight button tương ứng."""
        if self.transpose_value_label:
            self.transpose_value_label.configure(text=str(value))
        
        # Highlight button tương ứng với giá trị
        if value < 0:
            self._highlight_pitch_button('old')
        elif value == 0:
            self._highlight_pitch_button('normal')
        else:  # value > 0
            self._highlight_pitch_button('young')


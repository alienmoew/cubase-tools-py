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
        self.bolero_level_label = None
        self.bolero_minus_btn = None
        self.bolero_plus_btn = None
        self.bolero_apply_btn = None
        self.nhac_tre_level_label = None
        self.nhac_tre_minus_btn = None
        self.nhac_tre_plus_btn = None
        self.nhac_tre_apply_btn = None
        
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
            font=("Arial", 11, "bold"),
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
        """Tạo tone detection controls."""
        tone_row = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=4)
        tone_row.pack(fill="x", pady=2, padx=4)
        
        tone_info = CTK.CTkFrame(tone_row, fg_color="transparent")
        tone_info.pack(fill="x", padx=6, pady=6)
        
        # Tone hiện tại label
        tone_label = CTK.CTkLabel(
            tone_info,
            text="Tone hiện tại:",
            font=("Arial", 10),
            text_color="#AAAAAA",
            width=85
        )
        tone_label.pack(side="left")
        
        # Current Tone value
        self.current_tone_label = CTK.CTkLabel(
            tone_info,
            text="--",
            font=("Arial", 12, "bold"),
            text_color="#4CAF50",
            width=35
        )
        self.current_tone_label.pack(side="left")
        
        # Dò button
        btn_tone = CTK.CTkButton(
            tone_info,
            text="DÒ",
            font=("Arial", 10, "bold"),
            command=self._execute_tone_detector,
            width=40,
            height=24,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        btn_tone.pack(side="left", padx=(8, 0))
        
        # Auto toggle
        self.auto_detect_switch = CTK.CTkSwitch(
            tone_info,
            text="Tự động dò",
            command=self._toggle_auto_detect,
            width=40,
            height=18,
            font=("Arial", 10),
            fg_color="#666666",
            progress_color="#4CAF50"
        )
        
        saved_auto_detect = self.settings_manager.get_auto_detect()
        if saved_auto_detect:
            self.auto_detect_switch.select()
        
        self.auto_detect_switch.pack(side="right")
        
        if saved_auto_detect:
            DebugHelper.print_init_debug("🔄 Auto-detect đã được bật từ lần trước")
            self.main_window.root.after_idle(lambda: self.main_window._start_auto_detect_from_saved_state())
    
    def _create_transpose_controls(self, parent):
        """Tạo transpose controls."""
        transpose_frame = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=4)
        transpose_frame.pack(fill="x", pady=2, padx=4)
        
        transpose_inner = CTK.CTkFrame(transpose_frame, fg_color="transparent")
        transpose_inner.pack(pady=6, padx=6, fill="x")
        
        # Label
        label = CTK.CTkLabel(transpose_inner, text="Chuyển Giọng", font=("Arial", 10), text_color="#AAAAAA")
        label.pack(side="left")
        
        # Buttons right side
        btn_frame = CTK.CTkFrame(transpose_inner, fg_color="transparent")
        btn_frame.pack(side="right")
        
        self.btn_pitch_old = CTK.CTkButton(
            btn_frame,
            text="GIÀ",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_old,
            width=45,
            height=24,
            fg_color="#757575",
            hover_color="#616161"
        )
        self.btn_pitch_old.pack(side="left", padx=(0, 3))
        
        self.btn_pitch_normal = CTK.CTkButton(
            btn_frame,
            text="0",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_normal,
            width=35,
            height=24,
            fg_color="#757575",
            hover_color="#616161"
        )
        self.btn_pitch_normal.pack(side="left", padx=(0, 3))
        
        self.btn_pitch_young = CTK.CTkButton(
            btn_frame,
            text="TRẺ",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_young,
            width=45,
            height=24,
            fg_color="#757575",
            hover_color="#616161"
        )
        self.btn_pitch_young.pack(side="left", padx=(0, 8))
        
        self.transpose_value_label = CTK.CTkLabel(
            btn_frame,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF",
            width=30
        )
        self.transpose_value_label.pack(side="left", padx=(0, 0))
        
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
        """Tạo Bolero preset controls."""
        bolero_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4)
        bolero_container.grid(row=0, column=0, sticky="nsew", padx=(0, 3), pady=0)
        
        bolero_inner = CTK.CTkFrame(bolero_container, fg_color="transparent")
        bolero_inner.pack(pady=5, padx=6)
        
        # Title
        bolero_title = CTK.CTkLabel(
            bolero_inner,
            text="Bolero",
            font=("Arial", 10),
            text_color="#AAAAAA"
        )
        bolero_title.pack(side="left", padx=(0, 5))
        
        # Minus button
        self.bolero_minus_btn = CTK.CTkButton(
            bolero_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_music_preset('bolero', -1),
            width=28,
            height=24,
            fg_color="#EF6C00",
            hover_color="#E65100"
        )
        self.bolero_minus_btn.pack(side="left", padx=(0, 3))
        
        # Level display
        self.bolero_level_label = CTK.CTkLabel(
            bolero_inner,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF",
            width=25
        )
        self.bolero_level_label.pack(side="left", padx=(0, 3))
        
        # Plus button
        self.bolero_plus_btn = CTK.CTkButton(
            bolero_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_music_preset('bolero', 1),
            width=28,
            height=24,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.bolero_plus_btn.pack(side="left", padx=(0, 5))
        
        # Apply button
        self.bolero_apply_btn = CTK.CTkButton(
            bolero_inner,
            text="OK",
            font=("Arial", 9, "bold"),
            command=lambda: self._apply_music_preset('bolero'),
            width=32,
            height=24,
            fg_color="#757575",
            hover_color="#616161"
        )
        self.bolero_apply_btn.pack(side="left")
    
    def _create_nhac_tre_preset(self, parent):
        """Tạo Nhạc Trẻ preset controls."""
        nhac_tre_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4)
        nhac_tre_container.grid(row=0, column=1, sticky="nsew", padx=(3, 0), pady=0)
        
        nhac_tre_inner = CTK.CTkFrame(nhac_tre_container, fg_color="transparent")
        nhac_tre_inner.pack(pady=5, padx=6)
        
        # Title
        nhac_tre_title = CTK.CTkLabel(
            nhac_tre_inner,
            text="Nhạc Trẻ",
            font=("Arial", 10),
            text_color="#AAAAAA"
        )
        nhac_tre_title.pack(side="left", padx=(0, 5))
        
        # Minus button
        self.nhac_tre_minus_btn = CTK.CTkButton(
            nhac_tre_inner,
            text="-",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_music_preset('nhac_tre', -1),
            width=28,
            height=24,
            fg_color="#EF6C00",
            hover_color="#E65100"
        )
        self.nhac_tre_minus_btn.pack(side="left", padx=(0, 3))
        
        # Level display
        self.nhac_tre_level_label = CTK.CTkLabel(
            nhac_tre_inner,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF",
            width=25
        )
        self.nhac_tre_level_label.pack(side="left", padx=(0, 3))
        
        # Plus button
        self.nhac_tre_plus_btn = CTK.CTkButton(
            nhac_tre_inner,
            text="+",
            font=("Arial", 12, "bold"),
            command=lambda: self._adjust_music_preset('nhac_tre', 1),
            width=28,
            height=24,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.nhac_tre_plus_btn.pack(side="left", padx=(0, 5))
        
        # Apply button
        self.nhac_tre_apply_btn = CTK.CTkButton(
            nhac_tre_inner,
            text="OK",
            font=("Arial", 9, "bold"),
            command=lambda: self._apply_music_preset('nhac_tre'),
            width=32,
            height=24,
            fg_color="#757575",
            hover_color="#616161"
        )
        self.nhac_tre_apply_btn.pack(side="left")
    
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
        self.main_window._apply_pitch_old()
    
    def _apply_pitch_normal(self):
        """Áp dụng pitch Bình thường."""
        self.main_window._apply_pitch_normal()
    
    def _apply_pitch_young(self):
        """Áp dụng pitch Trẻ."""
        self.main_window._apply_pitch_young()
    
    def _adjust_music_preset(self, music_type, direction):
        """Điều chỉnh music preset level."""
        self.main_window._adjust_music_preset(music_type, direction)
    
    def _apply_music_preset(self, music_type):
        """Áp dụng music preset."""
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
        """Cập nhật hiển thị transpose value."""
        if self.transpose_value_label:
            self.transpose_value_label.configure(text=str(value))


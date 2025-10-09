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
        
        # Label ở bên trái với dấu hai chấm
        tone_title = CTK.CTkLabel(
            top_row,
            text="Tone hiện tại:",
            font=("Arial", 11, "bold"),
            text_color="#81C784"
        )
        tone_title.pack(side="left", padx=(0, 4))
        
        # Giá trị Key ở bên phải label
        self.current_tone_label = CTK.CTkLabel(
            top_row,
            text="--",
            font=("Arial", 14, "bold"),
            text_color="#EF5350",
            width=50
        )
        self.current_tone_label.pack(side="left")
        
        # Bottom row: Dò tone button (left) + Tự động dò switch (right)
        bottom_row = CTK.CTkFrame(tone_row, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(2, 4), padx=8)
        
        # Dò tone button ở bên trái
        btn_tone = CTK.CTkButton(
            bottom_row,
            text="Dò tone",
            font=("Arial", 11, "bold"),
            command=self._execute_tone_detector,
            width=80,
            height=26,
            fg_color="#388E3C",
            hover_color="#2E7D32"
        )
        btn_tone.pack(side="left", padx=0)
        
        # Tự động dò switch ở bên phải với text
        self.auto_detect_switch = CTK.CTkSwitch(
            bottom_row,
            text="Tự động dò",
            command=self._toggle_auto_detect,
            width=40,
            height=18,
            font=("Arial", 10),
            fg_color="#666666",
            progress_color="#4CAF50"
        )
        self.auto_detect_switch.pack(side="right", padx=0)
        
        saved_auto_detect = self.settings_manager.get_auto_detect()
        if saved_auto_detect:
            self.auto_detect_switch.select()
        
        if saved_auto_detect:
            DebugHelper.print_init_debug("🔄 Auto-detect đã được bật từ lần trước")
            self.main_window.root.after_idle(lambda: self.main_window._start_auto_detect_from_saved_state())   
    
    def _create_music_presets(self, parent):
        """Tạo music presets controls với bố cục dọc."""
        presets_frame = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=4)
        presets_frame.pack(fill="x", pady=2, padx=4)
        
        # Bolero (Trên)
        self._create_bolero_preset(presets_frame)
        
        # Nhạc Trẻ (Dưới)
        self._create_nhac_tre_preset(presets_frame)
        
        # Update initial display
        self._update_music_preset_display('bolero')
        self._update_music_preset_display('nhac_tre')
        # Reset highlight ban đầu
        self._highlight_active_preset(None)
    
    def _create_preset_base(self, parent, preset_name, border_color, music_type):
        """Hàm tạo preset cơ bản để tái sử dụng code."""
        container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color=border_color)
        container.pack(fill="x", pady=(0, 3), padx=6)
        
        # Bind click event để apply preset khi click vào container
        container.bind("<Button-1>", lambda e: self._apply_preset_on_click(music_type))
        
        # Header frame với title và level display
        header_frame = CTK.CTkFrame(container, fg_color="transparent")
        header_frame.pack(pady=(4, 2), padx=6, fill="x")
        
        # Nút apply preset với tên preset (bên trái)
        apply_circle = CTK.CTkButton(
            header_frame,
            text=preset_name,
            font=("Arial", 11, "bold"),
            command=lambda: self._apply_preset_on_click(music_type),
            width=70,
            height=26,
            corner_radius=6,
            fg_color="#303F9F",
            hover_color="#283593",
            border_width=0
        )
        apply_circle.pack(side="left")
        
        # Level display (bên phải)
        level_label = CTK.CTkLabel(
            header_frame,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#9FA8DA",
            width=25
        )
        level_label.pack(side="right")
        
        # Button frame với các nút điều khiển
        button_frame = CTK.CTkFrame(container, fg_color="transparent")
        button_frame.pack(pady=(0, 5), padx=6)
        
        # Giảm button
        minus_btn = CTK.CTkButton(
            button_frame,
            text="Giảm",
            font=("Arial", 10, "bold"),
            command=lambda: self._adjust_and_apply_preset(music_type, -1),
            width=45,
            height=24,
            fg_color="#303F9F",
            hover_color="#283593"
        )
        minus_btn.pack(side="left", padx=(0, 3))
        
        # Bình thường button
        normal_btn = CTK.CTkButton(
            button_frame,
            text="Bình thường",
            font=("Arial", 10, "bold"),
            command=lambda: self._reset_preset_level(music_type),
            width=75,
            height=24,
            fg_color="#303F9F",
            hover_color="#283593"
        )
        normal_btn.pack(side="left", padx=(0, 3))
        
        # Tăng button
        plus_btn = CTK.CTkButton(
            button_frame,
            text="Tăng",
            font=("Arial", 10, "bold"),
            command=lambda: self._adjust_and_apply_preset(music_type, 1),
            width=45,
            height=24,
            fg_color="#303F9F",
            hover_color="#283593"
        )
        plus_btn.pack(side="left")
        
        return container, level_label, minus_btn, normal_btn, plus_btn, apply_circle
    
    def _create_bolero_preset(self, parent):
        """Tạo Bolero preset controls với màu hồng."""
        self.bolero_container, self.bolero_level_label, self.bolero_minus_btn, self.bolero_normal_btn, self.bolero_plus_btn, self.bolero_apply_circle = self._create_preset_base(
            parent, "Bolero", "#E91E63", "bolero")
    
    def _create_nhac_tre_preset(self, parent):
        """Tạo Nhạc Trẻ preset controls với màu xanh tím/indigo."""
        self.nhac_tre_container, self.nhac_tre_level_label, self.nhac_tre_minus_btn, self.nhac_tre_normal_btn, self.nhac_tre_plus_btn, self.nhac_tre_apply_circle = self._create_preset_base(
            parent, "Nhạc Trẻ", "#3F51B5", "nhac_tre")
    
    # ==================== EVENT HANDLERS ====================
    def _reset_preset_level(self, music_type):
        """Reset preset level về 0 và áp dụng lại."""
        # 1. Đặt lại level của loại nhạc được chọn về 0
        self.main_window.music_presets_manager.current_levels[music_type] = 0
        
        # 2. Cập nhật lại giao diện để hiển thị level "0"
        self._update_music_preset_display(music_type)
        
        # 3. Áp dụng preset ở level 0 (level "Bình thường")
        self._apply_preset_on_click(music_type)
    
    def _execute_tone_detector(self):
        """Execute tone detector."""
        self.main_window._execute_tone_detector()
    
    def _toggle_auto_detect(self):
        """Toggle auto-detect."""
        self.main_window._toggle_auto_detect()
    
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
        bolero_active_border = "#F48FB1"  # Hồng sáng
        bolero_default_btn = "#303F9F"
        bolero_active_btn = "#F48FB1"
        
        # Màu cho Nhạc Trẻ (xanh tím/indigo)
        nhac_tre_default_border = "#3F51B5"
        nhac_tre_active_border = "#7986CB"  # Xanh tím sáng
        nhac_tre_default_btn = "#303F9F"
        nhac_tre_active_btn = "#7986CB"
        
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
            
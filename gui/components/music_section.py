"""
Music Section Component - Tone nhạc và volume controls.
"""
import customtkinter as CTK
from gui.components.base_component import BaseComponent


class MusicSection(BaseComponent):
    """Component cho Music section với tone adjustment và volume controls."""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        
        # UI element references
        self.soundshifter_bypass_toggle = None
        self.soundshifter_bypass_status_label = None
        self.soundshifter_value_label = None
        self.volume_slider = None
        self.volume_value_label = None
        self.volume_apply_btn = None
        self.mute_toggle_btn = None
        
    def create(self):
        """Tạo Music section với tất cả controls."""
        # Section frame - minimal
        self.container = CTK.CTkFrame(self.parent, corner_radius=6, border_width=1, border_color="#404040")
        
        # Header với title và toggle
        self._create_header()
        
        # Content frame - minimal
        content_frame = CTK.CTkFrame(self.container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        
        # Tone nhạc controls
        self._create_tone_controls(content_frame)
        
        # Volume controls
        self._create_volume_controls(content_frame)
        
        return self.container
    
    def _create_header(self):
        """Tạo header với title và bypass toggle."""
        header_frame = CTK.CTkFrame(self.container, fg_color="#1E1E1E", corner_radius=4)
        header_frame.pack(fill="x", padx=4, pady=4)
        
        # Title
        title_label = CTK.CTkLabel(
            header_frame,
            text="Nhạc",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(side="left", padx=8, pady=4)
        
        # SoundShifter Toggle (right side)
        toggle_container = CTK.CTkFrame(header_frame, fg_color="transparent")
        toggle_container.pack(side="right", padx=8)
        
        self.soundshifter_bypass_toggle = CTK.CTkSwitch(
            toggle_container,
            text="",
            command=lambda: self.main_window.bypass_manager.toggle_bypass('soundshifter'),
            width=35,
            height=18,
            fg_color="#666666",
            progress_color="#4CAF50"
        )
        self.soundshifter_bypass_toggle.pack(side="left", padx=(0, 5))
        
        self.soundshifter_bypass_status_label = CTK.CTkLabel(
            toggle_container,
            text="SoundShifter",
            font=("Arial", 11, "bold"),
            text_color="#4CAF50",
            width=50
        )
        self.soundshifter_bypass_status_label.pack(side="left")
    
    def _create_tone_controls(self, parent):
        """Tạo tone nhạc controls với màu xanh dương."""
        tone_nhac_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#2196F3")
        tone_nhac_container.pack(fill="x", pady=2, padx=4)
        
        # Label ở trên
        label = CTK.CTkLabel(
            tone_nhac_container, 
            text="Tone Nhạc", 
            font=("Arial", 11, "bold"), 
            text_color="#64B5F6"
        )
        label.pack(pady=(4, 1))
        
        # Buttons ở dưới
        btn_frame = CTK.CTkFrame(tone_nhac_container, fg_color="transparent")
        btn_frame.pack(pady=(1, 4))
        
        btn_lower = CTK.CTkButton(
            btn_frame,
            text="-",
            font=("Arial", 12, "bold"),
            command=self._lower_tone,
            width=35,
            height=26,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        btn_lower.pack(side="left", padx=2)
        
        btn_reset = CTK.CTkButton(
            btn_frame,
            text="0",
            font=("Arial", 12, "bold"),
            command=self._reset_soundshifter,
            width=35,
            height=26,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        btn_reset.pack(side="left", padx=2)
        
        btn_raise = CTK.CTkButton(
            btn_frame,
            text="+",
            font=("Arial", 12, "bold"),
            command=self._raise_tone,
            width=35,
            height=26,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        btn_raise.pack(side="left", padx=2)
        
        self.soundshifter_value_label = CTK.CTkLabel(
            btn_frame,
            text="0 Tone",
            font=("Arial", 11, "bold"),
            text_color="#64B5F6",
            width=60
        )
        self.soundshifter_value_label.pack(side="left", padx=(8, 0))
    
    def _create_volume_controls(self, parent):
        """Tạo volume controls với màu tím."""
        volume_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#9C27B0")
        volume_container.pack(fill="x", pady=2, padx=4)
        
        # Label ở trên
        vol_label = CTK.CTkLabel(
            volume_container, 
            text="Âm lượng nhạc", 
            font=("Arial", 11, "bold"), 
            text_color="#BA68C8"
        )
        vol_label.pack(pady=(4, 1))
        
        # Buttons ở dưới
        btn_frame = CTK.CTkFrame(volume_container, fg_color="transparent")
        btn_frame.pack(pady=(1, 4))
        
        # Decrease button
        btn_decrease = CTK.CTkButton(
            btn_frame,
            text="-",
            font=("Arial", 13, "bold"),
            command=self._decrease_volume,
            width=35,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        btn_decrease.pack(side="left", padx=2)
        
        # Value display (phần trăm)
        self.volume_value_label = CTK.CTkLabel(
            btn_frame,
            text="0%",
            font=("Arial", 11, "bold"),
            text_color="#BA68C8",
            width=50
        )
        self.volume_value_label.pack(side="left", padx=2)
        
        # Increase button
        btn_increase = CTK.CTkButton(
            btn_frame,
            text="+",
            font=("Arial", 13, "bold"),
            command=self._increase_volume,
            width=35,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        btn_increase.pack(side="left", padx=2)
        
        # Mute toggle
        self.mute_toggle_btn = CTK.CTkButton(
            btn_frame,
            text="🔇",
            font=("Arial", 12),
            command=self._toggle_mute,
            width=35,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.mute_toggle_btn.pack(side="left", padx=2)
        
        # Hidden slider for compatibility (không hiển thị)
        self.volume_slider = CTK.CTkSlider(
            volume_container,
            from_=0,
            to=100,
            number_of_steps=100,
            width=0,  # Ẩn đi
            height=0
        )
        self.volume_slider.set(0)
        
        # Remove old apply button reference
        self.volume_apply_btn = None
    
    # ==================== EVENT HANDLERS ====================
    
    def _lower_tone(self):
        """Hạ tone nhạc."""
        self.main_window._lower_tone()
    
    def _raise_tone(self):
        """Tăng tone nhạc."""
        self.main_window._raise_tone()
    
    def _reset_soundshifter(self):
        """Reset soundshifter về 0."""
        self.main_window._reset_soundshifter()
    
    def _increase_volume(self):
        """Tăng volume."""
        self.main_window._increase_system_volume()
    
    def _decrease_volume(self):
        """Giảm volume."""
        self.main_window._decrease_system_volume()
    
    def _toggle_mute(self):
        """Toggle mute."""
        self.main_window._toggle_system_mute()
    
    def update_soundshifter_display(self, value):
        """Cập nhật hiển thị soundshifter value theo tone (±2 value = ±1 tone)."""
        if self.soundshifter_value_label:
            # Chuyển đổi value sang tone: mỗi 2 value = 1 tone
            tone = value / 2.0
            
            # Format hiển thị
            if tone == 0:
                display = "0 Tone"
            elif tone > 0:
                display = f"+{tone:.1f} Tone" if tone % 1 != 0 else f"+{int(tone)} Tone"
            else:
                display = f"{tone:.1f} Tone" if tone % 1 != 0 else f"{int(tone)} Tone"
            
            self.soundshifter_value_label.configure(text=display)


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
        header_frame = CTK.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(5, 3))
        
        # Title
        title_label = CTK.CTkLabel(
            header_frame,
            text="Nhạc",
            font=("Arial", 11, "bold"),
            text_color="#FF6B6B"
        )
        title_label.pack(side="left")
        
        # SoundShifter Toggle (right side)
        toggle_container = CTK.CTkFrame(header_frame, fg_color="transparent")
        toggle_container.pack(side="right")
        
        self.soundshifter_bypass_toggle = CTK.CTkSwitch(
            toggle_container,
            text="",
            command=lambda: self.main_window.bypass_manager.toggle_bypass('soundshifter'),
            width=35,
            height=18,
            fg_color="#FF4444",
            progress_color="#44FF44"
        )
        self.soundshifter_bypass_toggle.pack(side="left", padx=(0, 3))
        
        self.soundshifter_bypass_status_label = CTK.CTkLabel(
            toggle_container,
            text="ON",
            font=("Arial", 8, "bold"),
            text_color="#44FF44",
            width=25
        )
        self.soundshifter_bypass_status_label.pack(side="left")
    
    def _create_tone_controls(self, parent):
        """Tạo tone nhạc controls."""
        tone_nhac_container = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=4)
        tone_nhac_container.pack(fill="x", pady=(0, 2))
        
        tone_nhac_inner = CTK.CTkFrame(tone_nhac_container, fg_color="transparent")
        tone_nhac_inner.pack(pady=4, padx=4, fill="x")
        
        # Label
        label = CTK.CTkLabel(tone_nhac_inner, text="Tone Nhạc", font=("Arial", 9))
        label.pack(side="left")
        
        # Buttons right side
        btn_frame = CTK.CTkFrame(tone_nhac_inner, fg_color="transparent")
        btn_frame.pack(side="right")
        
        btn_lower = CTK.CTkButton(
            btn_frame,
            text="-",
            font=("Arial", 12, "bold"),
            command=self._lower_tone,
            width=30,
            height=22,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        btn_lower.pack(side="left", padx=(0, 2))
        
        btn_reset = CTK.CTkButton(
            btn_frame,
            text="0",
            font=("Arial", 10, "bold"),
            command=self._reset_soundshifter,
            width=30,
            height=22,
            fg_color="#9E9E9E",
            hover_color="#757575"
        )
        btn_reset.pack(side="left", padx=(0, 2))
        
        btn_raise = CTK.CTkButton(
            btn_frame,
            text="+",
            font=("Arial", 12, "bold"),
            command=self._raise_tone,
            width=30,
            height=22,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        btn_raise.pack(side="left", padx=(0, 3))
        
        self.soundshifter_value_label = CTK.CTkLabel(
            btn_frame,
            text="0",
            font=("Arial", 9, "bold"),
            text_color="#FFFFFF",
            width=25
        )
        self.soundshifter_value_label.pack(side="left", padx=(3, 0))
    
    def _create_volume_controls(self, parent):
        """Tạo volume controls."""
        volume_container = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=4)
        volume_container.pack(fill="x", pady=(0, 2))
        
        volume_inner = CTK.CTkFrame(volume_container, fg_color="transparent")
        volume_inner.pack(pady=4, padx=4, fill="x")
        
        # Volume label
        vol_label = CTK.CTkLabel(volume_inner, text="Volume", font=("Arial", 9))
        vol_label.pack(side="left", padx=(0, 5))
        
        # Decrease button
        btn_decrease = CTK.CTkButton(
            volume_inner,
            text="-",
            font=("Arial", 10, "bold"),
            command=self._decrease_volume,
            width=25,
            height=22,
            fg_color="#FF9800",
            hover_color="#F57C00",
            text_color="#000000"
        )
        btn_decrease.pack(side="left", padx=(0, 3))
        
        # Value display (phần trăm)
        self.volume_value_label = CTK.CTkLabel(
            volume_inner,
            text="0%",
            font=("Arial", 9, "bold"),
            text_color="#FFFFFF",
            width=40
        )
        self.volume_value_label.pack(side="left", padx=3)
        
        # Increase button
        btn_increase = CTK.CTkButton(
            volume_inner,
            text="+",
            font=("Arial", 10, "bold"),
            command=self._increase_volume,
            width=25,
            height=22,
            fg_color="#FF9800",
            hover_color="#F57C00",
            text_color="#000000"
        )
        btn_increase.pack(side="left", padx=(3, 5))
        
        # Mute toggle
        self.mute_toggle_btn = CTK.CTkButton(
            volume_inner,
            text="🔇",
            font=("Arial", 9),
            command=self._toggle_mute,
            width=30,
            height=22,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.mute_toggle_btn.pack(side="left", padx=(5, 0))
        
        # Hidden slider for compatibility (không hiển thị)
        self.volume_slider = CTK.CTkSlider(
            volume_inner,
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
        """Cập nhật hiển thị soundshifter value."""
        if self.soundshifter_value_label:
            self.soundshifter_value_label.configure(text=str(value))


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
        # Transpose controls
        self.transpose_value_label = None
        self.btn_pitch_old = None
        self.btn_pitch_normal = None
        self.btn_pitch_young = None
        self.pitch_slider = None
        
        # Lưu trạng thái tắt tiếng locally để đồng bộ hóa tốt hơn
        self.is_muted = False
        
    def create(self):
        """Tạo Music section với tất cả controls."""
        # Section frame - minimal
        self.container = CTK.CTkFrame(self.parent, corner_radius=6, border_width=1, border_color="#404040")
        
        # Header với title và toggle
        self._create_header()
        
        # Content frame - minimal
        content_frame = CTK.CTkFrame(self.container, fg_color="transparent")
        # GIẢM PADDING
        content_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        
        # Volume controls (Đưa lên trên cùng)
        self._create_volume_controls(content_frame)
        
        # Tone nhạc controls (Ở giữa)
        self._create_tone_controls(content_frame)
        
        # Transpose controls (Ở dưới cùng)
        self._create_transpose_controls(content_frame)  
        
        # Thiết lập trạng thái ban đầu cho nút tắt tiếng
        # Cố gắng lấy trạng thái từ main_window, nếu không có thì mặc định là False
        try:
            self.is_muted = self.main_window.is_system_muted()
        except AttributeError:
            self.is_muted = False
        
        # Cập nhật giao diện nút tắt tiếng dựa trên trạng thái ban đầu
        self.update_mute_display(self.is_muted)
            
        return self.container
    
    def _create_header(self):
        """Tạo header với title và bypass toggle."""
        header_frame = CTK.CTkFrame(self.container, fg_color="#1E1E1E", corner_radius=4)
        # GIẢM PADDING
        header_frame.pack(fill="x", padx=3, pady=3)
        
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
    
    def _create_volume_controls(self, parent):
        """Tạo volume controls với màu tím."""
        volume_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#9C27B0")
        # GIẢM PADDING
        volume_container.pack(fill="x", pady=1, padx=2)
        
        # Label ở trên
        vol_label = CTK.CTkLabel(
            volume_container, 
            text="Âm lượng nhạc", 
            font=("Arial", 11, "bold"), 
            text_color="#BA68C8"
        )
        # GIẢM PADDING
        vol_label.pack(pady=(3, 1))
        
        # Buttons ở dưới
        btn_frame = CTK.CTkFrame(volume_container, fg_color="transparent")
        # GIẢM PADDING
        btn_frame.pack(pady=(1, 3))
        
        # Decrease button
        btn_decrease = CTK.CTkButton(
            btn_frame,
            text="Giảm",
            font=("Arial", 10, "bold"),
            command=self._decrease_volume,
            width=50,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        btn_decrease.pack(side="left", padx=2)
        
        # Mute toggle
        self.mute_toggle_btn = CTK.CTkButton(
            btn_frame,
            text="Tắt",
            font=("Arial", 10, "bold"),
            command=self._toggle_mute,
            width=55,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.mute_toggle_btn.pack(side="left", padx=2)
        
        # Increase button
        btn_increase = CTK.CTkButton(
            btn_frame,
            text="Tăng",
            font=("Arial", 10, "bold"),
            command=self._increase_volume,
            width=50,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        btn_increase.pack(side="left", padx=2)
        
        # Value display (hiển thị phần trăm)
        self.volume_value_label = CTK.CTkLabel(
            btn_frame,
            text="0%",
            font=("Arial", 11, "bold"),
            text_color="#BA68C8",
            width=50
        )
        self.volume_value_label.pack(side="left", padx=(8, 0))
        
        # Hidden slider for compatibility
        self.volume_slider = CTK.CTkSlider(
            volume_container,
            from_=0,
            to=100,
            number_of_steps=100,
            width=0,
            height=0
        )
        self.volume_slider.set(0)
    
    def _create_tone_controls(self, parent):
        """Tạo tone nhạc controls với màu xanh dương."""
        tone_nhac_container = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#2196F3")
        # GIẢM PADDING
        tone_nhac_container.pack(fill="x", pady=1, padx=2)
        
        # Label ở trên
        label = CTK.CTkLabel(
            tone_nhac_container, 
            text="Tone Nhạc", 
            font=("Arial", 11, "bold"), 
            text_color="#64B5F6"
        )
        # GIẢM PADDING
        label.pack(pady=(3, 1))
        
        # Buttons ở dưới
        btn_frame = CTK.CTkFrame(tone_nhac_container, fg_color="transparent")
        # GIẢM PADDING
        btn_frame.pack(pady=(1, 3))
        
        btn_lower = CTK.CTkButton(
            btn_frame,
            text="Giảm",
            font=("Arial", 10, "bold"),
            command=self._lower_tone,
            width=50,
            height=26,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        btn_lower.pack(side="left", padx=2)
        
        # Thêm nút Bình thường
        btn_normal = CTK.CTkButton(
            btn_frame,
            text="Bình thường",
            font=("Arial", 10, "bold"),
            command=self._reset_soundshifter,
            width=75,
            height=26,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        btn_normal.pack(side="left", padx=2)
        
        btn_raise = CTK.CTkButton(
            btn_frame,
            text="Tăng",
            font=("Arial", 10, "bold"),
            command=self._raise_tone,
            width=50,
            height=26,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        btn_raise.pack(side="left", padx=2)
        
        # Soundshifter value display (hiển thị giá trị tone)
        self.soundshifter_value_label = CTK.CTkLabel(
            btn_frame,
            text="0 Tone",
            font=("Arial", 11, "bold"),
            text_color="#64B5F6",
            width=70
        )
        self.soundshifter_value_label.pack(side="left", padx=(8, 0))
        
    def _create_transpose_controls(self, parent):
        """Tạo transpose controls với màu tím."""
        transpose_frame = CTK.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=4, border_width=2, border_color="#9C27B0")
        # GIẢM PADDING
        transpose_frame.pack(fill="x", pady=1, padx=2)
        
        # Label ở trên
        label = CTK.CTkLabel(
            transpose_frame, 
            text="Chuyển Giọng", 
            font=("Arial", 11, "bold"), 
            text_color="#BA68C8"
        )
        # GIẢM PADDING
        label.pack(pady=(3, 1))
        
        # Buttons ở dưới
        btn_frame = CTK.CTkFrame(transpose_frame, fg_color="transparent")
        # GIẢM PADDING
        btn_frame.pack(pady=(1, 3))
        
        self.btn_pitch_old = CTK.CTkButton(
            btn_frame,
            text="Người Già",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_old,
            width=60,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.btn_pitch_old.pack(side="left", padx=2)
        
        self.btn_pitch_normal = CTK.CTkButton(
            btn_frame,
            text="Bình Thường",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_normal,
            width=75,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.btn_pitch_normal.pack(side="left", padx=2)
        
        self.btn_pitch_young = CTK.CTkButton(
            btn_frame,
            text="Trẻ Em",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_young,
            width=60,
            height=26,
            fg_color="#7B1FA2",
            hover_color="#6A1B9A"
        )
        self.btn_pitch_young.pack(side="left", padx=2)
        
        # Ẩn label giá trị (không cần hiển thị số nữa)
        self.transpose_value_label = CTK.CTkLabel(
            btn_frame,
            text="0",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF",
            width=0  # Ẩn đi
        )
        
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
        """Toggle mute với logic đã được sửa lỗi."""
        # 1. Đảo ngược trạng thái local
        self.is_muted = not self.is_muted
        
        # 2. Cập nhật giao diện ngay lập tức để phản hồi tức thì
        self.update_mute_display(self.is_muted)
        
        # 3. Gọi hàm của main_window để thực hiện hành động
        self.main_window._toggle_system_mute()

    def update_mute_display(self, is_muted):
        """
        Cập nhật hiển thị của nút mute.
        Logic: Nếu đang tắt tiếng (is_muted=True), nút hiển thị "Bật" để bật lại.
        Nếu đang có tiếng (is_muted=False), nút hiển thị "Tắt" để tắt đi.
        """
        if self.mute_toggle_btn:
            self.mute_toggle_btn.configure(text="Bật" if is_muted else "Tắt")
    
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
    
    def update_volume_display(self, value):
        """Cập nhật hiển thị volume value theo phần trăm."""
        if self.volume_value_label:
            self.volume_value_label.configure(text=f"{value}%")
            
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
        active_color = "#F72585"   # Tím sáng (active)
        
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
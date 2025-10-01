import customtkinter as CTK

import config
from features.tone_detector import ToneDetector
from features.transpose_detector import TransposeDetector
from features.return_speed_detector import ReturnSpeedDetector
from features.flex_tune_detector import FlexTuneDetector
from features.natural_vibrato_detector import NaturalVibratoDetector
from features.humanize_detector import HumanizeDetector
from features.plugin_bypass_detector import PluginBypassDetector
from features.soundshifter_detector import SoundShifterDetector
from features.soundshifter_bypass_detector import SoundShifterBypassDetector
from features.proq3_bypass_detector import ProQ3BypassDetector
from features.xvox_volume_detector import XvoxVolumeDetector
from features.reverb_detector import ReverbDetector
from utils.settings_manager import SettingsManager
from utils.helpers import ConfigHelper
from utils.bypass_toggle_manager import BypassToggleManager
from utils.debug_helper import DebugHelper

class CubaseAutoToolGUI:
    """GUI chính của ứng dụng."""
    
    def __init__(self):
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Load default values from config file
        self.default_values = ConfigHelper.load_default_values()
        
        # Load saved theme
        saved_theme = self.settings_manager.get_theme()
        CTK.set_appearance_mode(saved_theme)
        
        self.root = CTK.CTk()
        self.root.title(f"{config.APP_NAME} {config.APP_VERSION}")
        self.root.geometry(config.UI_SETTINGS['window_size'])  # Tăng kích thước để chứa nhiều chức năng
        self.root.resizable(True, True)  # Cho phép resize
        
        # Bind theme shortcut key (Ctrl+T)
        self.root.bind("<Control-t>", lambda event: self._toggle_theme())
        
        self.tone_detector = ToneDetector()
        self.transpose_detector = TransposeDetector()
        self.return_speed_detector = ReturnSpeedDetector()
        self.flex_tune_detector = FlexTuneDetector()
        self.natural_vibrato_detector = NaturalVibratoDetector()
        self.humanize_detector = HumanizeDetector()
        self.plugin_bypass_detector = PluginBypassDetector()
        self.soundshifter_detector = SoundShifterDetector()
        self.soundshifter_bypass_detector = SoundShifterBypassDetector()
        self.proq3_bypass_detector = ProQ3BypassDetector()
        self.xvox_volume_detector = XvoxVolumeDetector()
        self.reverb_detector = ReverbDetector()
        
        # Initialize bypass toggle manager
        self.bypass_manager = BypassToggleManager(self)
        
        self.current_tone_label = None  # Để lưu reference tới label hiển thị tone
        self.transpose_value_label = None  # Label hiển thị giá trị transpose
        self.return_speed_value_label = None  # Label hiển thị giá trị return speed
        self.soundshifter_value_label = None  # Label hiển thị giá trị SoundShifter
        
        # Plugin bypass toggle state
        self.plugin_bypass_toggle = None  # Toggle switch widget
        self.plugin_bypass_state = False  # Current toggle state (False = ON, True = OFF)
        
        # SoundShifter bypass toggle state
        self.soundshifter_bypass_toggle = None  # SoundShifter toggle switch widget
        self.soundshifter_bypass_state = False  # Current SoundShifter toggle state (False = ON, True = OFF)
        
        # ProQ3 (Lofi) bypass toggle state
        self.proq3_bypass_toggle = None  # ProQ3 toggle switch widget
        self.proq3_bypass_state = False  # Current ProQ3 toggle state (False = ON, True = OFF)
        self.flex_tune_value_label = None  # Label hiển thị giá trị flex tune
        self.natural_vibrato_value_label = None  # Label hiển thị giá trị natural vibrato
        self.humanize_value_label = None  # Label hiển thị giá trị humanize
        self.auto_detect_switch = None  # Toggle switch
        self.current_detected_tone = "--"  # Lưu tone hiện tại để so sánh
        
        # Audio control labels
        self.xvox_volume_label = None
        self.reverb_value_label = None
        
        # Set current theme index based on saved theme
        try:
            self.current_theme_index = config.GUI_THEMES.index(saved_theme)
        except ValueError:
            self.current_theme_index = 0
            
        self.theme_button = None  # Reference to theme button
        self._setup_ui()
    
    def _setup_ui(self):
        # Main container frame - với scrolling để chứa nhiều chức năng
        main_frame = CTK.CTkScrollableFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # Content grid frame
        content_frame = CTK.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Configure grid - 3 cột bằng nhau
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)
        
        # 3 Sections
        self._create_section(content_frame, "Auto-Tune", 0, self._setup_autotune_section)
        self._create_section(content_frame, "Nhạc", 1, self._setup_music_section)
        self._create_section(content_frame, "Giọng hát", 2, self._setup_vocal_section)

        # Setup footer after main content
        self._setup_footer()
        
        # Initialize plugin toggle state
        self._initialize_plugin_toggle_state()
    
    def _create_section(self, parent, title, column, setup_func):
        """Tạo một section trong grid 3 cột."""
        # Section frame
        section_frame = CTK.CTkFrame(parent, corner_radius=10, border_width=1, border_color="#404040")
        section_frame.grid(row=0, column=column, sticky="nsew", padx=5, pady=5)
        
        # Configure section frame to expand
        parent.grid_rowconfigure(0, weight=1)
        
        # Section title
        title_label = CTK.CTkLabel(
            section_frame,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="#FF6B6B"
        )
        title_label.pack(pady=(10, 15))
        
        # Content frame
        content_frame = CTK.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Setup section content
        setup_func(content_frame)
    
    def _setup_autotune_section(self, parent):
        """Thiết lập nội dung cho section Auto-Tune theo yêu cầu."""
        # Phần đầu: Tone hiện tại (trái) và Toggle tự động dò (phải)
        top_row = CTK.CTkFrame(parent, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))
        
        # Current Tone Display - góc trái nhỏ
        self.current_tone_label = CTK.CTkLabel(
            top_row,
            text="Tone: --",
            font=("Arial", 12, "bold"),
            text_color="#2CC985"
        )
        self.current_tone_label.pack(side="left")
        
        # Auto Detect Toggle - bên phải
        auto_detect_frame = CTK.CTkFrame(top_row, fg_color="transparent")
        auto_detect_frame.pack(side="right")
        
        auto_detect_label = CTK.CTkLabel(
            auto_detect_frame,
            text="Tự động dò:",
            font=("Arial", 11)
        )
        auto_detect_label.pack(side="left", padx=(0, 5))
        
        self.auto_detect_switch = CTK.CTkSwitch(
            auto_detect_frame,
            text="",
            command=self._toggle_auto_detect,
            width=40,
            height=20
        )
        
        # Load saved auto-detect state
        saved_auto_detect = self.settings_manager.get_auto_detect()
        
        if saved_auto_detect:
            self.auto_detect_switch.select()
        
        self.auto_detect_switch.pack(side="left")
        
        # Auto-start if previously enabled
        if saved_auto_detect:
            DebugHelper.print_init_debug("🔄 Auto-detect đã được bật từ lần trước")
            self.root.after_idle(lambda: self._start_auto_detect_from_saved_state())
        
        # Khung chứa 2 nút chính
        main_buttons_frame = CTK.CTkFrame(parent, fg_color="transparent")
        main_buttons_frame.pack(pady=(0, 15))
        
        # Nút Dò Tone
        btn_tone = CTK.CTkButton(
            main_buttons_frame,
            text=self.tone_detector.get_name(),
            font=("Arial", 11, "bold"),
            command=self._execute_tone_detector,
            width=95,
            height=35
        )
        btn_tone.pack(side="left", padx=(0, 5))
        
        # Plugin Bypass Toggle Frame
        plugin_frame = CTK.CTkFrame(main_buttons_frame, fg_color="transparent")
        plugin_frame.pack(side="left", padx=(5, 0))
        
        # Plugin label
        plugin_label = CTK.CTkLabel(
            plugin_frame,
            text="Plugin:",
            font=("Arial", 9),
            text_color="#CCCCCC"
        )
        plugin_label.pack()
        
        # Plugin Bypass Toggle Switch
        self.plugin_bypass_toggle = CTK.CTkSwitch(
            plugin_frame,
            text="",
            command=lambda: self.bypass_manager.toggle_bypass('plugin'),
            width=50,
            height=24,
            progress_color="#4CAF50",  # Green when ON
            button_color="#FF4444",   # Red button
            button_hover_color="#CC3333"
        )
        self.plugin_bypass_toggle.pack()
        
        # Plugin state label
        self.plugin_state_label = CTK.CTkLabel(
            plugin_frame,
            text="ON",
            font=("Arial", 8, "bold"),
            text_color="#4CAF50"  # Green for ON
        )
        self.plugin_state_label.pack()
        
        # Separator
        separator = CTK.CTkFrame(parent, height=2, fg_color="#404040")
        separator.pack(fill="x", pady=(0, 10))
        
        # Auto-Tune Controls Collapsible Section
        self.autotune_expanded = False
        
        # Auto-Tune Toggle Button
        self.autotune_toggle_btn = CTK.CTkButton(
            parent,
            text="▶ Auto-Tune Controls (5 tính năng)",
            font=("Arial", 12, "bold"),
            command=self._toggle_autotune_section,
            width=300,
            height=35,
            fg_color="#4A90E2",
            hover_color="#357ABD",
            corner_radius=8,
            anchor="w",
            text_color="#FFFFFF"
        )
        self.autotune_toggle_btn.pack(pady=(0, 10))
        
        # Auto-Tune Controls Frame (initially hidden)
        self.autotune_frame = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=8)
        # Frame is packed but hidden initially
        
        # Setup Auto-Tune controls inside the frame
        self._setup_autotune_controls(self.autotune_frame)
    
    def _setup_music_section(self, parent):
        """Thiết lập nội dung cho section Nhạc."""
        # SoundShifter Pitch Stereo Title
        pitch_title = CTK.CTkLabel(
            parent,
            text="SoundShifter Pitch",
            font=("Arial", 14, "bold"),
            text_color="#FF6B6B"
        )
        pitch_title.pack(pady=(0, 10))
        
        # Current value display
        self.soundshifter_value_label = CTK.CTkLabel(
            parent,
            text="Giá trị: 0 (Bình thường)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=180,
            height=20
        )
        self.soundshifter_value_label.pack(pady=(0, 15))
        
        # Buttons Frame
        buttons_frame = CTK.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(pady=(0, 10))
        
        # Nâng Tone Button
        btn_raise = CTK.CTkButton(
            buttons_frame,
            text="Nâng Tone (+2)",
            command=self._raise_tone,
            width=120,
            height=35,
            font=("Arial", 11, "bold"),
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        btn_raise.pack(side="top", pady=(0, 5))
        
        # Hạ Tone Button
        btn_lower = CTK.CTkButton(
            buttons_frame,
            text="Hạ Tone (-2)",
            command=self._lower_tone,
            width=120,
            height=35,
            font=("Arial", 11, "bold"),
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        btn_lower.pack(side="top", pady=(0, 5))
        
        # Reset Button
        btn_reset = CTK.CTkButton(
            buttons_frame,
            text="Reset (0)",
            command=self._reset_soundshifter,
            width=120,
            height=30,
            font=("Arial", 10),
            fg_color="#9E9E9E",
            hover_color="#757575"
        )
        btn_reset.pack(side="top", pady=(0, 15))
    
    def _toggle_autotune_section(self):
        """Toggle hiển thị/ẩn Auto-Tune controls section."""
        if self.autotune_expanded:
            # Collapse - ẩn frame
            self.autotune_frame.pack_forget()
            self.autotune_toggle_btn.configure(text="▶ Auto-Tune Controls (5 tính năng)")
            self.autotune_expanded = False
        else:
            # Expand - hiển thị frame
            self.autotune_frame.pack(fill="x", pady=(0, 10), padx=10)
            self.autotune_toggle_btn.configure(text="▼ Auto-Tune Controls (5 tính năng)")
            self.autotune_expanded = True
    
    def _setup_autotune_controls(self, parent):
        """Thiết lập tất cả Auto-Tune controls trong collapsible section."""
        
        # Padding cho toàn bộ section
        content_frame = CTK.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # === 1. TRANSPOSE SECTION ===
        # Phần Chuyển Giọng
        pitch_title = CTK.CTkLabel(
            content_frame,
            text="1. Chuyển Giọng (Transpose)",
            font=("Arial", 13, "bold"),
            text_color="#FF6B6B"
        )
        pitch_title.pack(pady=(0, 5), anchor="w")
        
        # Current value display
        self.transpose_value_label = CTK.CTkLabel(
            content_frame,
            text="Giá trị: 0 (Bình thường)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=180,
            height=20
        )
        self.transpose_value_label.pack(pady=(0, 5))
        
        # Slider với styling nhỏ gọn
        self.pitch_slider = CTK.CTkSlider(
            content_frame,
            from_=self.default_values.get('transpose_min', -12),
            to=self.default_values.get('transpose_max', 12),
            number_of_steps=abs(self.default_values.get('transpose_min', -12)) + abs(self.default_values.get('transpose_max', 12)),
            command=self._on_pitch_slider_change,
            width=220,
            height=16,
            button_color="#FF6B6B",
            button_hover_color="#FF5252",
            progress_color="#FF6B6B"
        )
        self.pitch_slider.set(self.default_values.get('transpose_default', 0))
        self.pitch_slider.pack(pady=(0, 5))
        
        # Apply Button
        btn_apply_pitch = CTK.CTkButton(
            content_frame,
            text="Áp Dụng Transpose",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_change,
            width=140,
            height=28,
            fg_color="#2CC985",
            hover_color="#228B67",
            corner_radius=6
        )
        btn_apply_pitch.pack(pady=(0, 15))
        
        # === 2. RETURN SPEED SECTION ===
        return_speed_title = CTK.CTkLabel(
            content_frame,
            text="2. Return Speed",
            font=("Arial", 13, "bold"),
            text_color="#FFA500"
        )
        return_speed_title.pack(pady=(0, 5), anchor="w")
        
        self.return_speed_value_label = CTK.CTkLabel(
            content_frame,
            text="Giá trị: 0 (Mặc định)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=180,
            height=20
        )
        self.return_speed_value_label.pack(pady=(0, 5))
        
        self.return_speed_slider = CTK.CTkSlider(
            content_frame,
            from_=self.default_values.get('return_speed_min', 0),
            to=self.default_values.get('return_speed_max', 100),
            number_of_steps=self.default_values.get('return_speed_max', 100) - self.default_values.get('return_speed_min', 0),
            command=self._on_return_speed_slider_change,
            width=220,
            height=16,
            button_color="#FFA500",
            button_hover_color="#FF8C00",
            progress_color="#FFA500"
        )
        self.return_speed_slider.set(self.default_values.get('return_speed_default', 0))
        self.return_speed_slider.pack(pady=(0, 5))
        
        btn_apply_return_speed = CTK.CTkButton(
            content_frame,
            text="Áp Dụng Return Speed",
            font=("Arial", 10, "bold"),
            command=self._apply_return_speed_change,
            width=140,
            height=28,
            fg_color="#FFA500",
            hover_color="#FF8C00",
            corner_radius=6
        )
        btn_apply_return_speed.pack(pady=(0, 15))
        
        # === 3. FLEX TUNE SECTION ===
        flex_tune_title = CTK.CTkLabel(
            content_frame,
            text="3. Flex Tune",
            font=("Arial", 13, "bold"),
            text_color="#FF69B4"
        )
        flex_tune_title.pack(pady=(0, 5), anchor="w")
        
        self.flex_tune_value_label = CTK.CTkLabel(
            content_frame,
            text="Giá trị: 0 (Mặc định)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=180,
            height=20
        )
        self.flex_tune_value_label.pack(pady=(0, 5))
        
        self.flex_tune_slider = CTK.CTkSlider(
            content_frame,
            from_=self.default_values.get('flex_tune_min', 0),
            to=self.default_values.get('flex_tune_max', 100),
            number_of_steps=self.default_values.get('flex_tune_max', 100) - self.default_values.get('flex_tune_min', 0),
            command=self._on_flex_tune_slider_change,
            width=220,
            height=16,
            button_color="#FF69B4",
            button_hover_color="#FF1493",
            progress_color="#FF69B4"
        )
        self.flex_tune_slider.set(self.default_values.get('flex_tune_default', 0))
        self.flex_tune_slider.pack(pady=(0, 5))
        
        btn_apply_flex_tune = CTK.CTkButton(
            content_frame,
            text="Áp Dụng Flex Tune",
            font=("Arial", 10, "bold"),
            command=self._apply_flex_tune_change,
            width=140,
            height=28,
            fg_color="#FF69B4",
            hover_color="#FF1493",
            corner_radius=6
        )
        btn_apply_flex_tune.pack(pady=(0, 15))
        
        # === 4. NATURAL VIBRATO SECTION ===
        natural_vibrato_title = CTK.CTkLabel(
            content_frame,
            text="4. Natural Vibrato",
            font=("Arial", 13, "bold"),
            text_color="#8A2BE2"
        )
        natural_vibrato_title.pack(pady=(0, 5), anchor="w")
        
        self.natural_vibrato_value_label = CTK.CTkLabel(
            content_frame,
            text="Giá trị: 0 (Mặc định)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=180,
            height=20
        )
        self.natural_vibrato_value_label.pack(pady=(0, 5))
        
        self.natural_vibrato_slider = CTK.CTkSlider(
            content_frame,
            from_=self.default_values.get('natural_vibrato_min', -12),
            to=self.default_values.get('natural_vibrato_max', 12),
            number_of_steps=abs(self.default_values.get('natural_vibrato_min', -12)) + abs(self.default_values.get('natural_vibrato_max', 12)),
            command=self._on_natural_vibrato_slider_change,
            width=220,
            height=16,
            button_color="#8A2BE2",
            button_hover_color="#7B68EE",
            progress_color="#8A2BE2"
        )
        self.natural_vibrato_slider.set(self.default_values.get('natural_vibrato_default', 0))
        self.natural_vibrato_slider.pack(pady=(0, 5))
        
        btn_apply_natural_vibrato = CTK.CTkButton(
            content_frame,
            text="Áp Dụng Natural Vibrato",
            font=("Arial", 10, "bold"),
            command=self._apply_natural_vibrato_change,
            width=140,
            height=28,
            fg_color="#8A2BE2",
            hover_color="#7B68EE",
            corner_radius=6
        )
        btn_apply_natural_vibrato.pack(pady=(0, 15))
        
        # === 5. HUMANIZE SECTION ===
        humanize_title = CTK.CTkLabel(
            content_frame,
            text="5. Humanize",
            font=("Arial", 13, "bold"),
            text_color="#32CD32"
        )
        humanize_title.pack(pady=(0, 5), anchor="w")
        
        self.humanize_value_label = CTK.CTkLabel(
            content_frame,
            text="Giá trị: 0 (Mặc định)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=180,
            height=20
        )
        self.humanize_value_label.pack(pady=(0, 5))
        
        self.humanize_slider = CTK.CTkSlider(
            content_frame,
            from_=self.default_values.get('humanize_min', 0),
            to=self.default_values.get('humanize_max', 100),
            number_of_steps=self.default_values.get('humanize_max', 100) - self.default_values.get('humanize_min', 0),
            command=self._on_humanize_slider_change,
            width=220,
            height=16,
            button_color="#32CD32",
            button_hover_color="#228B22",
            progress_color="#32CD32"
        )
        self.humanize_slider.set(self.default_values.get('humanize_default', 0))
        self.humanize_slider.pack(pady=(0, 5))
        
        btn_apply_humanize = CTK.CTkButton(
            content_frame,
            text="Áp Dụng Humanize",
            font=("Arial", 10, "bold"),
            command=self._apply_humanize_change,
            width=140,
            height=28,
            fg_color="#32CD32",
            hover_color="#228B22",
            corner_radius=6
        )
        btn_apply_humanize.pack(pady=(0, 10))
    
    def _setup_music_section(self, parent):
        """Thiết lập nội dung cho section Nhạc."""
        # SoundShifter Pitch Stereo Title
        pitch_title = CTK.CTkLabel(
            parent,
            text="SoundShifter Pitch",
            font=("Arial", 14, "bold"),
            text_color="#FF6B6B"
        )
        pitch_title.pack(pady=(0, 10))
        
        # Current value display
        self.soundshifter_value_label = CTK.CTkLabel(
            parent,
            text="Giá trị: 0 (Bình thường)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=180,
            height=20
        )
        self.soundshifter_value_label.pack(pady=(0, 15))
        
        # Buttons Frame
        buttons_frame = CTK.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(pady=(0, 10))
        
        # Nâng Tone Button
        btn_raise = CTK.CTkButton(
            buttons_frame,
            text="Nâng Tone (+2)",
            command=self._raise_tone,
            width=120,
            height=35,
            font=("Arial", 11, "bold"),
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        btn_raise.pack(side="top", pady=(0, 5))
        
        # Hạ Tone Button
        btn_lower = CTK.CTkButton(
            buttons_frame,
            text="Hạ Tone (-2)",
            command=self._lower_tone,
            width=120,
            height=35,
            font=("Arial", 11, "bold"),
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        btn_lower.pack(side="top", pady=(0, 5))
        
        # Reset Button
        btn_reset = CTK.CTkButton(
            buttons_frame,
            text="Reset (0)",
            command=self._reset_soundshifter,
            width=120,
            height=30,
            font=("Arial", 10),
            fg_color="#9E9E9E",
            hover_color="#757575"
        )
        btn_reset.pack(side="top", pady=(0, 15))
        
        # SoundShifter Bypass Toggle Section
        bypass_frame = CTK.CTkFrame(parent, fg_color="transparent")
        bypass_frame.pack(pady=(0, 10))
        
        # Bypass Toggle Label
        bypass_label = CTK.CTkLabel(
            bypass_frame,
            text="Plugin Bypass:",
            font=("Arial", 11, "bold"),
            text_color="#FFFFFF"
        )
        bypass_label.pack(pady=(0, 5))
        
        # Bypass Toggle Switch
        self.soundshifter_bypass_toggle = CTK.CTkSwitch(
            bypass_frame,
            text="",
            command=lambda: self.bypass_manager.toggle_bypass('soundshifter'),
            width=50,
            height=24,
            switch_width=50,
            switch_height=24,
            fg_color="#FF4444",    # Red when OFF (bypassed)
            progress_color="#44FF44",  # Green when ON (active)
        )
        self.soundshifter_bypass_toggle.pack(pady=(0, 5))
        
        # Bypass Status Label
        self.soundshifter_bypass_status_label = CTK.CTkLabel(
            bypass_frame,
            text="Plugin: ON",
            font=("Arial", 10),
            text_color="#44FF44",
            fg_color="#1F1F1F",
            corner_radius=4,
            width=100,
            height=20
        )
        self.soundshifter_bypass_status_label.pack()
    
    def _setup_vocal_section(self, parent):
        """Thiết lập nội dung cho section Giọng hát - compact với Xvox Volume."""
        # Xvox Volume Title
        xvox_title = CTK.CTkLabel(
            parent,
            text="Xvox Volume",
            font=("Arial", 12, "bold"),
            text_color="#FF69B4"
        )
        xvox_title.pack(pady=(0, 5))
        
        # Current volume display
        self.xvox_volume_label = CTK.CTkLabel(
            parent,
            text="Volume: 45",
            font=("Arial", 9),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=3,
            width=120,
            height=18
        )
        self.xvox_volume_label.pack(pady=(0, 5))
        
        # Volume slider
        self.xvox_volume_slider = CTK.CTkSlider(
            parent,
            from_=self.default_values.get('xvox_volume_min', 30),
            to=self.default_values.get('xvox_volume_max', 60),
            number_of_steps=self.default_values.get('xvox_volume_max', 60) - self.default_values.get('xvox_volume_min', 30),
            command=self._on_xvox_volume_slider_change,
            width=160,
            height=14,
            button_color="#FF69B4",
            progress_color="#FF69B4"
        )
        self.xvox_volume_slider.set(self.default_values.get('xvox_volume_default', 45))
        self.xvox_volume_slider.pack(pady=(0, 5))
        
        # Apply button
        btn_apply_volume = CTK.CTkButton(
            parent,
            text="Áp Dụng",
            font=("Arial", 9, "bold"),
            command=self._apply_xvox_volume,
            width=100,
            height=26,
            fg_color="#FF69B4",
            hover_color="#FF1493",
            corner_radius=4
        )
        btn_apply_volume.pack(pady=(0, 8))
        
        # Separator
        separator = CTK.CTkFrame(parent, height=1, fg_color="#404040")
        separator.pack(fill="x", pady=(5, 8))
        
        # ProQ3 Title
        lofi_title = CTK.CTkLabel(
            parent,
            text="Pro-Q 3 Lofi",
            font=("Arial", 12, "bold"),
            text_color="#32CD32"
        )
        lofi_title.pack(pady=(0, 8))
        
        # Plugin status - compact
        bypass_frame = CTK.CTkFrame(parent, fg_color="transparent")
        bypass_frame.pack()
        
        bypass_label = CTK.CTkLabel(
            bypass_frame,
            text="Plugin:",
            font=("Arial", 9, "bold"),
            text_color="#FFFFFF"
        )
        bypass_label.pack(pady=(0, 5))
        
        self.proq3_bypass_toggle = CTK.CTkSwitch(
            bypass_frame,
            text="",
            command=lambda: self.bypass_manager.toggle_bypass('proq3'),
            width=40,
            height=20,
            fg_color="#FF4444",
            progress_color="#44FF44"
        )
        self.proq3_bypass_toggle.pack(pady=(0, 5))
        
        self.proq3_bypass_status_label = CTK.CTkLabel(
            bypass_frame,
            text="ON",
            font=("Arial", 8, "bold"),
            text_color="#44FF44",
            fg_color="#2B2B2B",
            corner_radius=3,
            width=60,
            height=16
        )
        self.proq3_bypass_status_label.pack()
        
        # Separator
        separator2 = CTK.CTkFrame(parent, height=1, fg_color="#404040")
        separator2.pack(fill="x", pady=(8, 5))
        
        # Reverb Title
        reverb_title = CTK.CTkLabel(
            parent,
            text="Độ Vang",
            font=("Arial", 12, "bold"),
            text_color="#00CED1"
        )
        reverb_title.pack(pady=(0, 5))
        
        # Current reverb display
        self.reverb_value_label = CTK.CTkLabel(
            parent,
            text="Reverb: 36",
            font=("Arial", 9),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=3,
            width=120,
            height=18
        )
        self.reverb_value_label.pack(pady=(0, 5))
        
        # Reverb slider
        self.reverb_slider = CTK.CTkSlider(
            parent,
            from_=self.default_values.get('reverb_min', 30),
            to=self.default_values.get('reverb_max', 42),
            number_of_steps=self.default_values.get('reverb_max', 42) - self.default_values.get('reverb_min', 30),
            command=self._on_reverb_slider_change,
            width=160,
            height=14,
            button_color="#00CED1",
            progress_color="#00CED1"
        )
        self.reverb_slider.set(self.default_values.get('reverb_default', 36))
        self.reverb_slider.pack(pady=(0, 5))
        
        # Apply button
        btn_apply_reverb = CTK.CTkButton(
            parent,
            text="Áp Dụng",
            font=("Arial", 9, "bold"),
            command=self._apply_reverb,
            width=100,
            height=26,
            fg_color="#00CED1",
            hover_color="#00BFCC",
            corner_radius=4
        )
        btn_apply_reverb.pack(pady=(0, 5))
    

    
    def _setup_footer(self):
        """Thiết lập footer đơn giản."""
        # Footer container - nhỏ gọn hơn
        footer_container = CTK.CTkFrame(self.root, fg_color="#1F1F1F", corner_radius=0, height=40)
        footer_container.pack(side="bottom", fill="x", padx=0, pady=0)
        footer_container.pack_propagate(False)  # Maintain fixed height
        
        footer_frame = CTK.CTkFrame(footer_container, fg_color="transparent")
        footer_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # App version (left side)
        version_label = CTK.CTkLabel(
            footer_frame,
            text=f"{config.APP_NAME} {config.APP_VERSION}",
            font=("Arial", 10),
            text_color="gray"
        )
        version_label.pack(side="left")
        
        # Theme switcher (center)
        current_theme = config.GUI_THEMES[self.current_theme_index]
        
        self.theme_button = CTK.CTkButton(
            footer_frame,
            text="Theme",
            command=self._toggle_theme,
            width=60,
            height=20,
            font=("Arial", 10),
            corner_radius=4
        )
        self.theme_button.pack(side="left", padx=(10, 0))
        
        # Copyright information (right side) - clickable
        copyright_label = CTK.CTkLabel(
            footer_frame,
            text=config.COPYRIGHT,
            font=("Arial", 10, "bold"),
            text_color="#FF6B6B",
            cursor="hand2"
        )
        copyright_label.pack(side="right")
        
        # Make copyright clickable (copy phone to clipboard)
        def copy_phone(event):
            try:
                import pyperclip
                pyperclip.copy(config.CONTACT_INFO['phone'])
                # Temporary feedback
                original_text = copyright_label.cget("text")
                copyright_label.configure(text="📞 Đã copy số!", text_color="#00aa00")
                self.root.after(2000, lambda: copyright_label.configure(
                    text=original_text, text_color="#FF6B6B"))
                print(f"📞 Copied phone number to clipboard: {config.CONTACT_INFO['phone']}")
            except ImportError:
                print(f"📞 Phone: {config.CONTACT_INFO['phone']}")
        
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
                
                # Reset transpose về giá trị mặc định sau khi dò tone thành công
                transpose_default = self.default_values.get('transpose_default', 0)
                print(f"🔄 Resetting transpose to default ({transpose_default})...")
                reset_success = self.transpose_detector.reset_to_default()
                if reset_success:
                    print(f"✅ Transpose reset to {transpose_default} successfully")
                    # Cập nhật UI slider về giá trị mặc định
                    self.pitch_slider.set(transpose_default)
                    self._on_pitch_slider_change(transpose_default)  # Cập nhật label
                else:
                    print(f"❌ Failed to reset transpose to {transpose_default}")
                
                # Reset return speed về giá trị mặc định
                return_speed_default = self.default_values.get('return_speed_default', 200)
                print(f"🔄 Resetting return speed to default ({return_speed_default})...")
                rs_reset_success = self.return_speed_detector.reset_to_default()
                if rs_reset_success:
                    print(f"✅ Return Speed reset to {return_speed_default} successfully")
                    # Cập nhật UI slider về giá trị mặc định
                    self.return_speed_slider.set(return_speed_default)
                    self._on_return_speed_slider_change(return_speed_default)  # Cập nhật label
                else:
                    print(f"❌ Failed to reset return speed to {return_speed_default}")
                
                # Reset flex tune về giá trị mặc định
                flex_tune_default = self.default_values.get('flex_tune_default', 0)
                print(f"🔄 Resetting flex tune to default ({flex_tune_default})...")
                ft_reset_success = self.flex_tune_detector.reset_to_default()
                if ft_reset_success:
                    print(f"✅ Flex Tune reset to {flex_tune_default} successfully")
                    # Cập nhật UI slider về giá trị mặc định
                    self.flex_tune_slider.set(flex_tune_default)
                    self._on_flex_tune_slider_change(flex_tune_default)  # Cập nhật label
                else:
                    print(f"❌ Failed to reset flex tune to {flex_tune_default}")
                
                # Reset natural vibrato về giá trị mặc định
                natural_vibrato_default = self.default_values.get('natural_vibrato_default', 0)
                print(f"🔄 Resetting natural vibrato to default ({natural_vibrato_default})...")
                nv_reset_success = self.natural_vibrato_detector.reset_to_default()
                if nv_reset_success:
                    print(f"✅ Natural Vibrato reset to {natural_vibrato_default} successfully")
                    # Cập nhật UI slider về giá trị mặc định
                    self.natural_vibrato_slider.set(natural_vibrato_default)
                    self._on_natural_vibrato_slider_change(natural_vibrato_default)  # Cập nhật label
                else:
                    print(f"❌ Failed to reset natural vibrato to {natural_vibrato_default}")
                
                # Reset humanize về giá trị mặc định
                humanize_default = self.default_values.get('humanize_default', 0)
                print(f"🔄 Resetting humanize to default ({humanize_default})...")
                hz_reset_success = self.humanize_detector.reset_to_default()
                if hz_reset_success:
                    print(f"✅ Humanize reset to {humanize_default} successfully")
                    # Cập nhật UI slider về giá trị mặc định
                    self.humanize_slider.set(humanize_default)
                    self._on_humanize_slider_change(humanize_default)  # Cập nhật label
                else:
                    print(f"❌ Failed to reset humanize to {humanize_default}")
            else:
                print("❌ Tone detector failed")
        except Exception as e:
            print(f"❌ Error in tone detector: {e}")
        finally:
            # Luôn resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _execute_transpose_detector(self):
        """Thực thi tính năng transpose detection."""
        # Pause auto-detect
        self.pause_auto_detect_for_manual_action()
        
        try:
            success = self.transpose_detector.execute()
            if success:
                print("✅ Transpose detector completed successfully")
                # Cập nhật UI với giá trị mới
                self._update_transpose_display()
            else:
                print("❌ Transpose detector failed")
        except Exception as e:
            print(f"❌ Error in transpose detector: {e}")
        finally:
            # Luôn resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _on_pitch_slider_change(self, value):
        """Xử lý khi pitch slider thay đổi."""
        pitch_value = int(round(value))
        
        # Tạo text mô tả
        if pitch_value < 0:
            description = f"Già ({pitch_value})"
        elif pitch_value > 0:
            description = f"Trẻ (+{pitch_value})"
        else:
            description = "Bình thường (0)"
        
        # Cập nhật label
        if self.transpose_value_label:
            self.transpose_value_label.configure(text=f"Giá trị: {description}")
    
    def _on_return_speed_slider_change(self, value):
        """Xử lý khi return speed slider thay đổi."""
        speed_value = int(round(value))
        
        # Tạo text mô tả
        if speed_value < 25:
            description = f"Chậm ({speed_value})"
        elif speed_value > 75:
            description = f"Nhanh ({speed_value})"
        else:
            description = f"Mặc định ({speed_value})"
        
        # Cập nhật label
        if self.return_speed_value_label:
            self.return_speed_value_label.configure(text=f"Giá trị: {description}")
    
    def _on_flex_tune_slider_change(self, value):
        """Xử lý khi flex tune slider thay đổi."""
        flex_value = int(round(value))
        
        # Tạo text mô tả
        if flex_value < 25:
            description = f"Cứng ({flex_value})"
        elif flex_value > 75:
            description = f"Mềm ({flex_value})"
        else:
            description = f"Mặc định ({flex_value})"
        
        # Cập nhật label
        if self.flex_tune_value_label:
            self.flex_tune_value_label.configure(text=f"Giá trị: {description}")
    
    def _on_natural_vibrato_slider_change(self, value):
        """Xử lý khi natural vibrato slider thay đổi."""
        vibrato_value = int(round(value))
        
        # Tạo text mô tả
        if vibrato_value < 25:
            description = f"Không ({vibrato_value})"
        elif vibrato_value > 75:
            description = f"Mạnh ({vibrato_value})"
        else:
            description = f"Mặc định ({vibrato_value})"
        
        # Cập nhật label
        if self.natural_vibrato_value_label:
            self.natural_vibrato_value_label.configure(text=f"Giá trị: {description}")
    
    def _on_humanize_slider_change(self, value):
        """Xử lý khi humanize slider thay đổi."""
        humanize_value = int(round(value))
        
        # Tạo text mô tả
        if humanize_value < 25:
            description = f"Robot ({humanize_value})"
        elif humanize_value > 75:
            description = f"Tự nhiên ({humanize_value})"
        else:
            description = f"Cân bằng ({humanize_value})"
        
        # Cập nhật label
        if self.humanize_value_label:
            self.humanize_value_label.configure(text=f"Giá trị: {description}")
    
    def _apply_pitch_change(self):
        """Áp dụng thay đổi giảng điệu."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            pitch_value = int(round(self.pitch_slider.get()))
            
            # Thực hiện chỉnh giảng điệu
            success = self.transpose_detector.set_pitch_value(pitch_value)
            
            if success:
                print(f"✅ Pitch adjustment to {pitch_value} completed successfully")
            else:
                print(f"❌ Pitch adjustment to {pitch_value} failed")
                
        except Exception as e:
            print(f"❌ Error in pitch adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _apply_return_speed_change(self):
        """Áp dụng thay đổi return speed."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            speed_value = int(round(self.return_speed_slider.get()))
            
            # Thực hiện chỉnh return speed
            success = self.return_speed_detector.set_return_speed_value(speed_value)
            
            if success:
                print(f"✅ Return Speed adjustment to {speed_value} completed successfully")
            else:
                print(f"❌ Return Speed adjustment to {speed_value} failed")
                
        except Exception as e:
            print(f"❌ Error in return speed adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _apply_flex_tune_change(self):
        """Áp dụng thay đổi flex tune."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            flex_value = int(round(self.flex_tune_slider.get()))
            
            # Thực hiện chỉnh flex tune
            success = self.flex_tune_detector.set_flex_tune_value(flex_value)
            
            if success:
                print(f"✅ Flex Tune adjustment to {flex_value} completed successfully")
            else:
                print(f"❌ Flex Tune adjustment to {flex_value} failed")
                
        except Exception as e:
            print(f"❌ Error in flex tune adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _apply_natural_vibrato_change(self):
        """Áp dụng thay đổi natural vibrato."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            vibrato_value = int(round(self.natural_vibrato_slider.get()))
            
            # Thực hiện chỉnh natural vibrato
            success = self.natural_vibrato_detector.set_natural_vibrato_value(vibrato_value)
            
            if success:
                print(f"✅ Natural Vibrato adjustment to {vibrato_value} completed successfully")
            else:
                print(f"❌ Natural Vibrato adjustment to {vibrato_value} failed")
                
        except Exception as e:
            print(f"❌ Error in natural vibrato adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _apply_humanize_change(self):
        """Áp dụng thay đổi humanize."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            humanize_value = int(round(self.humanize_slider.get()))
            
            # Thực hiện chỉnh humanize
            success = self.humanize_detector.set_humanize_value(humanize_value)
            
            if success:
                print(f"✅ Humanize adjustment to {humanize_value} completed successfully")
            else:
                print(f"❌ Humanize adjustment to {humanize_value} failed")
                
        except Exception as e:
            print(f"❌ Error in humanize adjustment: {e}")
        finally:
            # Resume auto-detect
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
    
    def _initialize_plugin_toggle_state(self):
        """Khởi tạo trạng thái toggle dựa trên trạng thái thực tế của plugin."""
        # Register all bypass toggles with the manager
        self.bypass_manager.register_toggle('plugin', self.plugin_bypass_detector, 
                                           self.plugin_bypass_toggle, self.plugin_state_label)
        self.bypass_manager.register_toggle('soundshifter', self.soundshifter_bypass_detector,
                                           self.soundshifter_bypass_toggle, self.soundshifter_bypass_status_label)
        self.bypass_manager.register_toggle('proq3', self.proq3_bypass_detector,
                                           self.proq3_bypass_toggle, self.proq3_bypass_status_label)
        
        # Initialize all toggles using the manager
        self.bypass_manager.initialize_all_toggles()
    
    def pause_auto_detect_for_manual_action(self):
        """Tạm dừng auto-detect khi có manual action."""
        self.tone_detector.pause_auto_detect()
    
    def resume_auto_detect_after_manual_action(self):
        """Khôi phục auto-detect sau khi manual action hoàn thành."""
        self.tone_detector.resume_auto_detect()
    
    def _on_xvox_volume_slider_change(self, value):
        """Xử lý khi Xvox volume slider thay đổi."""
        volume_value = int(round(value))
        
        # Tạo text mô tả
        description = self.xvox_volume_detector.get_volume_description(volume_value)
        
        # Cập nhật label
        if self.xvox_volume_label:
            self.xvox_volume_label.configure(text=f"Volume: {volume_value}")
    
    def _apply_xvox_volume(self):
        """Áp dụng thay đổi Xvox volume."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            volume_value = int(round(self.xvox_volume_slider.get()))
            
            # Thực hiện chỉnh Xvox volume
            success = self.xvox_volume_detector.set_volume_value(volume_value)
            
            if success:
                print(f"✅ Xvox Volume set to {volume_value} successfully")
            else:
                print(f"❌ Failed to set Xvox Volume to {volume_value}")
                
        except Exception as e:
            print(f"❌ Error in Xvox volume adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _on_reverb_slider_change(self, value):
        """Xử lý khi reverb slider thay đổi."""
        reverb_value = int(round(value))
        
        # Tạo text mô tả
        description = self.reverb_detector.get_reverb_description(reverb_value)
        
        # Cập nhật label
        if self.reverb_value_label:
            self.reverb_value_label.configure(text=f"Reverb: {reverb_value}")
    
    def _apply_reverb(self):
        """Áp dụng thay đổi Reverb."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            reverb_value = int(round(self.reverb_slider.get()))
            
            # Thực hiện chỉnh Reverb
            success = self.reverb_detector.set_reverb_value(reverb_value)
            
            if success:
                print(f"✅ Reverb set to {reverb_value} successfully")
            else:
                print(f"❌ Failed to set Reverb to {reverb_value}")
                
        except Exception as e:
            print(f"❌ Error in reverb adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _raise_tone(self):
        """Nâng tone lên (+2)."""
        self.pause_auto_detect_for_manual_action()
        
        try:
            success = self.soundshifter_detector.raise_tone(1)  # 1 tone = +2
            if success:
                self._update_soundshifter_display()
                print("✅ Raised tone successfully")
            else:
                print("❌ Failed to raise tone")
        except Exception as e:
            print(f"❌ Error raising tone: {e}")
    
    def _lower_tone(self):
        """Hạ tone xuống (-2)."""
        self.pause_auto_detect_for_manual_action()
        
        try:
            success = self.soundshifter_detector.lower_tone(1)  # 1 tone = -2
            if success:
                self._update_soundshifter_display()
                print("✅ Lowered tone successfully")
            else:
                print("❌ Failed to lower tone")
        except Exception as e:
            print(f"❌ Error lowering tone: {e}")
    
    def _reset_soundshifter(self):
        """Reset SoundShifter về 0."""
        self.pause_auto_detect_for_manual_action()
        
        try:
            success = self.soundshifter_detector.reset_pitch()
            if success:
                self._update_soundshifter_display()
                print("✅ Reset SoundShifter successfully")
            else:
                print("❌ Failed to reset SoundShifter")
        except Exception as e:
            print(f"❌ Error resetting SoundShifter: {e}")
    
    def _update_soundshifter_display(self):
        """Cập nhật hiển thị giá trị SoundShifter."""
        if self.soundshifter_value_label:
            current_value = self.soundshifter_detector.current_value
            description = self.soundshifter_detector.get_tone_description(current_value)
            self.soundshifter_value_label.configure(text=f"Giá trị: {current_value} ({description})")
    
    def _toggle_theme(self):
        """Chuyển đổi theme giữa dark và light."""
        # Cycle through themes (dark <-> light)
        self.current_theme_index = (self.current_theme_index + 1) % len(config.GUI_THEMES)
        new_theme = config.GUI_THEMES[self.current_theme_index]
        
        # Apply theme
        CTK.set_appearance_mode(new_theme)
        
        # Save theme preference
        self.settings_manager.set_theme(new_theme)
        
        print(f"Theme switched to: {new_theme}")
    
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



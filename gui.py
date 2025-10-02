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
from features.volume_detector import VolumeDetector
from features.tone_mic_detector import ToneMicDetector
from utils.settings_manager import SettingsManager
from utils.helpers import ConfigHelper, MessageHelper
from utils.bypass_toggle_manager import BypassToggleManager
from utils.debug_helper import DebugHelper
from utils.music_presets_manager import MusicPresetsManager
from utils.fast_batch_processor import FastBatchProcessor
from utils.ultra_fast_processor import UltraFastAutoTuneProcessor

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
        
        # Đảm bảo cửa sổ luôn hiển thị trên top khi khởi động
        self.root.lift()  # Đưa cửa sổ lên trên
        self.root.attributes('-topmost', True)  # Tạm thời set topmost
        self.root.focus_force()  # Force focus
        
        # Bind theme shortcut key (Ctrl+T)
        self.root.bind("<Control-t>", lambda event: self._toggle_theme())
        
        # Bind topmost toggle key (Ctrl+Shift+T)
        self.root.bind("<Control-Shift-T>", lambda event: self._toggle_topmost_mode())
        
        # Track topmost state
        self.is_topmost = True
        
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
        self.volume_detector = VolumeDetector()
        self.tone_mic_detector = ToneMicDetector()
        
        # Initialize bypass toggle manager
        self.bypass_manager = BypassToggleManager(self)
        
        # Initialize music presets manager
        self.music_presets_manager = MusicPresetsManager()
        
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
        
        # Tắt topmost mode sau khi UI đã setup xong để không gây phiền hà
        self.root.after(1000, self._disable_topmost_mode)  # Tắt sau 1 giây
    
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
        
        # Nút Tone Mic
        btn_tone_mic = CTK.CTkButton(
            main_buttons_frame,
            text="🎤 Tone Mic",
            font=("Arial", 11, "bold"),
            command=self._execute_tone_mic_detector,
            width=95,
            height=35,
            fg_color="#E91E63",
            hover_color="#C2185B"
        )
        btn_tone_mic.pack(side="left", padx=(0, 5))
        
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
        separator.pack(fill="x", pady=(0, 15))
        
        # Music Presets Section - Always visible
        presets_title = CTK.CTkLabel(
            parent,
            text="🎵 Music Presets",
            font=("Arial", 14, "bold"),
            text_color="#4A90E2"
        )
        presets_title.pack(pady=(0, 15))
        
        # Music Presets Frame - Always visible
        self.autotune_frame = CTK.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=8, border_width=1, border_color="#404040")
        self.autotune_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Setup Music Presets controls inside the frame
        self._setup_music_presets_controls(self.autotune_frame)
    
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
    

    
    def _setup_music_presets_controls(self, parent):
        """Thiết lập Music Presets controls với thiết kế đồng bộ."""
        
        # Padding cho toàn bộ section
        content_frame = CTK.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize sliders for compatibility (hidden)
        self._init_hidden_sliders(content_frame)
        
        # Configure grid layout - 3 columns for music controls
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)
        
        # === NHẠC BOLERO SECTION (Left Column) ===
        bolero_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#FF6B6B")
        bolero_container.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=5)
        
        bolero_title = CTK.CTkLabel(
            bolero_container,
            text="🎵 Nhạc Bolero",
            font=("Arial", 12, "bold"),
            text_color="#FF6B6B"
        )
        bolero_title.pack(pady=(10, 5))
        
        # Bolero Level Display
        self.bolero_level_label = CTK.CTkLabel(
            bolero_container,
            text="Mức: 0 (Bình thường)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=160,
            height=22
        )
        self.bolero_level_label.pack(pady=(0, 10))
        
        # Bolero Controls Frame
        bolero_controls = CTK.CTkFrame(bolero_container, fg_color="transparent")
        bolero_controls.pack(pady=(0, 10))
        
        # Bolero Buttons Row
        bolero_buttons = CTK.CTkFrame(bolero_controls, fg_color="transparent")
        bolero_buttons.pack()
        
        self.bolero_minus_btn = CTK.CTkButton(
            bolero_buttons,
            text="➖",
            font=("Arial", 14, "bold"),
            command=lambda: self._adjust_music_preset('bolero', -1),
            width=35,
            height=30,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.bolero_minus_btn.pack(side="left", padx=(0, 5))
        
        self.bolero_apply_btn = CTK.CTkButton(
            bolero_buttons,
            text="Áp Dụng",
            font=("Arial", 10, "bold"),
            command=lambda: self._apply_music_preset('bolero'),
            width=80,
            height=30,
            fg_color="#FF6B6B",
            hover_color="#FF5252"
        )
        self.bolero_apply_btn.pack(side="left", padx=(0, 5))
        
        self.bolero_plus_btn = CTK.CTkButton(
            bolero_buttons,
            text="➕",
            font=("Arial", 14, "bold"),
            command=lambda: self._adjust_music_preset('bolero', 1),
            width=35,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        self.bolero_plus_btn.pack(side="left")
        
        # === NHẠC TRẺ SECTION (Middle Column) ===
        nhac_tre_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#32CD32")
        nhac_tre_container.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        
        nhac_tre_title = CTK.CTkLabel(
            nhac_tre_container,
            text="🎤 Nhạc Trẻ",
            font=("Arial", 12, "bold"),
            text_color="#32CD32"
        )
        nhac_tre_title.pack(pady=(10, 5))
        
        # Nhạc Trẻ Level Display
        self.nhac_tre_level_label = CTK.CTkLabel(
            nhac_tre_container,
            text="Mức: 0 (Bình thường)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=160,
            height=22
        )
        self.nhac_tre_level_label.pack(pady=(0, 10))
        
        # Nhạc Trẻ Controls Frame
        nhac_tre_controls = CTK.CTkFrame(nhac_tre_container, fg_color="transparent")
        nhac_tre_controls.pack(pady=(0, 10))
        
        # Nhạc Trẻ Buttons Row
        nhac_tre_buttons = CTK.CTkFrame(nhac_tre_controls, fg_color="transparent")
        nhac_tre_buttons.pack()
        
        self.nhac_tre_minus_btn = CTK.CTkButton(
            nhac_tre_buttons,
            text="➖",
            font=("Arial", 14, "bold"),
            command=lambda: self._adjust_music_preset('nhac_tre', -1),
            width=35,
            height=30,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.nhac_tre_minus_btn.pack(side="left", padx=(0, 5))
        
        self.nhac_tre_apply_btn = CTK.CTkButton(
            nhac_tre_buttons,
            text="Áp Dụng",
            font=("Arial", 10, "bold"),
            command=lambda: self._apply_music_preset('nhac_tre'),
            width=80,
            height=30,
            fg_color="#32CD32",
            hover_color="#228B22"
        )
        self.nhac_tre_apply_btn.pack(side="left", padx=(0, 5))
        
        self.nhac_tre_plus_btn = CTK.CTkButton(
            nhac_tre_buttons,
            text="➕",
            font=("Arial", 14, "bold"),
            command=lambda: self._adjust_music_preset('nhac_tre', 1),
            width=35,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        self.nhac_tre_plus_btn.pack(side="left")
        
        # === VOLUME NHẠC SECTION (Right Column in Music Area) ===
        volume_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#FF9800")
        volume_container.grid(row=0, column=2, sticky="nsew", padx=(2, 0), pady=5)
        
        volume_title = CTK.CTkLabel(
            volume_container,
            text="🔊 Âm Lượng Nhạc",
            font=("Arial", 12, "bold"),
            text_color="#FF9800"
        )
        volume_title.pack(pady=(10, 5))
        
        # Volume value display
        self.volume_value_label = CTK.CTkLabel(
            volume_container,
            text="Âm lượng: -3 (Vừa)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=160,
            height=22
        )
        self.volume_value_label.pack(pady=(0, 8))
        
        # Volume slider
        self.volume_slider = CTK.CTkSlider(
            volume_container,
            from_=-7,
            to=0,
            number_of_steps=7,
            width=200,
            height=20,
            button_color="#FF9800",
            button_hover_color="#F57C00",
            progress_color="#FF9800",
            fg_color="#2B2B2B",
            command=self._on_volume_slider_change
        )
        self.volume_slider.set(-3)  # Default value
        self.volume_slider.pack(pady=(0, 10))
        
        # Volume buttons frame
        volume_buttons_frame = CTK.CTkFrame(volume_container, fg_color="transparent")
        volume_buttons_frame.pack(pady=(0, 15))
        
        # Volume Apply Button
        self.volume_apply_btn = CTK.CTkButton(
            volume_buttons_frame,
            text="✅ Áp Dụng",
            font=("Arial", 10, "bold"),
            command=self._apply_volume,
            width=100,
            height=30,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        self.volume_apply_btn.pack(side="left", padx=(0, 5))
        
        # Mute Toggle Button
        self.mute_toggle_btn = CTK.CTkButton(
            volume_buttons_frame,
            text="🔇 Mute",
            font=("Arial", 10, "bold"),
            command=self._toggle_mute,
            width=80,
            height=30,
            fg_color="#E91E63",
            hover_color="#C2185B"
        )
        self.mute_toggle_btn.pack(side="left")
        
        # === MIC CONTROLS SECTION (Bass, Treble, Volume, Reverb) ===
        mic_controls_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#00BCD4")
        mic_controls_container.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 5), padx=0)
        
        mic_controls_title = CTK.CTkLabel(
            mic_controls_container,
            text="🎤 Điều Chỉnh Mic (Bass, Treble, Volume, Reverb)",
            font=("Arial", 12, "bold"),
            text_color="#00BCD4"
        )
        mic_controls_title.pack(pady=(10, 5))
        
        # Mic controls grid frame (2x2 layout)
        mic_controls_grid = CTK.CTkFrame(mic_controls_container, fg_color="transparent")
        mic_controls_grid.pack(pady=(0, 15))
        
        # Configure grid for 2x2 layout (Bass, Treble, Volume, Reverb)
        mic_controls_grid.grid_columnconfigure(0, weight=1)
        mic_controls_grid.grid_columnconfigure(1, weight=1)
        mic_controls_grid.grid_rowconfigure(0, weight=1)
        mic_controls_grid.grid_rowconfigure(1, weight=1)
        
        # === BASS CONTROL (Top Left) ===
        bass_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        bass_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        
        bass_label = CTK.CTkLabel(
            bass_frame,
            text="🔉 Bass (LOW)",
            font=("Arial", 11, "bold"),
            text_color="#00BCD4"
        )
        bass_label.pack(pady=(0, 5))
        
        # Bass value display
        self.bass_value_label = CTK.CTkLabel(
            bass_frame,
            text="Bass: 0",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=120,
            height=22
        )
        self.bass_value_label.pack(pady=(0, 5))
        
        # Bass slider
        self.bass_slider = CTK.CTkSlider(
            bass_frame,
            from_=-30,
            to=30,
            number_of_steps=60,
            width=200,
            height=20,
            button_color="#00BCD4",
            button_hover_color="#00ACC1",
            progress_color="#00BCD4",
            fg_color="#2B2B2B",
            command=self._on_bass_slider_change
        )
        self.bass_slider.set(0)  # Default value
        self.bass_slider.pack(pady=(0, 10))
        
        # Bass Apply Button
        self.bass_apply_btn = CTK.CTkButton(
            bass_frame,
            text="✅ Áp Dụng Bass",
            font=("Arial", 9, "bold"),
            command=self._apply_bass,
            width=150,
            height=25,
            fg_color="#00BCD4",
            hover_color="#00ACC1"
        )
        self.bass_apply_btn.pack()
        
        # === TREBLE CONTROL (Top Right) ===
        treble_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        treble_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        treble_label = CTK.CTkLabel(
            treble_frame,
            text="🔊 Treble (HIGH)",
            font=("Arial", 11, "bold"),
            text_color="#00BCD4"
        )
        treble_label.pack(pady=(0, 5))
        
        # Treble value display
        self.treble_value_label = CTK.CTkLabel(
            treble_frame,
            text="Treble: 0",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=120,
            height=22
        )
        self.treble_value_label.pack(pady=(0, 5))
        
        # Treble slider
        self.treble_slider = CTK.CTkSlider(
            treble_frame,
            from_=-20,
            to=30,
            number_of_steps=50,
            width=200,
            height=20,
            button_color="#00BCD4",
            button_hover_color="#00ACC1",
            progress_color="#00BCD4",
            fg_color="#2B2B2B",
            command=self._on_treble_slider_change
        )
        self.treble_slider.set(0)  # Default value
        self.treble_slider.pack(pady=(0, 10))
        
        # Treble Apply Button
        self.treble_apply_btn = CTK.CTkButton(
            treble_frame,
            text="✅ Áp Dụng Treble",
            font=("Arial", 9, "bold"),
            command=self._apply_treble,
            width=150,
            height=25,
            fg_color="#00BCD4",
            hover_color="#00ACC1"
        )
        self.treble_apply_btn.pack()
        
        # === VOLUME MIC CONTROL (Bottom Left) ===
        volume_mic_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        volume_mic_frame.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(10, 0))
        
        volume_mic_label = CTK.CTkLabel(
            volume_mic_frame,
            text="🎛️ COMP",
            font=("Arial", 11, "bold"),
            text_color="#FF69B4"
        )
        volume_mic_label.pack(pady=(0, 5))
        
        # COMP value display
        self.volume_mic_value_label = CTK.CTkLabel(
            volume_mic_frame,
            text="COMP: 45",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=120,
            height=22
        )
        self.volume_mic_value_label.pack(pady=(0, 5))
        
        # Volume slider
        self.volume_mic_slider = CTK.CTkSlider(
            volume_mic_frame,
            from_=30,
            to=60,
            number_of_steps=30,
            width=200,
            height=20,
            button_color="#FF69B4",
            button_hover_color="#E91E63",
            progress_color="#FF69B4",
            fg_color="#2B2B2B",
            command=self._on_volume_mic_slider_change
        )
        self.volume_mic_slider.set(45)  # Default value
        self.volume_mic_slider.pack(pady=(0, 10))
        
        # Volume Apply Button
        self.volume_mic_apply_btn = CTK.CTkButton(
            volume_mic_frame,
            text="✅ Áp Dụng Volume",
            font=("Arial", 9, "bold"),
            command=self._apply_volume_mic,
            width=150,
            height=25,
            fg_color="#FF69B4",
            hover_color="#E91E63"
        )
        self.volume_mic_apply_btn.pack()
        
        # === REVERB CONTROL (Bottom Right) ===
        reverb_mic_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        reverb_mic_frame.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))
        
        reverb_mic_label = CTK.CTkLabel(
            reverb_mic_frame,
            text="🌊 Độ Vang Mic",
            font=("Arial", 11, "bold"),
            text_color="#00CED1"
        )
        reverb_mic_label.pack(pady=(0, 5))
        
        # Reverb value display
        self.reverb_mic_value_label = CTK.CTkLabel(
            reverb_mic_frame,
            text="Reverb: 36",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=120,
            height=22
        )
        self.reverb_mic_value_label.pack(pady=(0, 5))
        
        # Reverb slider
        self.reverb_mic_slider = CTK.CTkSlider(
            reverb_mic_frame,
            from_=30,
            to=42,
            number_of_steps=12,
            width=200,
            height=20,
            button_color="#00CED1",
            button_hover_color="#00BCD4",
            progress_color="#00CED1",
            fg_color="#2B2B2B",
            command=self._on_reverb_mic_slider_change
        )
        self.reverb_mic_slider.set(36)  # Default value
        self.reverb_mic_slider.pack(pady=(0, 10))
        
        # Reverb Apply Button
        self.reverb_mic_apply_btn = CTK.CTkButton(
            reverb_mic_frame,
            text="✅ Áp Dụng Reverb",
            font=("Arial", 9, "bold"),
            command=self._apply_reverb_mic,
            width=150,
            height=25,
            fg_color="#00CED1",
            hover_color="#00BCD4"
        )
        self.reverb_mic_apply_btn.pack()
        
        # === TRANSPOSE SECTION (Full Width Row) ===
        transpose_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#9C27B0")
        transpose_container.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 5), padx=0)
        
        transpose_title = CTK.CTkLabel(
            transpose_container,
            text="🎶 Chuyển Giọng (Transpose)",
            font=("Arial", 12, "bold"),
            text_color="#9C27B0"
        )
        transpose_title.pack(pady=(10, 5))
        
        # Transpose value display
        self.transpose_value_label = CTK.CTkLabel(
            transpose_container,
            text="Giá trị: 0 (Bình thường)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=160,
            height=22
        )
        self.transpose_value_label.pack(pady=(0, 8))
        
        # Transpose controls frame
        transpose_controls = CTK.CTkFrame(transpose_container, fg_color="transparent")
        transpose_controls.pack(pady=(0, 10))
        
        # Transpose slider
        self.pitch_slider = CTK.CTkSlider(
            transpose_controls,
            from_=self.default_values.get('transpose_min', -12),
            to=self.default_values.get('transpose_max', 12),
            number_of_steps=abs(self.default_values.get('transpose_min', -12)) + abs(self.default_values.get('transpose_max', 12)),
            command=self._on_pitch_slider_change,
            width=200,
            height=16,
            button_color="#9C27B0",
            button_hover_color="#7B1FA2",
            progress_color="#9C27B0"
        )
        self.pitch_slider.set(self.default_values.get('transpose_default', 0))
        self.pitch_slider.pack(pady=(0, 8))
        
        # Transpose Apply Button
        btn_apply_pitch = CTK.CTkButton(
            transpose_controls,
            text="Áp Dụng Transpose",
            font=("Arial", 10, "bold"),
            command=self._apply_pitch_change,
            width=120,
            height=28,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        btn_apply_pitch.pack()
        
        # Update initial display
        self._update_music_preset_display('bolero')
        self._update_music_preset_display('nhac_tre')
    
    def _init_hidden_sliders(self, parent):
        """Khởi tạo sliders ẩn để giữ compatibility với code cũ."""
        # Hidden frame không hiển thị
        hidden_frame = CTK.CTkFrame(parent, fg_color="transparent", height=0)
        # Không pack frame này
        
        # Return Speed Slider (hidden)
        self.return_speed_slider = CTK.CTkSlider(
            hidden_frame,
            from_=self.default_values.get('return_speed_min', 0),
            to=self.default_values.get('return_speed_max', 100),
            command=self._on_return_speed_slider_change,
        )
        self.return_speed_slider.set(self.default_values.get('return_speed_default', 0))
        
        # Flex Tune Slider (hidden)
        self.flex_tune_slider = CTK.CTkSlider(
            hidden_frame,
            from_=self.default_values.get('flex_tune_min', 0),
            to=self.default_values.get('flex_tune_max', 100),
            command=self._on_flex_tune_slider_change,
        )
        self.flex_tune_slider.set(self.default_values.get('flex_tune_default', 0))
        
        # Natural Vibrato Slider (hidden)
        self.natural_vibrato_slider = CTK.CTkSlider(
            hidden_frame,
            from_=self.default_values.get('natural_vibrato_min', -12),
            to=self.default_values.get('natural_vibrato_max', 12),
            command=self._on_natural_vibrato_slider_change,
        )
        self.natural_vibrato_slider.set(self.default_values.get('natural_vibrato_default', 0))
        
        # Humanize Slider (hidden)
        self.humanize_slider = CTK.CTkSlider(
            hidden_frame,
            from_=self.default_values.get('humanize_min', 0),
            to=self.default_values.get('humanize_max', 100),
            command=self._on_humanize_slider_change,
        )
        self.humanize_slider.set(self.default_values.get('humanize_default', 0))
        
        # Labels for compatibility
        self.return_speed_value_label = CTK.CTkLabel(hidden_frame, text="")
        self.flex_tune_value_label = CTK.CTkLabel(hidden_frame, text="")
        self.natural_vibrato_value_label = CTK.CTkLabel(hidden_frame, text="")
        self.humanize_value_label = CTK.CTkLabel(hidden_frame, text="")
    
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
        """Thiết lập nội dung cho section Giọng hát - chỉ ProQ3 controls."""
        
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
        
        # Hotkeys info (center)
        hotkeys_label = CTK.CTkLabel(
            footer_frame,
            text="Ctrl+T: Theme | Ctrl+Shift+T: Always on Top",
            font=("Arial", 8),
            text_color="#888888"
        )
        hotkeys_label.pack(side="left", padx=(15, 0))
        
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
            # Truyền callback để cập nhật UI - sử dụng fast mode cho batch reset
            success = self.tone_detector.execute(tone_callback=self.update_current_tone, fast_mode=True)
            if success:
                print("✅ Tone detector completed successfully")
                
                # Batch reset tất cả về giá trị mặc định - nhanh và mượt hơn
                print("🔄 Batch resetting all Auto-Tune parameters to defaults...")
                self._batch_reset_autotune_parameters()
                
            else:
                print("❌ Tone detector failed")
        except Exception as e:
            print(f"❌ Error in tone detector: {e}")
        finally:
            # Luôn resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _execute_tone_mic_detector(self):
        """Thực thi tính năng phát hiện tone mic controls."""
        # Pause auto-detect
        self.pause_auto_detect_for_manual_action()
        
        try:
            print("🎤 Executing Tone Mic Detector...")
            success = self.tone_mic_detector.execute()
            
            if success:
                print("✅ Tone Mic detector completed successfully")
                MessageHelper.show_info(
                    "Tone Mic Detector", 
                    "✅ Phát hiện thành công!\n\nKiểm tra file debug image trong folder 'result' để xem kết quả OCR."
                )
            else:
                print("❌ Tone Mic detector failed")
                MessageHelper.show_error(
                    "Lỗi Tone Mic", 
                    "❌ Không thể phát hiện các control tone mic!\n\nVui lòng:\n• Đảm bảo Cubase Pro đang mở\n• Kiểm tra template tone_mic_template.png\n• Xem console log để biết thêm chi tiết"
                )
                
        except Exception as e:
            print(f"❌ Error in tone mic detector: {e}")
            MessageHelper.show_error("Lỗi", f"Lỗi trong tone mic detector: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _batch_reset_autotune_parameters(self):
        """Ultra fast batch reset tất cả parameters Auto-Tune."""
        
        # Prepare ultra fast batch parameters
        reset_configs = [
            ('Return Speed', self.return_speed_detector, 'return_speed_default', 200),
            ('Flex Tune', self.flex_tune_detector, 'flex_tune_default', 0),
            ('Natural Vibrato', self.natural_vibrato_detector, 'natural_vibrato_default', 0),
            ('Humanize', self.humanize_detector, 'humanize_default', 0),
            ('Transpose', self.transpose_detector, 'transpose_default', 0)
        ]
        
        # Build parameters list for ultra fast processor
        parameters_list = []
        ui_updates = []
        
        for name, detector, default_key, default_fallback in reset_configs:
            default_value = self.default_values.get(default_key, default_fallback)
            
            parameters_list.append({
                'detector': detector,
                'value': default_value,
                'name': name
            })
            
            # Prepare UI updates
            slider_map = {
                'Return Speed': (self.return_speed_slider, self._on_return_speed_slider_change),
                'Flex Tune': (self.flex_tune_slider, self._on_flex_tune_slider_change),
                'Natural Vibrato': (self.natural_vibrato_slider, self._on_natural_vibrato_slider_change),
                'Humanize': (self.humanize_slider, self._on_humanize_slider_change),
                'Transpose': (self.pitch_slider, self._on_pitch_slider_change)
            }
            
            if name in slider_map:
                slider, update_method = slider_map[name]
                ui_updates.append({
                    'name': name,
                    'slider': slider,
                    'update_method': update_method,
                    'default_value': default_value
                })
        
        # Execute ultra fast batch
        try:
            print("⚡ Ultra fast batch reset starting...")
            
            ultra_processor = UltraFastAutoTuneProcessor()
            success_count, total_count = ultra_processor.execute_ultra_fast_batch(parameters_list)
            
            # Update UI sliders instantly (no delays needed)
            for ui_update in ui_updates:
                try:
                    ui_update['slider'].set(ui_update['default_value'])
                    ui_update['update_method'](ui_update['default_value'])
                except Exception as e:
                    print(f"⚠️ UI update error for {ui_update['name']}: {e}")
            
            print(f"⚡ Ultra fast reset completed: {success_count}/{total_count} successful")
            
        except Exception as e:
            print(f"❌ Error in ultra fast reset: {e}")
            # Fallback to individual resets if ultra fast fails
            self._fallback_individual_reset()
    
    def _fallback_individual_reset(self):
        """Fallback method - reset từng cái một nếu batch fails."""
        print("🔄 Fallback to individual reset...")
        
        reset_items = [
            (self.transpose_detector, self.pitch_slider, self._on_pitch_slider_change, 'transpose_default', 0, 'Transpose'),
            (self.return_speed_detector, self.return_speed_slider, self._on_return_speed_slider_change, 'return_speed_default', 200, 'Return Speed'),
            (self.flex_tune_detector, self.flex_tune_slider, self._on_flex_tune_slider_change, 'flex_tune_default', 0, 'Flex Tune'),
            (self.natural_vibrato_detector, self.natural_vibrato_slider, self._on_natural_vibrato_slider_change, 'natural_vibrato_default', 0, 'Natural Vibrato'),
            (self.humanize_detector, self.humanize_slider, self._on_humanize_slider_change, 'humanize_default', 0, 'Humanize')
        ]
        
        success_count = 0
        for detector, slider, update_method, default_key, default_fallback, name in reset_items:
            try:
                default_value = self.default_values.get(default_key, default_fallback)
                if detector.reset_to_default():
                    slider.set(default_value)
                    update_method(default_value)
                    success_count += 1
                    print(f"✅ {name}: {default_value}")
                else:
                    print(f"❌ {name}: Failed")
            except Exception as e:
                print(f"❌ {name} error: {e}")
        
        print(f"🔄 Individual reset completed: {success_count}/5 successful")
    
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
    
    def _disable_topmost_mode(self):
        """Tắt chế độ topmost để không gây phiền hà khi làm việc."""
        try:
            self.root.attributes('-topmost', False)
            self.is_topmost = False
            print("✅ GUI topmost mode disabled - Có thể chuyển giữa các cửa sổ bình thường")
        except Exception as e:
            print(f"⚠️ Không thể tắt topmost mode: {e}")
    
    def _toggle_topmost_mode(self):
        """Toggle chế độ always on top (Ctrl+Shift+T)."""
        try:
            self.is_topmost = not self.is_topmost
            self.root.attributes('-topmost', self.is_topmost)
            
            if self.is_topmost:
                print("🔝 GUI set to Always On Top - Press Ctrl+Shift+T to toggle")
            else:
                print("📱 GUI normal mode - Press Ctrl+Shift+T to toggle")
                
        except Exception as e:
            print(f"❌ Error toggling topmost mode: {e}")
    
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
    
    def _on_volume_slider_change(self, value):
        """Callback khi volume slider thay đổi - chỉ cập nhật display."""
        volume_value = int(value)
        
        # Chỉ cập nhật display, không thực hiện action
        description = self.volume_detector.get_volume_description(volume_value)
        self.volume_value_label.configure(text=f"Âm lượng: {volume_value} ({description})")
    
    def _apply_volume(self):
        """Áp dụng thay đổi Volume khi nhấn nút Áp Dụng."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            volume_value = int(round(self.volume_slider.get()))
            
            print(f"🔊 Applying music volume: {volume_value}")
            
            # Thực hiện chỉnh Volume
            success = self.volume_detector.set_volume(volume_value)
            
            if success:
                print(f"✅ Music volume set to {volume_value} successfully")
            else:
                print(f"❌ Failed to set music volume to {volume_value}")
                
        except Exception as e:
            print(f"❌ Error in volume adjustment: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _toggle_mute(self):
        """Toggle mute âm lượng nhạc."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            print("🔇 Toggling music mute...")
            
            # Thực hiện toggle mute
            success = self.volume_detector.toggle_mute()
            
            if success:
                print("✅ Music mute toggled successfully")
                # Update button text để phản ánh trạng thái
                current_text = self.mute_toggle_btn.cget("text")
                if "🔇" in current_text:
                    self.mute_toggle_btn.configure(text="🔊 Unmute")
                else:
                    self.mute_toggle_btn.configure(text="🔇 Mute")
            else:
                print("❌ Failed to toggle music mute")
                
        except Exception as e:
            print(f"❌ Error in mute toggle: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()

    def _on_bass_slider_change(self, value):
        """Callback khi bass slider thay đổi - chỉ cập nhật display."""
        bass_value = int(value)
        
        # Chỉ cập nhật display, không thực hiện action
        self.bass_value_label.configure(text=f"Bass: {bass_value}")
    
    def _apply_bass(self):
        """Áp dụng thay đổi Bass khi nhấn nút Áp Dụng."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            bass_value = int(round(self.bass_slider.get()))
            
            print(f"🔉 Applying bass value: {bass_value}")
            
            # Thực hiện chỉnh Bass qua ToneMicDetector
            success = self.tone_mic_detector.set_bass_value(bass_value)
            
            if success:
                print("✅ Bass applied successfully")
            else:
                print("❌ Failed to apply bass")
                
        except Exception as e:
            print(f"❌ Error in bass application: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _on_treble_slider_change(self, value):
        """Callback khi treble slider thay đổi - chỉ cập nhật display."""
        treble_value = int(value)
        
        # Chỉ cập nhật display, không thực hiện action
        self.treble_value_label.configure(text=f"Treble: {treble_value}")
    
    def _apply_treble(self):
        """Áp dụng thay đổi Treble khi nhấn nút Áp Dụng."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            treble_value = int(round(self.treble_slider.get()))
            
            print(f"🔊 Applying treble value: {treble_value}")
            
            # Thực hiện chỉnh Treble qua ToneMicDetector
            success = self.tone_mic_detector.set_treble_value(treble_value)
            
            if success:
                print("✅ Treble applied successfully")
            else:
                print("❌ Failed to apply treble")
                
        except Exception as e:
            print(f"❌ Error in treble application: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()

    def _on_volume_mic_slider_change(self, value):
        """Callback khi COMP (Compressor) slider thay đổi - chỉ cập nhật display."""
        volume_value = int(value)
        
        # Chỉ cập nhật display, không thực hiện action
        self.volume_mic_value_label.configure(text=f"COMP: {volume_value}")
    
    def _apply_volume_mic(self):
        """Áp dụng thay đổi COMP (Compressor) khi nhấn nút Áp Dụng."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            volume_value = int(round(self.volume_mic_slider.get()))
            
            print(f"🎛️ Applying COMP value: {volume_value}")
            
            # Thực hiện chỉnh COMP qua XvoxVolumeDetector
            success = self.xvox_volume_detector.set_volume_value(volume_value)
            
            if success:
                print("✅ COMP applied successfully")
            else:
                print("❌ Failed to apply volume mic")
                
        except Exception as e:
            print(f"❌ Error in volume mic application: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
    def _on_reverb_mic_slider_change(self, value):
        """Callback khi reverb mic slider thay đổi - chỉ cập nhật display."""
        reverb_value = int(value)
        
        # Chỉ cập nhật display, không thực hiện action
        self.reverb_mic_value_label.configure(text=f"Reverb: {reverb_value}")
    
    def _apply_reverb_mic(self):
        """Áp dụng thay đổi Reverb Mic khi nhấn nút Áp Dụng."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            # Lấy giá trị từ slider
            reverb_value = int(round(self.reverb_mic_slider.get()))
            
            print(f"🌊 Applying reverb mic value: {reverb_value}")
            
            # Thực hiện chỉnh Reverb qua ReverbDetector
            success = self.reverb_detector.set_reverb_value(reverb_value)
            
            if success:
                print("✅ Reverb mic applied successfully")
            else:
                print("❌ Failed to apply reverb mic")
                
        except Exception as e:
            print(f"❌ Error in reverb mic application: {e}")
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
    
    def _adjust_music_preset(self, music_type, direction):
        """Điều chỉnh mức preset của loại nhạc (direction: +1 hoặc -1)."""
        try:
            if direction > 0:
                success = self.music_presets_manager.increase_level(music_type)
            else:
                success = self.music_presets_manager.decrease_level(music_type)
            
            if success:
                self._update_music_preset_display(music_type)
                current_level = self.music_presets_manager.get_current_level(music_type)
                print(f"✅ {music_type} level adjusted to {current_level}")
            else:
                print(f"⚠️ Cannot adjust {music_type} level further")
                
        except Exception as e:
            print(f"❌ Error adjusting {music_type} preset: {e}")
    
    def _update_music_preset_display(self, music_type):
        """Cập nhật hiển thị mức preset hiện tại."""
        try:
            current_level = self.music_presets_manager.get_current_level(music_type)
            level_desc = self.music_presets_manager.get_level_description(current_level)
            level_str = self.music_presets_manager.get_level_string(current_level)
            
            display_text = f"Mức: {level_str} ({level_desc})"
            
            if music_type == 'bolero' and hasattr(self, 'bolero_level_label'):
                self.bolero_level_label.configure(text=display_text)
            elif music_type == 'nhac_tre' and hasattr(self, 'nhac_tre_level_label'):
                self.nhac_tre_level_label.configure(text=display_text)
                
        except Exception as e:
            print(f"❌ Error updating {music_type} display: {e}")
    
    def _apply_music_preset(self, music_type):
        """Áp dụng preset hiện tại của loại nhạc."""
        # Pause auto-detect during operation
        self.pause_auto_detect_for_manual_action()
        
        try:
            success = self.music_presets_manager.apply_preset(music_type, self)
            
            if success:
                current_level = self.music_presets_manager.get_current_level(music_type)
                level_str = self.music_presets_manager.get_level_string(current_level)
                level_desc = self.music_presets_manager.get_level_description(current_level)
                print(f"✅ Applied {music_type} preset level {level_str} ({level_desc})")
            else:
                print(f"❌ Failed to apply {music_type} preset")
                
        except Exception as e:
            print(f"❌ Error applying {music_type} preset: {e}")
        finally:
            # Resume auto-detect
            self.resume_auto_detect_after_manual_action()
    
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



import customtkinter as CTK
import threading
import time
from datetime import datetime

import config
from features.tone_detector import ToneDetector
from features.transpose_detector import TransposeDetector
from features.autotune_controls_detector import AutoTuneControlsDetector
from features.plugin_bypass_detector import PluginBypassDetector
from features.soundshifter_detector import SoundShifterDetector
from features.soundshifter_bypass_detector import SoundShifterBypassDetector
from features.proq3_bypass_detector import ProQ3BypassDetector
from features.xvox_detector import XVoxDetector
from features.volume_detector import VolumeDetector
from utils.settings_manager import SettingsManager
from utils.helpers import ConfigHelper, MessageHelper
from utils.bypass_toggle_manager import BypassToggleManager
from utils.debug_helper import DebugHelper
from utils.music_presets_manager import MusicPresetsManager
from utils.fast_batch_processor import FastBatchProcessor
from utils.ultra_fast_processor import UltraFastAutoTuneProcessor

class DebugWindow:
    """Cửa sổ debug log riêng biệt."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.text_widget = None
        self.log_buffer = []  # Buffer để lưu trữ logs
        self.max_lines = 1000  # Giới hạn số dòng log
        self.is_auto_scroll = True  # Auto scroll to bottom
        self._lock = threading.Lock()
    
    def create_window(self):
        """Tạo cửa sổ debug."""
        if self.window is None or not self.window.winfo_exists():
            self.window = CTK.CTkToplevel()
            self.window.title("Debug Console - Cubase Auto Tool")
            self.window.geometry("800x600")
            self.window.resizable(True, True)
            
            # Icon và style
            try:
                self.window.after(201, lambda: self.window.iconbitmap(''))
            except:
                pass
            
            # Main container
            main_frame = CTK.CTkFrame(self.window, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title
            title_label = CTK.CTkLabel(
                main_frame,
                text="🐛 Debug Console",
                font=("Arial", 16, "bold"),
                text_color="#FF9800"
            )
            title_label.pack(pady=(0, 10))
            
            # Controls frame
            controls_frame = CTK.CTkFrame(main_frame, fg_color="transparent")
            controls_frame.pack(fill="x", pady=(0, 10))
            
            # Clear button
            clear_btn = CTK.CTkButton(
                controls_frame,
                text="Clear Logs",
                command=self._clear_logs,
                width=100,
                height=30,
                fg_color="#E91E63",
                hover_color="#C2185B"
            )
            clear_btn.pack(side="left", padx=(0, 10))
            
            # Auto-scroll toggle
            self.auto_scroll_switch = CTK.CTkSwitch(
                controls_frame,
                text="Auto Scroll",
                command=self._toggle_auto_scroll,
                width=40,
                height=20
            )
            self.auto_scroll_switch.select()  # Default: ON
            self.auto_scroll_switch.pack(side="left", padx=(0, 10))
            
            # Export button
            export_btn = CTK.CTkButton(
                controls_frame,
                text="Export Logs",
                command=self._export_logs,
                width=100,
                height=30,
                fg_color="#4CAF50",
                hover_color="#45A049"
            )
            export_btn.pack(side="left")
            
            # Stats label
            self.stats_label = CTK.CTkLabel(
                controls_frame,
                text="Lines: 0",
                font=("Arial", 10),
                text_color="#888888"
            )
            self.stats_label.pack(side="right")
            
            # Text display frame with scrollbar
            text_frame = CTK.CTkFrame(main_frame, fg_color="#1E1E1E", corner_radius=8)
            text_frame.pack(fill="both", expand=True)
            
            # Create text widget with scrollbar
            self.text_widget = CTK.CTkTextbox(
                text_frame,
                font=("Consolas", 10),
                fg_color="#1E1E1E",
                text_color="#FFFFFF",
                corner_radius=0,
                wrap="word"
            )
            self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Load existing logs
            self._load_existing_logs()
            
            # Protocol để cleanup khi đóng
            self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            print("🐛 Debug window created successfully")
        else:
            # Nếu window đã tồn tại, đưa lên foreground
            self.window.lift()
            self.window.focus()
    
    def show(self):
        """Hiển thị cửa sổ debug."""
        self.create_window()
        if self.window:
            self.window.deiconify()  # Show if minimized
            self.window.lift()
            self.window.focus()
    
    def add_log(self, message, level="INFO"):
        """Thêm log message với thread-safe."""
        with self._lock:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Color coding based on level
            color = {
                "INFO": "#FFFFFF",
                "SUCCESS": "#4CAF50", 
                "WARNING": "#FF9800",
                "ERROR": "#F44336",
                "DEBUG": "#2196F3"
            }.get(level, "#FFFFFF")
            
            # Format message
            formatted_msg = f"[{timestamp}] [{level}] {message}\n"
            
            # Add to buffer
            self.log_buffer.append({
                'text': formatted_msg,
                'color': color,
                'timestamp': time.time()
            })
            
            # Limit buffer size
            if len(self.log_buffer) > self.max_lines:
                self.log_buffer.pop(0)
            
            # Update UI if window exists
            if self.text_widget:
                self._update_display()
    
    def _update_display(self):
        """Cập nhật hiển thị trong text widget."""
        if not self.text_widget:
            return
            
        try:
            # Clear and rebuild display
            self.text_widget.delete("1.0", "end")
            
            for log_entry in self.log_buffer:
                # Insert text (note: CTkTextbox doesn't support text coloring like tkinter Text)
                self.text_widget.insert("end", log_entry['text'])
            
            # Auto scroll to bottom if enabled
            if self.is_auto_scroll:
                self.text_widget.see("end")
            
            # Update stats
            self._update_stats()
            
        except Exception as e:
            print(f"Error updating debug display: {e}")
    
    def _load_existing_logs(self):
        """Load existing logs từ print statements."""
        # Thêm một số log mẫu để demo
        sample_logs = [
            ("🚀 Cubase Auto Tool started", "INFO"),
            ("✅ GUI initialized successfully", "SUCCESS"),
            ("🔧 Loading default values...", "INFO"),
            ("⚙️ Settings loaded", "INFO"),
            ("🎨 Theme applied: dark", "INFO")
        ]
        
        for msg, level in sample_logs:
            self.add_log(msg, level)
    
    def _clear_logs(self):
        """Xóa tất cả logs."""
        with self._lock:
            self.log_buffer.clear()
            if self.text_widget:
                self.text_widget.delete("1.0", "end")
                self._update_stats()
        print("🧹 Debug logs cleared")
    
    def _toggle_auto_scroll(self):
        """Toggle auto scroll."""
        self.is_auto_scroll = self.auto_scroll_switch.get()
        print(f"📜 Auto scroll: {'ON' if self.is_auto_scroll else 'OFF'}")
    
    def _export_logs(self):
        """Export logs to file."""
        try:
            filename = f"debug_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Cubase Auto Tool Debug Logs\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                for log_entry in self.log_buffer:
                    f.write(log_entry['text'])
            
            print(f"📄 Logs exported to: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting logs: {e}")
    
    def _update_stats(self):
        """Cập nhật statistics."""
        if self.stats_label:
            line_count = len(self.log_buffer)
            self.stats_label.configure(text=f"Lines: {line_count}")
    
    def _on_window_close(self):
        """Xử lý khi đóng cửa sổ."""
        if self.window:
            self.window.withdraw()  # Hide instead of destroy
            print("🐛 Debug window hidden")

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
        self.root.geometry("1200x600")  # Kích thước tối ưu cho 1 tab
        self.root.resizable(False, False)
        
        # Đảm bảo cửa sổ luôn hiển thị trên top khi khởi động
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        # Bind theme shortcut key (Ctrl+T)
        self.root.bind("<Control-t>", lambda event: self._toggle_theme())
        
        # Bind topmost toggle key (Ctrl+Shift+T)
        self.root.bind("<Control-Shift-T>", lambda event: self._toggle_topmost_mode())
        
        # Track topmost state
        self.is_topmost = True
        
        self.tone_detector = ToneDetector()
        self.transpose_detector = TransposeDetector()
        self.autotune_controls_detector = AutoTuneControlsDetector()
        self.plugin_bypass_detector = PluginBypassDetector()
        self.soundshifter_detector = SoundShifterDetector()
        self.soundshifter_bypass_detector = SoundShifterBypassDetector()
        self.proq3_bypass_detector = ProQ3BypassDetector()
        self.xvox_detector = XVoxDetector()
        self.volume_detector = VolumeDetector()
        
        # Initialize bypass toggle manager
        self.bypass_manager = BypassToggleManager(self)
        
        # Initialize music presets manager
        self.music_presets_manager = MusicPresetsManager()
        
        # UI element references
        self.current_tone_label = None
        self.transpose_value_label = None
        self.return_speed_value_label = None
        self.soundshifter_value_label = None
        
        # Plugin bypass toggle state
        self.plugin_bypass_toggle = None
        self.plugin_bypass_state = False
        
        # SoundShifter bypass toggle state
        self.soundshifter_bypass_toggle = None
        self.soundshifter_bypass_state = False
        
        # ProQ3 bypass toggle state
        self.proq3_bypass_toggle = None
        self.proq3_bypass_state = False
        self.flex_tune_value_label = None
        self.natural_vibrato_value_label = None
        self.humanize_value_label = None
        self.auto_detect_switch = None
        self.current_detected_tone = "--"
        
        # Audio control labels
        self.xvox_volume_label = None
        self.reverb_value_label = None
        
        # Set current theme index based on saved theme
        try:
            self.current_theme_index = config.GUI_THEMES.index(saved_theme)
        except ValueError:
            self.current_theme_index = 0
            
        self.theme_button = None
        
        # Initialize debug window
        self.debug_window = DebugWindow(self)
        
        # Override print function to capture debug output
        self._setup_debug_logging()
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Main container frame
        main_frame = CTK.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main content frame
        content_frame = CTK.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid layout - 3 columns for main sections
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)
        
        # Create 3 main sections
        self._create_autotune_section(content_frame)
        self._create_music_section(content_frame)
        self._create_vocal_section(content_frame)
        
        # Setup footer
        self._setup_footer()
        
        # Initialize plugin toggle state
        self._initialize_plugin_toggle_state()
        
        # Tắt topmost mode sau khi UI đã setup xong
        self.root.after(1000, self._disable_topmost_mode)
    
    def _create_autotune_section(self, parent):
        """Tạo section Auto-Tune."""
        # Section frame
        section_frame = CTK.CTkFrame(parent, corner_radius=10, border_width=1, border_color="#404040")
        section_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Section title
        title_label = CTK.CTkLabel(
            section_frame,
            text="Auto-Tune",
            font=("Arial", 16, "bold"),
            text_color="#FF6B6B"
        )
        title_label.pack(pady=(10, 15))
        
        # Content frame
        content_frame = CTK.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Tone hiện tại và Tự động dò
        top_row = CTK.CTkFrame(content_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))
        
        # Current Tone Display
        self.current_tone_label = CTK.CTkLabel(
            top_row,
            text="Tone: --",
            font=("Arial", 12, "bold"),
            text_color="#2CC985"
        )
        self.current_tone_label.pack(side="left")
        
        # Auto Detect Toggle
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
        
        # Khung chứa nút Dò Tone
        main_buttons_frame = CTK.CTkFrame(content_frame, fg_color="transparent")
        main_buttons_frame.pack(pady=(0, 10))
        
        # Nút Dò Tone
        btn_tone = CTK.CTkButton(
            main_buttons_frame,
            text=self.tone_detector.get_name(),
            font=("Arial", 11, "bold"),
            command=self._execute_tone_detector,
            width=120,
            height=35
        )
        btn_tone.pack(side="left", padx=(0, 10))
        
        # Bypass Controls Section
        bypass_section_title = CTK.CTkLabel(
            content_frame,
            text="Điều Khiển Plugin",
            font=("Arial", 14, "bold"),
            text_color="#FF9800"
        )
        bypass_section_title.pack(pady=(0, 10))
        
        # Bypass controls frame
        bypass_controls_frame = CTK.CTkFrame(content_frame, fg_color="#2B2B2B", corner_radius=8, border_width=1, border_color="#404040")
        bypass_controls_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Container for the 3 bypass toggles
        toggles_container = CTK.CTkFrame(bypass_controls_frame, fg_color="transparent")
        toggles_container.pack(pady=15, padx=15)
        
        # Configure grid for 4 columns
        toggles_container.grid_columnconfigure(0, weight=1)
        toggles_container.grid_columnconfigure(1, weight=1) 
        toggles_container.grid_columnconfigure(2, weight=1)
        toggles_container.grid_columnconfigure(3, weight=1)
        
        # 1. Auto-tune Bypass (Plugin Bypass)
        autotune_frame = CTK.CTkFrame(toggles_container, fg_color="transparent")
        autotune_frame.grid(row=0, column=0, padx=10, pady=5)
        
        autotune_label = CTK.CTkLabel(
            autotune_frame,
            text="Auto-tune",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF"
        )
        autotune_label.pack(pady=(0, 5))
        
        self.plugin_bypass_toggle = CTK.CTkSwitch(
            autotune_frame,
            text="",
            command=lambda: self.bypass_manager.toggle_bypass('plugin'),
            width=50,
            height=24,
            fg_color="#FF4444",
            progress_color="#44FF44"
        )
        self.plugin_bypass_toggle.pack(pady=(0, 5))
        
        self.plugin_state_label = CTK.CTkLabel(
            autotune_frame,
            text="ON",
            font=("Arial", 8, "bold"),
            text_color="#44FF44",
            fg_color="#2B2B2B",
            corner_radius=3,
            width=60,
            height=20
        )
        self.plugin_state_label.pack()
        
        # 2. Tone nhạc (SoundShifter Bypass)
        tone_nhac_frame = CTK.CTkFrame(toggles_container, fg_color="transparent")
        tone_nhac_frame.grid(row=0, column=1, padx=10, pady=5)
        
        tone_nhac_label = CTK.CTkLabel(
            tone_nhac_frame,
            text="Tone nhạc",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF"
        )
        tone_nhac_label.pack(pady=(0, 5))
        
        self.soundshifter_bypass_toggle = CTK.CTkSwitch(
            tone_nhac_frame,
            text="",
            command=lambda: self.bypass_manager.toggle_bypass('soundshifter'),
            width=50,
            height=24,
            fg_color="#FF4444",
            progress_color="#44FF44"
        )
        self.soundshifter_bypass_toggle.pack(pady=(0, 5))
        
        self.soundshifter_bypass_status_label = CTK.CTkLabel(
            tone_nhac_frame,
            text="ON",
            font=("Arial", 8, "bold"),
            text_color="#44FF44",
            fg_color="#2B2B2B",
            corner_radius=3,
            width=60,
            height=20
        )
        self.soundshifter_bypass_status_label.pack()
        
        # 3. Lofi (ProQ3 Bypass)
        lofi_frame = CTK.CTkFrame(toggles_container, fg_color="transparent")
        lofi_frame.grid(row=0, column=2, padx=10, pady=5)
        
        lofi_label = CTK.CTkLabel(
            lofi_frame,
            text="Lofi",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF"
        )
        lofi_label.pack(pady=(0, 5))
        
        self.proq3_bypass_toggle = CTK.CTkSwitch(
            lofi_frame,
            text="",
            command=lambda: self.bypass_manager.toggle_bypass('proq3'),
            width=50,
            height=24,
            fg_color="#FF4444",
            progress_color="#44FF44"
        )
        self.proq3_bypass_toggle.pack(pady=(0, 5))
        
        self.proq3_bypass_status_label = CTK.CTkLabel(
            lofi_frame,
            text="ON",
            font=("Arial", 8, "bold"),
            text_color="#44FF44",
            fg_color="#2B2B2B",
            corner_radius=3,
            width=60,
            height=20
        )
        self.proq3_bypass_status_label.pack()
        
        # 4. Transpose (Chuyển Giọng)
        transpose_frame = CTK.CTkFrame(toggles_container, fg_color="transparent")
        transpose_frame.grid(row=0, column=3, padx=10, pady=5)
        
        transpose_label = CTK.CTkLabel(
            transpose_frame,
            text="Chuyển Giọng",
            font=("Arial", 10, "bold"),
            text_color="#FFFFFF"
        )
        transpose_label.pack(pady=(0, 5))
        
        # Transpose value display (compact)
        self.transpose_value_label = CTK.CTkLabel(
            transpose_frame,
            text="Giá trị: 0",
            font=("Arial", 8),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=3,
            width=60,
            height=20
        )
        self.transpose_value_label.pack(pady=(0, 5))
        
        # Transpose slider (compact)
        self.pitch_slider = CTK.CTkSlider(
            transpose_frame,
            from_=self.default_values.get('transpose_min', -12),
            to=self.default_values.get('transpose_max', 12),
            number_of_steps=abs(self.default_values.get('transpose_min', -12)) + abs(self.default_values.get('transpose_max', 12)),
            command=self._on_pitch_slider_change,
            width=120,
            height=16,
            button_color="#9C27B0",
            button_hover_color="#7B1FA2",
            progress_color="#9C27B0"
        )
        self.pitch_slider.set(self.default_values.get('transpose_default', 0))
        self.pitch_slider.pack(pady=(0, 5))
        
        # Transpose Apply Button (compact)
        btn_apply_pitch = CTK.CTkButton(
            transpose_frame,
            text="Áp Dụng",
            font=("Arial", 8, "bold"),
            command=self._apply_pitch_change,
            width=60,
            height=20,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        btn_apply_pitch.pack()
        
        # Separator
        separator = CTK.CTkFrame(content_frame, height=2, fg_color="#404040")
        separator.pack(fill="x", pady=(0, 10))
        
        # Music Presets Frame
        presets_frame = CTK.CTkFrame(content_frame, fg_color="#2B2B2B", corner_radius=8, border_width=1, border_color="#404040")
        presets_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Setup Music Presets controls
        self._setup_music_presets_controls(presets_frame)
        

    
    def _create_music_section(self, parent):
        """Tạo section Nhạc."""
        # Section frame
        section_frame = CTK.CTkFrame(parent, corner_radius=10, border_width=1, border_color="#404040")
        section_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Section title
        title_label = CTK.CTkLabel(
            section_frame,
            text="Nhạc",
            font=("Arial", 16, "bold"),
            text_color="#FF6B6B"
        )
        title_label.pack(pady=(10, 15))
        
        # Content frame
        content_frame = CTK.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Tone nhạc Section Container
        tone_nhac_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#FF6B6B")
        tone_nhac_container.pack(fill="x", pady=(0, 10), padx=5)
        
        # Tone nhạc Title
        tone_nhac_title = CTK.CTkLabel(
            tone_nhac_container,
            text="Tone nhạc",
            font=("Arial", 12, "bold"),
            text_color="#FF6B6B"
        )
        tone_nhac_title.pack(pady=(10, 5))
        
        # Current value display
        self.soundshifter_value_label = CTK.CTkLabel(
            tone_nhac_container,
            text="Mức: 0 (Bình thường)",
            font=("Arial", 10),
            text_color="#FFFFFF",
            fg_color="#2B2B2B",
            corner_radius=4,
            width=160,
            height=22
        )
        self.soundshifter_value_label.pack(pady=(0, 10))
        
        # Tone nhạc Controls Frame
        tone_nhac_controls = CTK.CTkFrame(tone_nhac_container, fg_color="transparent")
        tone_nhac_controls.pack(pady=(0, 10))
        
        # Tone nhạc Buttons Row
        tone_nhac_buttons = CTK.CTkFrame(tone_nhac_controls, fg_color="transparent")
        tone_nhac_buttons.pack()
        
        # Hạ Tone Button (-)
        btn_lower = CTK.CTkButton(
            tone_nhac_buttons,
            text="-",
            font=("Arial", 14, "bold"),
            command=self._lower_tone,
            width=35,
            height=30,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        btn_lower.pack(side="left", padx=(0, 5))
        
        # Reset Button
        btn_reset = CTK.CTkButton(
            tone_nhac_buttons,
            text="Reset",
            font=("Arial", 10, "bold"),
            command=self._reset_soundshifter,
            width=80,
            height=30,
            fg_color="#9E9E9E",
            hover_color="#757575"
        )
        btn_reset.pack(side="left", padx=(0, 5))
        
        # Nâng Tone Button (+)
        btn_raise = CTK.CTkButton(
            tone_nhac_buttons,
            text="+",
            font=("Arial", 14, "bold"),
            command=self._raise_tone,
            width=35,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        btn_raise.pack(side="left")
        

        
        # Separator
        separator = CTK.CTkFrame(content_frame, height=2, fg_color="#404040")
        separator.pack(fill="x", pady=(0, 15))
        
        # Volume Section
        volume_title = CTK.CTkLabel(
            content_frame,
            text="Âm Lượng Nhạc",
            font=("Arial", 14, "bold"),
            text_color="#FF9800"
        )
        volume_title.pack(pady=(0, 10))
        
        # Volume value display
        self.volume_value_label = CTK.CTkLabel(
            content_frame,
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
            content_frame,
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
        volume_buttons_frame = CTK.CTkFrame(content_frame, fg_color="transparent")
        volume_buttons_frame.pack(pady=(0, 15))
        
        # Volume Apply Button
        self.volume_apply_btn = CTK.CTkButton(
            volume_buttons_frame,
            text="Áp Dụng",
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
            text="Mute",
            font=("Arial", 10, "bold"),
            command=self._toggle_mute,
            width=80,
            height=30,
            fg_color="#E91E63",
            hover_color="#C2185B"
        )
        self.mute_toggle_btn.pack(side="left")
    
    def _create_vocal_section(self, parent):
        """Tạo section Giọng hát."""
        # Section frame
        section_frame = CTK.CTkFrame(parent, corner_radius=10, border_width=1, border_color="#404040")
        section_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # Section title
        title_label = CTK.CTkLabel(
            section_frame,
            text="Giọng hát",
            font=("Arial", 16, "bold"),
            text_color="#FF6B6B"
        )
        title_label.pack(pady=(10, 15))
        
        # Content frame
        content_frame = CTK.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Mic Controls Title
        mic_controls_title = CTK.CTkLabel(
            content_frame,
            text="Điều Chỉnh Mic",
            font=("Arial", 14, "bold"),
            text_color="#00BCD4"
        )
        mic_controls_title.pack(pady=(0, 10))
        
        # Mic controls grid frame (2x2 layout)
        mic_controls_grid = CTK.CTkFrame(content_frame, fg_color="transparent")
        mic_controls_grid.pack(pady=(0, 15))
        
        # Configure grid for 2x2 layout (Bass, Treble, Volume, Reverb)
        mic_controls_grid.grid_columnconfigure(0, weight=1)
        mic_controls_grid.grid_columnconfigure(1, weight=1)
        mic_controls_grid.grid_rowconfigure(0, weight=1)
        mic_controls_grid.grid_rowconfigure(1, weight=1)
        
        # === BASS CONTROL (Top Left) ===
        bass_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        bass_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 5))
        
        bass_label = CTK.CTkLabel(
            bass_frame,
            text="Bass (LOW)",
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
            text="Áp Dụng",
            font=("Arial", 9, "bold"),
            command=self._apply_bass,
            width=120,
            height=25,
            fg_color="#00BCD4",
            hover_color="#00ACC1"
        )
        self.bass_apply_btn.pack()
        
        # === TREBLE CONTROL (Top Right) ===
        treble_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        treble_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 5))
        
        treble_label = CTK.CTkLabel(
            treble_frame,
            text="Treble (HIGH)",
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
            text="Áp Dụng",
            font=("Arial", 9, "bold"),
            command=self._apply_treble,
            width=120,
            height=25,
            fg_color="#00BCD4",
            hover_color="#00ACC1"
        )
        self.treble_apply_btn.pack()
        
        # === VOLUME MIC CONTROL (Bottom Left) ===
        volume_mic_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        volume_mic_frame.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(5, 0))
        
        volume_mic_label = CTK.CTkLabel(
            volume_mic_frame,
            text="Âm lượng Mic",
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
            text="Áp Dụng",
            font=("Arial", 9, "bold"),
            command=self._apply_volume_mic,
            width=120,
            height=25,
            fg_color="#FF69B4",
            hover_color="#E91E63"
        )
        self.volume_mic_apply_btn.pack()
        
        # === REVERB CONTROL (Bottom Right) ===
        reverb_mic_frame = CTK.CTkFrame(mic_controls_grid, fg_color="transparent")
        reverb_mic_frame.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
        
        reverb_mic_label = CTK.CTkLabel(
            reverb_mic_frame,
            text="Độ vang Mic",
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
            text="Áp Dụng",
            font=("Arial", 9, "bold"),
            command=self._apply_reverb_mic,
            width=120,
            height=25,
            fg_color="#00CED1",
            hover_color="#00BCD4"
        )
        self.reverb_mic_apply_btn.pack()
        

        

    
    def _setup_music_presets_controls(self, parent):
        """Thiết lập Music Presets controls với thiết kế đồng bộ."""
        
        # Padding cho toàn bộ section
        content_frame = CTK.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize sliders for compatibility (hidden)
        self._init_hidden_sliders(content_frame)
        
        # Configure grid layout - 2 columns for music controls
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # === NHẠC BOLERO SECTION (Left Column) ===
        bolero_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#FF6B6B")
        bolero_container.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=5)
        
        bolero_title = CTK.CTkLabel(
            bolero_container,
            text="Nhạc Bolero",
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
            text="-",
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
            text="+",
            font=("Arial", 14, "bold"),
            command=lambda: self._adjust_music_preset('bolero', 1),
            width=35,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        self.bolero_plus_btn.pack(side="left")
        
        # === NHẠC TRẺ SECTION (Right Column) ===
        nhac_tre_container = CTK.CTkFrame(content_frame, fg_color="#1A1A1A", corner_radius=8, border_width=1, border_color="#32CD32")
        nhac_tre_container.grid(row=0, column=1, sticky="nsew", padx=(2, 0), pady=5)
        
        nhac_tre_title = CTK.CTkLabel(
            nhac_tre_container,
            text="Nhạc Trẻ",
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
            text="-",
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
            text="+",
            font=("Arial", 14, "bold"),
            command=lambda: self._adjust_music_preset('nhac_tre', 1),
            width=35,
            height=30,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        self.nhac_tre_plus_btn.pack(side="left")
        
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
    
    def _setup_footer(self):
        """Thiết lập footer đơn giản."""
        # Footer container
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
        
        # Debug button (next to theme)
        self.debug_button = CTK.CTkButton(
            footer_frame,
            text="Debug",
            command=self._show_debug_window,
            width=60,
            height=20,
            font=("Arial", 10),
            corner_radius=4,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        self.debug_button.pack(side="left", padx=(5, 0))
        
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
            font=("Arial", 14, "bold"),
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
                copyright_label.configure(text="Đã copy số!", text_color="#00aa00")
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
    
    def _batch_reset_autotune_parameters(self):
        """Ultra fast batch reset tất cả parameters Auto-Tune."""
        
        # Prepare ultra fast batch parameters
        reset_configs = [
            ('Return Speed', self.autotune_controls_detector.return_speed_detector, 'return_speed_default', 200),
            ('Flex Tune', self.autotune_controls_detector.flex_tune_detector, 'flex_tune_default', 0),
            ('Natural Vibrato', self.autotune_controls_detector.natural_vibrato_detector, 'natural_vibrato_default', 0),
            ('Humanize', self.autotune_controls_detector.humanize_detector, 'humanize_default', 0),
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
            (self.autotune_controls_detector.return_speed_detector, self.return_speed_slider, self._on_return_speed_slider_change, 'return_speed_default', 200, 'Return Speed'),
            (self.autotune_controls_detector.flex_tune_detector, self.flex_tune_slider, self._on_flex_tune_slider_change, 'flex_tune_default', 0, 'Flex Tune'),
            (self.autotune_controls_detector.natural_vibrato_detector, self.natural_vibrato_slider, self._on_natural_vibrato_slider_change, 'natural_vibrato_default', 0, 'Natural Vibrato'),
            (self.autotune_controls_detector.humanize_detector, self.humanize_slider, self._on_humanize_slider_change, 'humanize_default', 0, 'Humanize')
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
        
        # Cập nhật label với format ngắn gọn
        if self.transpose_value_label:
            self.transpose_value_label.configure(text=f"Giá trị: {pitch_value}")
    
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
            success = self.autotune_controls_detector.set_return_speed_value(speed_value)
            
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
            success = self.autotune_controls_detector.set_flex_tune_value(flex_value)
            
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
            success = self.autotune_controls_detector.set_natural_vibrato_value(vibrato_value)
            
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
            success = self.autotune_controls_detector.set_humanize_value(humanize_value)
            
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
        
        # Restore original print function
        if hasattr(self, '_original_print'):
            import builtins
            builtins.print = self._original_print
            
        # Close debug window if open
        if hasattr(self, 'debug_window') and self.debug_window and self.debug_window.window:
            try:
                self.debug_window.window.destroy()
            except:
                pass
        
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
                if "Mute" in current_text:
                    self.mute_toggle_btn.configure(text="Unmute")
                else:
                    self.mute_toggle_btn.configure(text="Mute")
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
            success = self.xvox_detector.set_bass_value(bass_value)
            
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
            
            # Thực hiện chỉnh Treble qua XVoxDetector
            success = self.xvox_detector.set_treble_value(treble_value)
            
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
            
            # Thực hiện chỉnh COMP qua XVoxDetector
            success = self.xvox_detector.set_comp_value(volume_value)
            
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
            
            # Thực hiện chỉnh Reverb qua XVoxDetector
            success = self.xvox_detector.set_reverb_value(reverb_value)
            
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
        """Cập nhật hiển thị giá trị Tone nhạc."""
        if self.soundshifter_value_label:
            current_value = self.soundshifter_detector.current_value
            description = self.soundshifter_detector.get_tone_description(current_value)
            self.soundshifter_value_label.configure(text=f"Mức: {current_value} ({description})")
    
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
    
    def _setup_debug_logging(self):
        """Thiết lập hệ thống debug logging để capture print statements."""
        import builtins
        
        # Lưu original print function
        self._original_print = builtins.print
        
        def debug_print(*args, **kwargs):
            """Custom print function để capture debug output."""
            # Call original print
            self._original_print(*args, **kwargs)
            
            # Extract message và level
            message = ' '.join(str(arg) for arg in args)
            
            # Determine log level based on message content
            level = "INFO"
            if any(indicator in message for indicator in ["✅", "Success", "completed successfully"]):
                level = "SUCCESS"
            elif any(indicator in message for indicator in ["❌", "Error", "Failed", "failed"]):
                level = "ERROR"
            elif any(indicator in message for indicator in ["⚠️", "Warning", "Cannot"]):
                level = "WARNING"
            elif any(indicator in message for indicator in ["🐛", "Debug", "debug"]):
                level = "DEBUG"
            
            # Add to debug window
            if hasattr(self, 'debug_window') and self.debug_window:
                try:
                    self.debug_window.add_log(message, level)
                except:
                    pass  # Fail silently nếu có lỗi
        
        # Replace built-in print
        builtins.print = debug_print
        
        print("🐛 Debug logging system initialized")
    
    def _show_debug_window(self):
        """Hiển thị cửa sổ debug."""
        try:
            if self.debug_window:
                self.debug_window.show()
            print("🐛 Debug window opened")
        except Exception as e:
            print(f"❌ Error opening debug window: {e}")
    
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
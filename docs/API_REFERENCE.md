# 📚 API REFERENCE - Complete Classes & Methods Documentation

> **Chi tiết tất cả classes, methods, parameters với examples cụ thể**

---

## 📋 Mục lục

1. [**GUI Layer**](#-gui-layer)
2. [**Feature Classes**](#-feature-classes)
3. [**Utility Classes**](#-utility-classes)
4. [**Configuration**](#-configuration)
5. [**Examples & Usage**](#-examples--usage)

---

## 🖥️ GUI Layer

### `CubaseAutoToolGUI` (gui.py)

**Main GUI class sử dụng CustomTkinter framework**

#### Constructor
```python
def __init__(self):
    """Khởi tạo GUI với settings manager và detector instances"""
```

#### Core Methods

##### Settings Management
```python
def load_settings(self) -> None:
    """Load user settings từ settings.json"""

def save_settings(self) -> None:
    """Save current settings to settings.json"""

def on_closing(self) -> None:
    """Cleanup khi đóng app: stop auto-detect, save settings"""
```

##### Feature Integration
```python
def _execute_tone_detector(self) -> None:
    """
    Chạy manual tone detection với auto-pause system
    Flow: pause auto → execute → resume auto
    """

def _toggle_auto_detect(self) -> None:
    """
    Bật/tắt auto-detect mode
    Updates UI toggle switch và starts/stops background thread
    """

def update_current_tone(self, tone: str) -> None:
    """
    Cập nhật display tone hiện tại trên GUI
    Args:
        tone: String format "A Major" hoặc "C Minor"
    """
```

##### Auto-Pause System
```python
def pause_auto_detect_for_manual_action(self) -> None:
    """Tạm dừng auto-detect cho manual operations"""

def resume_auto_detect_after_manual_action(self) -> None:
    """Khôi phục auto-detect sau manual operations"""
```

##### Plugin Controllers
```python
# Auto-Tune Section
def _raise_tone(self) -> None:
    """Tăng tone Auto-Tune (+1)"""
    
def _lower_tone(self) -> None:
    """Giảm tone Auto-Tune (-1)"""
    
def _reset_auto_tune(self) -> None:
    """Reset Auto-Tune về 0"""

# Music Section  
def _raise_tone(self) -> None:
    """SoundShifter tăng tone (+2)"""
    
def _lower_tone(self) -> None:
    """SoundShifter giảm tone (-2)"""
    
def _reset_soundshifter(self) -> None:
    """Reset SoundShifter về 0"""

# Voice Section
def _toggle_bypass(self) -> None:
    """Toggle plugin bypass ON/OFF"""
    
def _revert_toggle_state(self) -> None:
    """Revert bypass toggle state (fix infinite loop)"""
```

---

## 🎵 Feature Classes

### `BaseFeature` (features/base_feature.py)

**Abstract base class cho tất cả plugin detectors**

#### Abstract Interface
```python
class BaseFeature(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """Return tên hiển thị của feature"""
        pass
```

#### Template Method Pattern
```python
def execute(self) -> bool:
    """
    Template method định nghĩa workflow chung:
    1. Find Cubase process
    2. Focus Cubase window  
    3. Find template match
    4. Perform action
    
    Returns:
        bool: True if successful, False otherwise
    """
```

### `ToneDetector` (features/tone_detector.py)

**Plugin detector cho AUTO-KEY tone detection và auto-click**

#### Constructor & Properties
```python
def __init__(self):
    """
    Initialize với thread safety components:
    - _detection_lock: Threading.Lock for mutual exclusion
    - _manual_active: Flag cho manual operations
    - auto_detect_active: Flag cho auto-detect state
    - auto_detect_thread: Background thread
    """
```

#### Core Methods

##### Manual Detection
```python
def execute(self, tone_callback=None) -> bool:
    """
    Thực thi manual tone detection workflow
    
    Args:
        tone_callback: Callback function để update UI
        
    Returns:
        bool: Success status
        
    Flow:
        1. Set manual flag và acquire lock
        2. Find Cubase process
        3. Focus Cubase window
        4. Find AUTO-KEY plugin window
        5. Screenshot và OCR
        6. Click detected tone
        7. Click Send button
        8. Release lock và reset flags
    """
```

##### Auto-Detection System
```python
def start_auto_detect(self, tone_callback=None, current_tone_getter=None) -> None:
    """
    Bật auto-detect background monitoring
    
    Args:
        tone_callback: Function để update UI với tone mới
        current_tone_getter: Function để lấy current app tone
    """

def stop_auto_detect(self) -> None:
    """Dừng auto-detect thread và cleanup"""

def _auto_detect_loop(self) -> None:
    """
    Background thread loop:
    - Check manual operation flags
    - Acquire detection lock (non-blocking)
    - OCR current tone từ plugin
    - Compare với app current tone
    - Auto-send nếu khác nhau
    - Sleep và repeat
    """
```

##### OCR & Template Processing
```python
def _extract_current_tone(self, words_list: List[str]) -> Optional[str]:
    """
    Trích xuất tone từ OCR text data
    
    Args:
        words_list: List các từ từ OCR
        
    Returns:
        Optional[str]: Tone format "A Major" hoặc None
        
    Logic:
        1. Tìm markers "AUTO-KEY" và "Send"  
        2. Lấy text giữa 2 markers
        3. Parse note (A, B, C, D, E, F, G) + mode (Major, Minor)
        4. Combine và return
    """

def _find_and_click_tone(self, ocr_data, left, top, crop_box) -> bool:
    """
    Tìm và click tone button với listening detection
    
    Args:
        ocr_data: OCR result data
        left, top: Window coordinates
        crop_box: Crop region coordinates
        
    Returns:
        bool: Click success status
        
    Features:
        - Wait for "Listening" state completion
        - Find Major/Minor buttons
        - Calculate click coordinates
        - Safe click với MouseHelper
    """

def _is_listening(self, ocr_data) -> bool:
    """
    Kiểm tra plugin có đang ở listening state không
    
    Args:
        ocr_data: OCR result data
        
    Returns:
        bool: True if listening state detected
        
    Keywords: "listening", "analyzing", "processing", "detecting"
    """

def _wait_for_listening_complete(self, max_wait_time=30, check_interval=1.0) -> bool:
    """
    Đợi cho listening state hoàn tất
    
    Args:
        max_wait_time: Maximum wait time in seconds
        check_interval: Check interval in seconds
        
    Returns:
        bool: True if completed, False if timeout
    """
```

##### Screenshot & Cropping
```python
def _screenshot_and_crop_plugin(self, plugin_win):
    """
    Screenshot plugin window và crop theo config margins
    
    Args:
        plugin_win: Window object
        
    Returns:
        Tuple[PIL.Image, Tuple]: (cropped_image, (left, top, crop_box))
    """

def _calculate_crop_box(self, win_w, win_h) -> Tuple[int, int, int, int]:
    """
    Tính crop box coordinates từ window size
    
    Args:
        win_w, win_h: Window width và height
        
    Returns:
        Tuple[int, int, int, int]: (left, top, right, bottom)
    """
```

##### Thread Safety
```python
def pause_auto_detect(self) -> None:
    """Set flag để auto-detect nhường quyền cho manual operations"""

def resume_auto_detect(self) -> None:
    """Clear flag để auto-detect tiếp tục sau manual"""
```

### `AutoTuneDetector` (features/auto_tune_detector.py)

**Controller cho Auto-Tune Pro plugin**

#### Core Methods
```python
def raise_tone(self) -> bool:
    """Tăng tone Auto-Tune +1 semitone"""

def lower_tone(self) -> bool:
    """Giảm tone Auto-Tune -1 semitone"""

def reset_pitch(self) -> bool:
    """Reset pitch correction về 0"""

def _find_template_match(self) -> bool:
    """Find Auto-Tune plugin interface bằng template matching"""

def _perform_action(self, action: str) -> bool:
    """
    Perform specific action trên Auto-Tune interface
    
    Args:
        action: "raise", "lower", hoặc "reset"
    """
```

### `SoundShifterDetector` (features/soundshifter_detector.py)

**Controller cho SoundShifter Pitch Stereo plugin**

#### Inheritance & Overrides
```python
class SoundShifterDetector(AutoTuneDetector):
    """Inherit từ AutoTuneDetector, override specific behaviors"""
```

#### Core Methods
```python
def raise_tone(self) -> bool:
    """Tăng pitch +2 per tone (±4 range)"""

def lower_tone(self) -> bool:  
    """Giảm pitch -2 per tone (±4 range)"""

def set_pitch_value(self, target_value: int) -> bool:
    """
    Set exact pitch value bằng double-click input
    
    Args:
        target_value: Target pitch value (-4 to +4)
        
    Returns:
        bool: Success status
        
    Method:
        - Double-click input field
        - Clear existing value
        - Type new value
        - Press Enter
    """

def get_tone_description(self, value: int) -> str:
    """
    Convert pitch value sang tone description
    
    Args:
        value: Pitch value (-4 to +4)
        
    Returns:
        str: Description như "Giảm 2 tone" hoặc "Tăng 1 tone"
    """
```

#### Overridden Methods
```python
def _find_template_match(self) -> Optional[Tuple]:
    """
    Override parent method với 40% click position
    Template: soundshifter_pitch_template.png
    Click position: 40% từ trên xuống (thay vì 50%)
    """
```

### `PluginBypassDetector` (features/plugin_bypass_detector.py)

**Controller cho plugin bypass toggle functionality**

#### Core Methods
```python
def toggle_bypass(self) -> bool:
    """
    Toggle plugin bypass ON/OFF với dual template detection
    
    Returns:
        bool: Toggle success status
        
    Templates:
        - bypass_on_template.png: Bypass enabled state
        - bypass_off_template.png: Bypass disabled state
        
    Logic:
        1. Detect current bypass state
        2. Click appropriate button
        3. Verify state change
    """

def get_current_state(self, silent=True) -> Optional[str]:
    """
    Get current bypass state
    
    Args:
        silent: If True, suppress error messages
        
    Returns:
        Optional[str]: "ON", "OFF", hoặc None
    """

def _revert_toggle_state(self) -> None:
    """
    Revert toggle state để fix infinite loop bug
    Called from GUI khi cần reset toggle callbacks
    """
```

#### Template Detection
```python
def _find_cubase_process_silent(self) -> Optional[Any]:
    """Silent version của process finding (no error popups)"""

def _detect_bypass_state(self) -> Optional[str]:
    """
    Detect bypass state bằng template matching
    
    Returns:
        "ON" if bypass enabled
        "OFF" if bypass disabled  
        None if không detect được
    """
```

### Other Plugin Detectors

#### `TransposeDetector`
```python
def transpose_up(self) -> bool:
    """Transpose lên +1 semitone"""

def transpose_down(self) -> bool:
    """Transpose xuống -1 semitone"""
```

#### `FlexTuneDetector`
```python
def adjust_flex_tune(self, direction: str) -> bool:
    """Adjust FlexTune parameter"""
```

#### `NaturalVibratoDetector` 
```python
def adjust_vibrato(self, amount: float) -> bool:
    """Adjust natural vibrato amount"""
```

#### `HumanizeDetector`
```python
def toggle_humanize(self) -> bool:
    """Toggle humanization ON/OFF"""
```

#### `ReturnSpeedDetector`
```python
def adjust_return_speed(self, speed: int) -> bool:
    """Adjust return speed parameter"""
```

---

## 🔧 Utility Classes

### `TemplateHelper` (utils/helpers.py)

**Template matching engine với OpenCV**

#### Core Methods
```python
@staticmethod
def match_template(template_path: str, confidence_threshold=0.9) -> Optional[Tuple]:
    """
    Match template với screen capture
    
    Args:
        template_path: Path đến template image
        confidence_threshold: Minimum confidence (0.0-1.0)
        
    Returns:
        Optional[Tuple]: (center_x, center_y, confidence) hoặc None
        
    Algorithm:
        1. Load template image
        2. Screen capture  
        3. cv2.matchTemplate với TM_CCOEFF_NORMED
        4. Find maximum confidence location
        5. Return nếu > threshold
    """

@staticmethod  
def get_match_center(match_location: Tuple, template_size: Tuple) -> Tuple[int, int]:
    """
    Calculate center coordinates từ match location
    
    Args:
        match_location: (top_left_x, top_left_y)
        template_size: (width, height)
        
    Returns:
        Tuple[int, int]: (center_x, center_y)
    """

@staticmethod
def save_debug_screenshot(filename: str) -> str:
    """Save screenshot for debugging với timestamp"""
```

### `MouseHelper` (utils/helpers.py)

**Safe mouse operations với cursor restoration**

#### Core Methods  
```python
@staticmethod
def safe_click(x: int, y: int, delay=0.1) -> None:
    """
    Click với cursor position restoration
    
    Args:
        x, y: Click coordinates
        delay: Delay sau click
        
    Safety Features:
        - Store original cursor position
        - Perform click
        - Restore cursor position
        - Handle exceptions gracefully
    """

@staticmethod
def safe_double_click(x: int, y: int, delay=0.1) -> None:
    """Double-click với safety features"""

@staticmethod
def get_cursor_position() -> Tuple[int, int]:
    """Get current cursor position"""

@staticmethod  
def restore_cursor(original_pos: Tuple[int, int]) -> None:
    """Restore cursor to original position"""
```

### `OCRHelper` (utils/helpers.py)

**OCR operations với Tesseract**

#### Setup & Configuration
```python
@staticmethod
def setup_tesseract() -> None:
    """
    Setup Tesseract executable path
    Auto-detect common installation locations
    """

@staticmethod
def extract_text_data(image) -> Dict:
    """
    Extract text data từ image với bounding boxes
    
    Args:
        image: PIL Image object
        
    Returns:
        Dict: Tesseract data với text, coordinates, confidence
        
    Configuration:
        - PSM 6: Uniform block of text
        - OEM 3: Default OCR Engine Mode
        - Whitelist: A-Za-z0-9 space characters
    """
```

#### Text Processing
```python
@staticmethod
def get_text_words(ocr_data: Dict) -> List[str]:
    """
    Extract clean words từ OCR data
    
    Args:
        ocr_data: Tesseract result dictionary
        
    Returns:
        List[str]: List of cleaned words
        
    Cleaning:
        - Remove empty strings
        - Strip whitespace  
        - Filter confidence > threshold
    """

@staticmethod
def clean_ocr_text(text: str) -> str:
    """
    Clean OCR text output
    
    Args:
        text: Raw OCR text
        
    Returns:
        str: Cleaned text
        
    Operations:
        - Remove special characters
        - Fix common OCR errors
        - Normalize whitespace
    """
```

### `WindowManager` (utils/window_manager.py)

**Windows API integration cho window operations**

#### Window Finding
```python
@staticmethod
def find_window(title_contains: str) -> Optional[Any]:
    """
    Find window by title substring
    
    Args:
        title_contains: Substring to search trong window title
        
    Returns:
        Optional[Window]: Window object hoặc None
        
    Method:
        - Enumerate all windows
        - Match title substring (case-insensitive)
        - Return first match
    """

@staticmethod
def focus_window_by_pid(pid: int) -> Optional[int]:
    """
    Focus window by process ID
    
    Args:
        pid: Process ID
        
    Returns:
        Optional[int]: Window handle hoặc None
    """
```

#### Window Operations
```python
@staticmethod
def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """
    Get window rectangle coordinates
    
    Args:
        hwnd: Window handle
        
    Returns:
        Tuple: (left, top, right, bottom)
    """

@staticmethod
def activate_window(hwnd: int) -> bool:
    """Activate window và bring to foreground"""

@staticmethod
def is_window_visible(hwnd: int) -> bool:
    """Check if window is visible"""
```

### `ProcessFinder` (utils/process_finder.py)

**Process detection và management**

#### Process Detection
```python
class CubaseProcessFinder:
    @staticmethod
    def find() -> Optional[Any]:
        """
        Find Cubase process
        
        Returns:
            Optional[Process]: Process object hoặc None
            
        Search Patterns:
            - "Cubase"
            - "cubase"  
            - Case-insensitive matching
        """

    @staticmethod
    def get_process_info(process) -> Dict:
        """
        Get detailed process information
        
        Args:
            process: Process object
            
        Returns:
            Dict: Process info (pid, name, memory usage, etc.)
        """
```

### `SettingsManager` (utils/settings_manager.py)

**Configuration persistence và management**

#### Settings Operations
```python
class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        """Initialize với settings file path"""
    
    def load_settings(self) -> Dict:
        """
        Load settings từ JSON file
        
        Returns:
            Dict: Settings dictionary với default fallbacks
        """
    
    def save_settings(self, settings: Dict) -> bool:
        """
        Save settings to JSON file
        
        Args:
            settings: Settings dictionary
            
        Returns:
            bool: Save success status
        """
    
    def get_setting(self, key: str, default=None) -> Any:
        """Get specific setting với default fallback"""
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set specific setting value"""
```

### `MessageHelper` (utils/helpers.py)

**User feedback và error messaging**

#### Message Operations
```python
@staticmethod
def show_error(title: str, message: str) -> None:
    """
    Show error dialog to user
    
    Args:
        title: Dialog title
        message: Error message content
    """

@staticmethod  
def show_info(title: str, message: str) -> None:
    """Show info dialog"""

@staticmethod
def show_warning(title: str, message: str) -> None:
    """Show warning dialog"""
```

### `ImageHelper` (utils/helpers.py)

**Image processing và debug utilities**

#### Debug Operations
```python
@staticmethod
def save_debug_image_with_boxes(image, ocr_data: Dict, filename: str) -> str:
    """
    Save debug image với OCR bounding boxes
    
    Args:
        image: PIL Image
        ocr_data: OCR result data  
        filename: Output filename
        
    Returns:
        str: Saved file path
        
    Features:
        - Draw bounding boxes around detected text
        - Color-coded confidence levels
        - Save to result/ directory
    """

@staticmethod
def crop_image_with_margin(image, margin_ratio: float) -> Any:
    """Crop image với margin percentage"""
```

---

## ⚙️ Configuration

### `config.py` - Static Configuration

**Global constants và configuration values**

#### Timing Constants
```python
FOCUS_DELAY = 0.5          # Delay after window focus
ANALYSIS_DELAY = 1.0       # Delay after tone click
CLICK_DELAY = 0.1          # Delay between clicks
SCREENSHOT_DELAY = 0.2     # Delay before screenshot
```

#### Template Matching
```python
TEMPLATE_CONFIDENCE_THRESHOLD = 0.9  # Template match confidence
TEMPLATE_DIR = "templates"           # Template images directory  
RESULT_DIR = "result"               # Debug images directory
```

#### OCR Configuration
```python
OCR_CONFIG = "--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
```

#### Auto-Detection Settings
```python
AUTO_DETECT_INTERVAL = 2.0           # Check interval seconds
AUTO_DETECT_RESPONSIVE_DELAY = 0.1   # Quick response delay  
AUTO_DETECT_TIMEOUT_SHORT = 10       # Short timeout for auto mode
THREAD_JOIN_TIMEOUT = 2.0            # Thread cleanup timeout
```

#### Template Cropping
```python
MARGIN_RATIO = 0.15  # 15% margin for template crops
```

### `settings.json` - Dynamic User Settings

**User-configurable preferences (runtime modifiable)**

#### Structure Example
```json
{
    "auto_detect_enabled": false,
    "current_tone": "--",
    "template_confidence": 0.9,
    "click_positions": {
        "soundshifter": 0.4,
        "auto_tune": 0.5,
        "transpose": 0.6
    },
    "ui_preferences": {
        "window_geometry": "800x600+100+100",
        "theme": "dark"
    }
}
```

---

## 💡 Examples & Usage

### Basic Plugin Control
```python
# Auto-Tune control
detector = AutoTuneDetector()
success = detector.raise_tone()
if success:
    print("Tone raised successfully")

# SoundShifter control  
shifter = SoundShifterDetector()
shifter.set_pitch_value(-2)  # Set to -2 pitch
```

### Template Matching
```python
# Find plugin interface
match_result = TemplateHelper.match_template(
    "templates/auto_tune_template.png",
    confidence_threshold=0.9
)

if match_result:
    center_x, center_y, confidence = match_result
    print(f"Found at ({center_x}, {center_y}) with {confidence:.2f} confidence")
```

### Auto-Detection Setup
```python
# Start auto-detection
tone_detector = ToneDetector()
tone_detector.start_auto_detect(
    tone_callback=gui.update_current_tone,
    current_tone_getter=lambda: gui.current_tone_var.get()
)

# Stop auto-detection  
tone_detector.stop_auto_detect()
```

### Thread-Safe Operations
```python
# Manual operation với auto-pause
def manual_operation():
    gui.pause_auto_detect_for_manual_action()
    try:
        # Perform manual operation
        detector.execute()
    finally:
        gui.resume_auto_detect_after_manual_action()
```

### OCR Processing
```python
# Extract text từ screenshot
screenshot = pyautogui.screenshot()
ocr_data = OCRHelper.extract_text_data(screenshot)
words = OCRHelper.get_text_words(ocr_data)

# Process tone information
tone = tone_detector._extract_current_tone(words)
print(f"Detected tone: {tone}")
```

### Error Handling Patterns
```python
try:
    result = detector.execute()
    if not result:
        MessageHelper.show_error("Operation Failed", "Could not complete operation")
except Exception as e:
    logger.error(f"Detector error: {e}")
    MessageHelper.show_error("Unexpected Error", str(e))
```

---

*🔍 **API Reference hoàn chỉnh** - Tất cả thông tin cần thiết để hiểu và extend Cubase Tools*
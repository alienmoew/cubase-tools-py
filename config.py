import os
import sys

# Tesseract paths
if hasattr(sys, "_MEIPASS"):  # PyInstaller
    BASE_PATH = sys._MEIPASS
    TESSERACT_PATH = os.path.join(BASE_PATH, "tesseract.exe")
    TESSDATA_DIR = os.path.join(BASE_PATH, "tessdata")
else:  # Development
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    TESSDATA_DIR = r"C:\Program Files\Tesseract-OCR\tessdata"

# Directories
RESULT_DIR = "result"
DATA_DIR = "data"
SETTINGS_FILE = "settings.json"
RESULT_DIR = "result"

# OCR Config
OCR_CONFIG = r"--oem 3 --psm 6"

# Timing
FOCUS_DELAY = 0.5
FOCUS_DELAY_FAST = 0.2  # Faster focus for batch operations
ANALYSIS_DELAY = 6.0  # BẮT BUỘC 6-7 giây để AUTO-KEY phân tích tone
AUTO_DETECT_INTERVAL = 2.0
LISTENING_CHECK_INTERVAL = 1.0
LISTENING_TIMEOUT = 30

# Image Processing
CROP_MARGIN_RATIO = 6  # 1/6 margin on each side
THREAD_JOIN_TIMEOUT = 2.0

# Auto-detect settings  
AUTO_DETECT_RESPONSIVE_DELAY = 0.5
AUTO_DETECT_TIMEOUT_SHORT = 10

# Template matching settings
TEMPLATE_MATCH_THRESHOLD = 0.65  # Lowered from 0.7 to handle slight UI variations
VALUE_CLICK_OFFSET_X_RATIO = 0.5  # 50% from left (center horizontally)
VALUE_CLICK_OFFSET_Y_RATIO = 0.6  # 60% from top (slightly below center)

# Multi-scale template matching settings
MULTI_SCALE_ENABLED = True
SCALE_RANGE = (0.6, 1.4)  # Scale from 60% to 140%
SCALE_STEP = 0.1  # Step size for scaling
MAX_SCALE_ATTEMPTS = 8  # Maximum number of scale attempts
SCALE_CONFIDENCE_BOOST = 0.02  # Boost confidence for scaled matches

# GUI Theme settings
GUI_THEMES = ["dark", "light"]
DEFAULT_THEME = "dark"

# Debug settings
DEBUG_MODE = False  # Global debug mode
DEBUG_INITIALIZATION = False  # Debug during app initialization
DEBUG_TEMPLATE_MATCHING = True  # Debug template matching operations
DEBUG_SAVE_IMAGES = True  # Save debug images
SILENT_INITIALIZATION = True  # Silent mode during initialization

# Plugin Names
PLUGIN_NAMES = {
    'autotune': 'AUTO-TUNE PRO',
    'autokey': 'AUTO-KEY',
    'soundshifter': 'SoundShifter Pitch Stereo',
    'proq3': 'Pro-Q 3'
}

# Contact Information
CONTACT_INFO = {
    'phone': '0948999892',
    'studio': 'KT STUDIO'
}

# UI Delays and Timings
UI_DELAYS = {
    'window_focus': 0.3,
    'plugin_activate': 0.3,
    'click_delay': 0.15,
    'click_delay_short': 0.2,
    'batch_reset_delay': 0.05,  # Giảm từ 0.1 xuống 0.05 - nhanh hơn
    'fast_click_delay': 0.05,   # Delay nhanh cho batch operations
    'auto_tune_input_delay': 0.05  # Delay cho auto-tune input operations
}

# Template Paths
TEMPLATE_PATHS = {
    'bypass_off': 'templates/bypass_off_template.png',
    'bypass_on': 'templates/bypass_on_template.png',
    'volume_template': 'templates/volume_template.png',
    'mute_music_template': 'templates/mute_music_template.png',
    'tone_mic_template': 'templates/tone_mic_template.png'
}

# UI Settings
UI_SETTINGS = {
    'window_size': '1200x700',
    'confidence_threshold': 0.7
}

# App Information
APP_NAME = "Cubase Auto Tools"
APP_VERSION = "v1.0"
COPYRIGHT = f"© {CONTACT_INFO['studio']} - {CONTACT_INFO['phone']}"
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

# OCR Config
OCR_CONFIG = r"--oem 3 --psm 6"

# Timing
FOCUS_DELAY = 0.5
ANALYSIS_DELAY = 6.0
AUTO_DETECT_INTERVAL = 2.0
LISTENING_CHECK_INTERVAL = 1.0
LISTENING_TIMEOUT = 30

# Image Processing
CROP_MARGIN_RATIO = 6  # 1/6 margin on each side
THREAD_JOIN_TIMEOUT = 2.0

# Auto-detect settings  
AUTO_DETECT_RESPONSIVE_DELAY = 0.5
AUTO_DETECT_TIMEOUT_SHORT = 10

# GUI Theme settings
GUI_THEMES = ["dark", "light"]
DEFAULT_THEME = "dark"

# App Information
APP_NAME = "Cubase Auto Tools"
APP_VERSION = "v1.0"
COPYRIGHT = "© KT STUDIO - 0948999892"
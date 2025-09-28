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

# OCR Config
OCR_CONFIG = r"--oem 3 --psm 6"

# Timing
FOCUS_DELAY = 0.5
ANALYSIS_DELAY = 6.0
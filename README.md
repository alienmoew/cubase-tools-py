# 🎵 Cubase Tools - Auto Plugin Controller# 📖 CUBASE-TOOLS - PROJECT OVERVIEW



**Công cụ tự động hóa plugin Cubase thông qua Template Matching và GUI Control**> **Tự động hóa Cubase với AI tone detection và thread-safe operations**



[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)## 🎯 **WHAT IT DOES**

[![Windows](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)- **Dò tone tự động** từ plugin AUTO-KEY bằng OCR  

[![Status](https://img.shields.io/badge/status-production-green.svg)](https://github.com/alienmoew/cubase-tools-py)- **Click tự động** Major/Minor và Send buttons

- **Auto-detect mode** theo dõi thay đổi tone trong background

## 📖 Tổng quan- **Thread-safe** với priority system cho manual operations



Cubase Tools là một ứng dụng Python desktop cho phép **điều khiển tự động các plugin Cubase** mà không cần thao tác thủ công. Tool sử dụng **template matching** để nhận diện giao diện plugin và **GUI automation** để thực hiện các thao tác như:## 🏗️ **ARCHITECTURE**

```

- 🎚️ **Điều chỉnh tông nhạc** (Auto-Tune, Transpose, SoundShifter)  main.py → gui.py → features/tone_detector.py → utils/

- 🎛️ **Bật/tắt plugin bypass**```

- ⚡ **Tối ưu workflow** với hotkeys và shortcuts- **GUI:** 3-section layout (Auto-Tune, Nhạc, Giọng hát)

- 🔧 **Cấu hình linh hoạt** cho từng plugin- **Core:** ToneDetector với manual + auto modes  

- **Utils:** OCR, mouse, window, process helpers

### 🎯 Mục đích- **Thread Safety:** Auto-pause system

- **Tăng tốc độ làm việc** trong Cubase khi mix/master nhạc

- **Giảm thiểu lỗi thao tác** thủ công  ## ⚙️ **KEY COMPONENTS**

- **Tự động hóa các tác vụ lặp lại** phổ biến

- **Hỗ trợ multi-plugin** trong một giao diện thống nhất### **ToneDetector (484 lines)**

- `execute()` - Manual tone detection workflow

---- `_auto_detect_loop()` - Background monitoring  

- `_extract_current_tone()` - OCR → "A Major" parsing

## 🏗️ Kiến trúc hệ thống- Thread safety với `_detection_lock` + `_manual_active`



```### **GUI (220 lines)**  

cubase-tools/- CustomTkinter với modern design

├── 📁 features/          # Plugin detector classes- Auto-detect toggle switch

│   ├── auto_tune_detector.py      # Auto-Tune Pro controller- Real-time tone display  

│   ├── soundshifter_detector.py   # SoundShifter Pitch controller  - Auto-pause integration for all features

│   ├── plugin_bypass_detector.py  # Plugin bypass toggle

│   └── ...                       # 6 plugin detectors khác### **Utils (269 lines total)**

├── 📁 utils/            # Core utilities- **OCRHelper:** Tesseract setup + text extraction

│   ├── window_manager.py          # Cubase window handling- **MouseHelper:** Safe click với cursor restoration  

│   ├── helpers.py                 # Template matching engine- **WindowManager:** Focus + find windows

│   └── settings_manager.py        # Configuration management- **ProcessFinder:** Detect Cubase processes

├── 📁 templates/        # Template images cho matching

├── 📁 docs/            # Documentation chi tiết## 🔄 **WORKFLOWS**

├── gui.py              # Main GUI interface (CustomTkinter)

└── main.py             # Entry point### **Manual Detection:**

``````

User clicks "Dò Tone" → Pause auto → Find Cubase → Focus → 

---Screenshot → OCR → Click tone → Wait → Click Send → Resume auto

```

## 🚀 Cài đặt & Sử dụng

### **Auto Detection:**  

### Yêu cầu hệ thống```

- **Windows 10/11** (64-bit)Background loop → Check tone change → Update UI → Auto send → 

- **Python 3.8+** Sleep 2s → Repeat (với priority cho manual)

- **Cubase** (bất kỳ version nào)```

- **Screen resolution** tối thiểu 1920x1080

## 🚀 **USAGE**

### Cài đặt

### **For Users:**

1. **Clone repository:**1. Mở Cubase + plugin AUTO-KEY

```bash2. Run `python main.py` 

git clone https://github.com/alienmoew/cubase-tools-py.git3. Toggle "Auto Detect" hoặc click "Dò Tone"

cd cubase-tools-py

```### **For Developers:**

1. Read `FUNCTION_REFERENCE.md` - Hiểu tất cả functions

2. **Tạo virtual environment:**2. Read `DEBUG_GUIDE.md` - Debug và troubleshooting

```bash3. Read `AUTO_PAUSE_SYSTEM.md` - Thread safety system

python -m venv venv

venv\Scripts\activate## 📂 **FILES TO KNOW**

```

| **File** | **Purpose** | **Key Functions** |

3. **Cài đặt dependencies:**|----------|-------------|-------------------|

```bash| `main.py` | Entry point | `main()` |

pip install -r requirements.txt| `gui.py` | User interface | `_execute_tone_detector()`, `_toggle_auto_detect()` |

```| `tone_detector.py` | Core logic | `execute()`, `_auto_detect_loop()`, `_extract_current_tone()` |

| `helpers.py` | Utilities | `OCRHelper`, `MouseHelper`, `MessageHelper` |

### Chạy ứng dụng| `config.py` | Settings | Paths, delays, OCR config |



```bash## 🔧 **QUICK COMMANDS**

python main.py

```### **Run App:**

```bash

### Sử dụng cơ bảnpython main.py

```

1. **Khởi động Cubase** và mở project có plugin

2. **Chạy Cubase Tools** ### **Debug Mode:**

3. **Chọn plugin** cần điều khiển từ giao diện```python  

4. **Thực hiện thao tác** (tăng/giảm tone, bypass, etc.)# Xem debug image: result/plugin_ocr_debug.png

# Console logs: "📜 OCR text:", "🎹 Click key:", "✅ Clicked 'Send'"

---```



## 🎛️ Tính năng chính### **Add New Feature:**

```python

### 🎵 Plugin Controllersdef _new_feature(self):

    self.pause_auto_detect_for_manual_action()

| Plugin | Tính năng | Status |    try:

|--------|-----------|---------|        # Your feature code

| **Auto-Tune Pro** | Raise/Lower tone ±12 | ✅ Working |    finally:

| **SoundShifter** | Pitch adjustment ±4 tones | ✅ Working |        self.resume_auto_detect_after_manual_action()

| **Transpose** | Key transpose ±12 | ✅ Working |```

| **Plugin Bypass** | ON/OFF toggle | ✅ Working |

| **FlexTune** | Fine tuning control | ✅ Working |## 🏆 **ACHIEVEMENTS** 

| **Natural Vibrato** | Vibrato adjustment | ✅ Working |- ✅ **1,024 lines** of clean, documented code

| **Return Speed** | Speed parameter control | ✅ Working |- ✅ **Thread-safe** với advanced priority system

| **Humanize** | Humanization settings | ✅ Working |- ✅ **Robust OCR** với character cleaning và listening detection  

| **Tone Detector** | General tone detection | ✅ Working |- ✅ **Modern GUI** với CustomTkinter

- ✅ **Extensible** architecture cho unlimited features

### 🔧 Core Features- ✅ **Production-ready** với comprehensive error handling



- **Template Matching**: Confidence-based image recognition (90%+ accuracy)## 📚 **DOCUMENTATION**

- **Auto Window Focus**: Tự động focus Cubase window- **`FUNCTION_REFERENCE.md`** - Complete function list  

- **Error Handling**: Silent failure modes, no crashes- **`DEBUG_GUIDE.md`** - Troubleshooting guide

- **Settings Persistence**: Lưu cấu hình user preferences- **`AUTO_PAUSE_SYSTEM.md`** - Thread safety system

- **Multi-threaded**: Non-blocking GUI operations- **This file** - Quick project overview

- **Debug Mode**: Comprehensive logging và screenshot capture

---

---

*🎯 Đọc file này = hiểu 80% project. Đọc thêm FUNCTION_REFERENCE.md = hiểu 100%!*
## 📚 Documentation chi tiết

| File | Nội dung |
|------|----------|
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | Kiến trúc hệ thống, design patterns, data flow |
| [**API_REFERENCE.md**](docs/API_REFERENCE.md) | Chi tiết tất cả classes, methods, parameters |
| [**FEATURES_GUIDE.md**](docs/FEATURES_GUIDE.md) | Hướng dẫn sử dụng từng plugin detector |
| [**DEBUG_GUIDE.md**](docs/DEBUG_GUIDE.md) | Troubleshooting và debug techniques |

---

## 🛠️ Cấu hình nâng cao

### Template Customization
```python
# settings.json
{
    "template_confidence_threshold": 0.9,
    "click_positions": {
        "soundshifter": 0.4,  # 40% từ trên xuống
        "auto_tune": 0.5,     # 50% từ trên xuống
        "transpose": 0.6      # 60% từ trên xuống
    }
}
```

### Debug Mode
```bash
python main.py --debug  # Bật debug logging
```

---

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Credits

- **Template Matching**: OpenCV-python
- **GUI Framework**: CustomTkinter  
- **Window Automation**: pyautogui, win32gui
- **Image Processing**: Pillow, numpy

---

**⚡ Built with ❤️ for Cubase producers và sound engineers**
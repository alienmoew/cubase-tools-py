# 📖 CUBASE-TOOLS - PROJECT OVERVIEW

> **Tự động hóa Cubase với AI tone detection và thread-safe operations**

## 🎯 **WHAT IT DOES**
- **Dò tone tự động** từ plugin AUTO-KEY bằng OCR  
- **Click tự động** Major/Minor và Send buttons
- **Auto-detect mode** theo dõi thay đổi tone trong background
- **Thread-safe** với priority system cho manual operations

## 🏗️ **ARCHITECTURE**
```
main.py → gui.py → features/tone_detector.py → utils/
```
- **GUI:** 3-section layout (Auto-Tune, Nhạc, Giọng hát)
- **Core:** ToneDetector với manual + auto modes  
- **Utils:** OCR, mouse, window, process helpers
- **Thread Safety:** Auto-pause system

## ⚙️ **KEY COMPONENTS**

### **ToneDetector (484 lines)**
- `execute()` - Manual tone detection workflow
- `_auto_detect_loop()` - Background monitoring  
- `_extract_current_tone()` - OCR → "A Major" parsing
- Thread safety với `_detection_lock` + `_manual_active`

### **GUI (220 lines)**  
- CustomTkinter với modern design
- Auto-detect toggle switch
- Real-time tone display  
- Auto-pause integration for all features

### **Utils (269 lines total)**
- **OCRHelper:** Tesseract setup + text extraction
- **MouseHelper:** Safe click với cursor restoration  
- **WindowManager:** Focus + find windows
- **ProcessFinder:** Detect Cubase processes

## 🔄 **WORKFLOWS**

### **Manual Detection:**
```
User clicks "Dò Tone" → Pause auto → Find Cubase → Focus → 
Screenshot → OCR → Click tone → Wait → Click Send → Resume auto
```

### **Auto Detection:**  
```
Background loop → Check tone change → Update UI → Auto send → 
Sleep 2s → Repeat (với priority cho manual)
```

## 🚀 **USAGE**

### **For Users:**
1. Mở Cubase + plugin AUTO-KEY
2. Run `python main.py` 
3. Toggle "Auto Detect" hoặc click "Dò Tone"

### **For Developers:**
1. Read `FUNCTION_REFERENCE.md` - Hiểu tất cả functions
2. Read `DEBUG_GUIDE.md` - Debug và troubleshooting
3. Read `AUTO_PAUSE_SYSTEM.md` - Thread safety system

## 📂 **FILES TO KNOW**

| **File** | **Purpose** | **Key Functions** |
|----------|-------------|-------------------|
| `main.py` | Entry point | `main()` |
| `gui.py` | User interface | `_execute_tone_detector()`, `_toggle_auto_detect()` |
| `tone_detector.py` | Core logic | `execute()`, `_auto_detect_loop()`, `_extract_current_tone()` |
| `helpers.py` | Utilities | `OCRHelper`, `MouseHelper`, `MessageHelper` |
| `config.py` | Settings | Paths, delays, OCR config |

## 🔧 **QUICK COMMANDS**

### **Run App:**
```bash
python main.py
```

### **Debug Mode:**
```python  
# Xem debug image: result/plugin_ocr_debug.png
# Console logs: "📜 OCR text:", "🎹 Click key:", "✅ Clicked 'Send'"
```

### **Add New Feature:**
```python
def _new_feature(self):
    self.pause_auto_detect_for_manual_action()
    try:
        # Your feature code
    finally:
        self.resume_auto_detect_after_manual_action()
```

## 🏆 **ACHIEVEMENTS** 
- ✅ **1,024 lines** of clean, documented code
- ✅ **Thread-safe** với advanced priority system
- ✅ **Robust OCR** với character cleaning và listening detection  
- ✅ **Modern GUI** với CustomTkinter
- ✅ **Extensible** architecture cho unlimited features
- ✅ **Production-ready** với comprehensive error handling

## 📚 **DOCUMENTATION**
- **`FUNCTION_REFERENCE.md`** - Complete function list  
- **`DEBUG_GUIDE.md`** - Troubleshooting guide
- **`AUTO_PAUSE_SYSTEM.md`** - Thread safety system
- **This file** - Quick project overview

---

*🎯 Đọc file này = hiểu 80% project. Đọc thêm FUNCTION_REFERENCE.md = hiểu 100%!*
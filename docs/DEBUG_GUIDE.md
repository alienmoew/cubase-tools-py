# 🔧 CUBASE-TOOLS QUICK DEBUG GUIDE

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **❌ "Không tìm thấy tiến trình Cubase"**
```python
# Check: CubaseProcessFinder.find() 
# Fix: Đảm bảo Cubase đang chạy với tên process: cubase*.exe
```

### **❌ "Không tìm thấy plugin AUTO-KEY"**  
```python
# Check: WindowManager.find_window("AUTO-KEY")
# Fix: Plugin phải mở và title chứa "AUTO-KEY"
```

### **❌ OCR không đọc được text**
```python
# Debug: Xem file result/plugin_ocr_debug.png  
# Fix: Adjust crop_box ratios trong _process_plugin_window()
```

### **❌ Auto-detect không chạy**
```python  
# Check: self.auto_detect_active = True?
# Check: Thread có bị block bởi _manual_active?
# Debug: Thêm print trong _auto_detect_loop()
```

---

## 🔍 **DEBUG WORKFLOW**

### **Step 1: OCR Debug**
```python
# File được save tự động: result/plugin_ocr_debug.png
# Red boxes = detected text regions
# Console output: "📜 OCR text: ['word1', 'word2']"
```

### **Step 2: Tone Extraction Debug**  
```python
# trong _extract_current_tone():
print(f"AUTO-KEY index: {auto_key_index}")
print(f"Send index: {send_index}")  
print(f"Tone words: {tone_words}")
print(f"Final note: {note}, mode: {mode}")
```

### **Step 3: Thread Debug**
```python
# Manual vs Auto conflict:
print(f"Manual active: {self._manual_active}")
print(f"Lock acquired: {self._detection_lock.acquire(blocking=False)}")
```

---

## ⚡ **QUICK FIXES**

### **Performance Tuning**
```python
# config.py adjustments:
FOCUS_DELAY = 0.3      # Faster window focus
ANALYSIS_DELAY = 4.0   # Shorter wait time  
check_interval = 1.0   # Faster auto-detect
```

### **OCR Accuracy**
```python  
# Adjust crop ratios để focus vào text area:
crop_box = (
    win_w // 8,        # Less crop = more text
    win_h // 8,        
    win_w * 7 // 8,    
    win_h * 7 // 8     
)
```

### **Add New Notes**  
```python
# trong _extract_current_tone():
valid_notes = ["C", "C#", "Db", ..., "YOUR_NEW_NOTE"]
```

---

## 🎯 **EXTENSION POINTS**

### **Add New Feature**
```python
# 1. Create class inherit BaseFeature
# 2. Implement execute() và get_name()  
# 3. Add button trong GUI section
# 4. Use pause/resume pattern:

def _new_feature(self):
    self.pause_auto_detect_for_manual_action()
    try:
        # Your code here
    finally:
        self.resume_auto_detect_after_manual_action()
```

### **Modify GUI Layout**
```python
# gui.py sections:
# - _setup_autotune_section() 
# - _setup_music_section()    ← Add features here
# - _setup_vocal_section()    ← Add features here
```

### **Custom OCR Processing**
```python
# Override trong helpers.py:
def custom_extract_text_data(image, custom_config):
    return pytesseract.image_to_data(
        image, output_type=Output.DICT, config=custom_config
    )
```

---

## 📊 **MONITORING & LOGGING**

### **Key Log Messages**
```
🎯 Manual operation started    → Manual detection bắt đầu
⏸️ Auto-detect bị tạm dừng    → Priority system working  
🔄 Auto detect started       → Auto-detect enabled
🎧 Plugin đang Listening      → Waiting for analysis
✅ Clicked 'Send' button      → Success
❌ Error in tone detector     → Check exception
```

### **Performance Metrics**
```python
# Add timing trong execute():
start_time = time.time()
# ... detection logic ...
elapsed = time.time() - start_time
print(f"Detection took {elapsed:.2f}s")
```

---

## 🚀 **DEVELOPMENT SHORTCUTS**

### **Test OCR Quickly**
```python
# Run in Python console:
from features.tone_detector import ToneDetector  
td = ToneDetector()
result = td._check_current_tone()  # No clicking, just OCR
print(f"Detected: {result}")
```

### **Test GUI Without Cubase**  
```python
# Comment out process checks trong execute()
# Add mock data để test UI updates
```

### **Quick Restart Auto-Detect**
```python
# Trong GUI console:
self.tone_detector.stop_auto_detect()
time.sleep(1)  
self.tone_detector.start_auto_detect()
```

---

*🎯 Save docs này để debug nhanh khi có issue!*
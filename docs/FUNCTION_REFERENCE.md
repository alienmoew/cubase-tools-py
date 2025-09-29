# 📚 CUBASE-TOOLS FUNCTION REFERENCE

## 🎯 **MAIN ENTRY POINT**

### `main.py`
- **`main()`** - Khởi chạy ứng dụng GUI

---

## 🖥️ **GUI LAYER (`gui.py`)**

### **Core Methods**
- **`__init__()`** - Khởi tạo GUI với 3 sections (Auto-Tune, Nhạc, Giọng hát)
- **`run()`** - Chạy main loop của GUI
- **`_on_closing()`** - Cleanup khi đóng app

### **UI Setup**  
- **`_setup_ui()`** - Tạo layout chính với grid 3 cột
- **`_create_section()`** - Tạo từng section với title và content
- **`_setup_autotune_section()`** - Setup section Auto-Tune (toggle, buttons, labels)
- **`_setup_music_section()`** - Setup section Nhạc (placeholder + demo)
- **`_setup_vocal_section()`** - Setup section Giọng hát (placeholder)

### **Feature Integration**
- **`_execute_tone_detector()`** - Chạy manual tone detection với auto-pause
- **`_toggle_auto_detect()`** - Bật/tắt auto-detect mode
- **`update_current_tone()`** - Cập nhật display tone hiện tại

### **Auto-Pause System**
- **`pause_auto_detect_for_manual_action()`** - Tạm dừng auto cho manual action
- **`resume_auto_detect_after_manual_action()`** - Khôi phục auto sau manual
- **`_example_music_feature()`** - Demo feature sử dụng auto-pause

---

## 🎵 **TONE DETECTOR (`features/tone_detector.py`)**

### **Core Detection**
- **`execute()`** - Main function: tìm Cubase → focus → screenshot → OCR → click
- **`_process_plugin_window()`** - Screenshot plugin → OCR → extract tone → click buttons
- **`_extract_current_tone()`** - Parse OCR words thành note + mode (A Major, C# Minor...)

### **Smart Clicking**
- **`_find_and_click_tone()`** - Tìm và click Major/Minor button, đợi khi Listening
- **`_find_and_click_send_button()`** - Tìm và click Send button
- **`_is_listening()`** - Detect plugin có đang analyze không
- **`_wait_for_listening_complete()`** - Đợi plugin hoàn tất analyze trước khi click

### **Auto-Detect System**
- **`start_auto_detect()`** - Bật auto-detect trong background thread
- **`stop_auto_detect()`** - Tắt auto-detect thread
- **`_auto_detect_loop()`** - Loop chính: check tone mới → compare → auto send
- **`_check_current_tone()`** - Chỉ OCR để check tone, không click
- **`_auto_send_tone()`** - Tự động click Send khi detect thay đổi

### **Thread Safety**
- **`pause_auto_detect()`** - Set flag để auto nhường quyền cho manual
- **`resume_auto_detect()`** - Clear flag để auto tiếp tục
- **`_detection_lock`** - Mutex đảm bảo chỉ 1 detection chạy tại 1 thời điểm

---

## 🔧 **UTILITY HELPERS (`utils/helpers.py`)**

### **OCRHelper**
- **`setup_tesseract()`** - Config đường dẫn Tesseract từ config.py
- **`extract_text_data()`** - OCR image → dict với text, coordinates, dimensions
- **`get_text_words()`** - Extract clean words từ OCR data

### **ImageHelper**  
- **`save_debug_image_with_boxes()`** - Save ảnh với red boxes quanh detected text

### **MessageHelper**
- **`show_error()`** - Popup lỗi với icon đỏ
- **`show_warning()`** - Popup cảnh báo với icon vàng  
- **`show_info()`** - Popup thông tin với icon xanh
- **`show_success()`** - Popup thành công

### **MouseHelper**
- **`safe_click()`** - Click và trả chuột về vị trí cũ (instant/fast/smooth)
- **`safe_double_click()`** - Double click an toàn
- **`safe_right_click()`** - Right click an toàn

---

## 🎯 **PROCESS & WINDOW (`utils/`)**

### **CubaseProcessFinder (`process_finder.py`)**
- **`find()`** - Tìm Cubase process theo tên (cubase, cubase14, cubasepro...)

### **WindowManager (`window_manager.py`)**  
- **`focus_window_by_pid()`** - Focus window theo process ID
- **`find_window()`** - Tìm window theo title keyword ("AUTO-KEY")
- **`screenshot_window()`** - Chụp màn hình window cụ thể

---

## 🏗️ **BASE ARCHITECTURE (`features/base_feature.py`)**

### **BaseFeature (Abstract)**
- **`__init__()`** - Tạo folders (result/, data/)
- **`execute()`** - Abstract method các features phải implement
- **`get_name()`** - Abstract method trả về tên feature

---

## ⚙️ **CONFIGURATION (`config.py`)**

### **Paths**
- **`TESSERACT_PATH`** - Đường dẫn Tesseract executable
- **`TESSDATA_DIR`** - Thư mục tessdata
- **`RESULT_DIR`** - Thư mục save debug images
- **`DATA_DIR`** - Thư mục data

### **Settings**  
- **`OCR_CONFIG`** - Tesseract parameters "--oem 3 --psm 6"
- **`FOCUS_DELAY`** - Delay sau khi focus window (0.5s)
- **`ANALYSIS_DELAY`** - Delay chờ plugin analyze (6.0s)

---

## 🔄 **AUTO-PAUSE DECORATOR (`utils/auto_pause_decorator.py`)**

### **pause_auto_on_manual(gui_instance)**
- **Decorator** tự động pause/resume auto-detect cho manual functions
- **Input:** GUI instance có methods pause/resume
- **Output:** Wrapped function với auto-pause logic

---

## 🚀 **QUICK REFERENCE WORKFLOW**

### **Manual Tone Detection:**
```
GUI._execute_tone_detector() 
→ pause_auto_detect() 
→ ToneDetector.execute() 
→ find Cubase → focus → screenshot → OCR → click tone → click send
→ resume_auto_detect()
```

### **Auto-Detect Loop:**
```  
ToneDetector._auto_detect_loop()
→ check manual_active flag → acquire lock 
→ _check_current_tone() → compare with current 
→ if changed: update UI + _auto_send_tone()
→ release lock → sleep 2s → repeat
```

### **Thread Safety:**
```
Manual action: set _manual_active = True
Auto loop: if _manual_active → skip cycle  
Manual done: set _manual_active = False
Auto loop: continue normal operation
```

---

*📝 Docs này cover 100% functions trong project. Đọc này là hiểu được toàn bộ codebase!*
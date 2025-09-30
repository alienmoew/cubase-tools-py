# 🔧 DEBUG GUIDE - Troubleshooting & Development Guide# 🔧 CUBASE-TOOLS QUICK DEBUG GUIDE



> **Comprehensive debugging guide cho Cubase Tools development và troubleshooting**## 🚨 **COMMON ISSUES & SOLUTIONS**



---### **❌ "Không tìm thấy tiến trình Cubase"**

```python

## 📋 Mục lục# Check: CubaseProcessFinder.find() 

# Fix: Đảm bảo Cubase đang chạy với tên process: cubase*.exe

1. [**Common Issues & Quick Fixes**](#-common-issues--quick-fixes)```

2. [**Debug Workflow**](#-debug-workflow)  

3. [**Template Matching Debug**](#-template-matching-debug)### **❌ "Không tìm thấy plugin AUTO-KEY"**  

4. [**OCR Debug Techniques**](#-ocr-debug-techniques)```python

5. [**Threading Debug**](#-threading-debug)# Check: WindowManager.find_window("AUTO-KEY")

6. [**Performance Optimization**](#-performance-optimization)# Fix: Plugin phải mở và title chứa "AUTO-KEY"

7. [**Development Tools**](#-development-tools)```



---### **❌ OCR không đọc được text**

```python

## 🚨 Common Issues & Quick Fixes# Debug: Xem file result/plugin_ocr_debug.png  

# Fix: Adjust crop_box ratios trong _process_plugin_window()

### Plugin Detection Issues```



#### ❌ "Không tìm thấy tiến trình Cubase"### **❌ Auto-detect không chạy**

```python```python  

# Cause: Cubase process not found# Check: self.auto_detect_active = True?

# Debug: # Check: Thread có bị block bởi _manual_active?

proc = CubaseProcessFinder.find()# Debug: Thêm print trong _auto_detect_loop()

print(f"Found processes: {proc}")```



# Solutions:---

1. Ensure Cubase is running

2. Check process name patterns: "cubase*.exe"## 🔍 **DEBUG WORKFLOW**

3. Run as administrator if needed

4. Verify Cubase version compatibility### **Step 1: OCR Debug**

``````python

# File được save tự động: result/plugin_ocr_debug.png

#### ❌ "Không tìm thấy plugin AUTO-KEY"# Red boxes = detected text regions

```python# Console output: "📜 OCR text: ['word1', 'word2']"

# Cause: Plugin window not found```

# Debug:

plugin_win = WindowManager.find_window("AUTO-KEY")### **Step 2: Tone Extraction Debug**  

print(f"Plugin window: {plugin_win}")```python

# trong _extract_current_tone():

# Solutions:print(f"AUTO-KEY index: {auto_key_index}")

1. Open AUTO-KEY plugin in Cubaseprint(f"Send index: {send_index}")  

2. Ensure plugin window is visible on screenprint(f"Tone words: {tone_words}")

3. Check window title contains "AUTO-KEY"print(f"Final note: {note}, mode: {mode}")

4. Verify plugin is not minimized```

```

### **Step 3: Thread Debug**

#### ❌ Template matching fails (confidence < 0.9)```python

```python# Manual vs Auto conflict:

# Cause: Template image doesn't match current plugin appearanceprint(f"Manual active: {self._manual_active}")

# Debug:print(f"Lock acquired: {self._detection_lock.acquire(blocking=False)}")

match_result = TemplateHelper.match_template("template.png")```

if match_result:

    x, y, confidence = match_result---

    print(f"Match confidence: {confidence:.3f}")

## ⚡ **QUICK FIXES**

# Solutions:

1. Update template image### **Performance Tuning**

2. Check screen DPI scaling (100% vs 150%)```python

3. Verify plugin theme/appearance# config.py adjustments:

4. Test with different window sizesFOCUS_DELAY = 0.3      # Faster window focus

```ANALYSIS_DELAY = 4.0   # Shorter wait time  

check_interval = 1.0   # Faster auto-detect

### OCR Issues```



#### ❌ OCR không đọc được text### **OCR Accuracy**

```python```python  

# Cause: Text extraction failed# Adjust crop ratios để focus vào text area:

# Debug: Check result/plugin_ocr_debug.pngcrop_box = (

# Solutions:    win_w // 8,        # Less crop = more text

1. Improve text contrast    win_h // 8,        

2. Adjust crop_box ratios    win_w * 7 // 8,    

3. Update OCR configuration    win_h * 7 // 8     

4. Check Tesseract installation)

``````



#### ❌ Tone parsing incorrect### **Add New Notes**  

```python```python

# Cause: Text parsing logic issues# trong _extract_current_tone():

# Debug trong _extract_current_tone():valid_notes = ["C", "C#", "Db", ..., "YOUR_NEW_NOTE"]

print(f"AUTO-KEY index: {auto_key_index}")```

print(f"Send index: {send_index}")  

print(f"Tone words: {tone_words}")---

print(f"Final result: {note} {mode}")

## 🎯 **EXTENSION POINTS**

# Solutions:

1. Update note validation patterns### **Add New Feature**

2. Check marker detection ("AUTO-KEY", "Send")```python

3. Review text cleaning logic# 1. Create class inherit BaseFeature

4. Add more note variations# 2. Implement execute() và get_name()  

```# 3. Add button trong GUI section

# 4. Use pause/resume pattern:

### Threading Issues

def _new_feature(self):

#### ❌ Auto-detect không hoạt động    self.pause_auto_detect_for_manual_action()

```python    try:

# Cause: Thread synchronization problems        # Your code here

# Debug:    finally:

print(f"Auto detect active: {self.auto_detect_active}")        self.resume_auto_detect_after_manual_action()

print(f"Manual active: {self._manual_active}")```

print(f"Lock acquired: {self._detection_lock.acquire(blocking=False)}")

### **Modify GUI Layout**

# Solutions:```python

1. Check thread lifecycle# gui.py sections:

2. Verify flag management# - _setup_autotune_section() 

3. Review lock acquisition logic# - _setup_music_section()    ← Add features here

4. Add thread status logging# - _setup_vocal_section()    ← Add features here

``````



#### ❌ GUI freezing### **Custom OCR Processing**

```python```python

# Cause: UI thread blocking# Override trong helpers.py:

# Solutions:def custom_extract_text_data(image, custom_config):

1. Use threading for long operations    return pytesseract.image_to_data(

2. Add progress feedback        image, output_type=Output.DICT, config=custom_config

3. Implement timeout mechanisms    )

4. Use non-blocking operations```

```

---

---

## 📊 **MONITORING & LOGGING**

## 🔍 Debug Workflow

### **Key Log Messages**

### Step 1: Environment Verification```

```python🎯 Manual operation started    → Manual detection bắt đầu

# Check system requirements⏸️ Auto-detect bị tạm dừng    → Priority system working  

def verify_environment():🔄 Auto detect started       → Auto-detect enabled

    # Check Python version🎧 Plugin đang Listening      → Waiting for analysis

    import sys✅ Clicked 'Send' button      → Success

    print(f"Python version: {sys.version}")❌ Error in tone detector     → Check exception

    ```

    # Check dependencies

    try:### **Performance Metrics**

        import cv2, customtkinter, pytesseract```python

        print("✅ All dependencies available")# Add timing trong execute():

    except ImportError as e:start_time = time.time()

        print(f"❌ Missing dependency: {e}")# ... detection logic ...

    elapsed = time.time() - start_time

    # Check Tesseract installationprint(f"Detection took {elapsed:.2f}s")

    try:```

        OCRHelper.setup_tesseract()

        print("✅ Tesseract configured")---

    except Exception as e:

        print(f"❌ Tesseract issue: {e}")## 🚀 **DEVELOPMENT SHORTCUTS**

```

### **Test OCR Quickly**

### Step 2: Plugin Detection Chain```python

```python# Run in Python console:

def debug_plugin_detection():from features.tone_detector import ToneDetector  

    # 1. Process detectiontd = ToneDetector()

    proc = CubaseProcessFinder.find()result = td._check_current_tone()  # No clicking, just OCR

    print(f"Cubase process: {proc}")print(f"Detected: {result}")

    ```

    # 2. Window focus

    if proc:### **Test GUI Without Cubase**  

        hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])```python

        print(f"Focus result: {hwnd}")# Comment out process checks trong execute()

    # Add mock data để test UI updates

    # 3. Plugin window detection  ```

    plugin_win = WindowManager.find_window("AUTO-KEY")

    print(f"Plugin window: {plugin_win}")### **Quick Restart Auto-Detect**

    ```python

    # 4. Template matching (if applicable)# Trong GUI console:

    match_result = TemplateHelper.match_template("template.png")self.tone_detector.stop_auto_detect()

    print(f"Template match: {match_result}")time.sleep(1)  

```self.tone_detector.start_auto_detect()

```

### Step 3: Data Flow Verification

```python---

def debug_data_flow():

    # Screenshot → OCR → Parsing chain*🎯 Save docs này để debug nhanh khi có issue!*
    detector = ToneDetector()
    
    # Manual OCR test (no clicking)
    current_tone = detector._check_current_tone()
    print(f"Current tone detected: {current_tone}")
    
    # Check debug images
    debug_files = os.listdir("result/")
    print(f"Debug files available: {debug_files}")
```

---

## 🎯 Template Matching Debug

### Quick Template Test
```python
def quick_template_test():
    """Test all templates quickly"""
    templates = {
        'auto_tune': 'templates/auto_tune_template.png',
        'soundshifter': 'templates/soundshifter_pitch_template.png',
        'bypass_on': 'templates/bypass_on_template.png',
        'bypass_off': 'templates/bypass_off_template.png'
    }
    
    for name, path in templates.items():
        if os.path.exists(path):
            result = TemplateHelper.match_template(path)
            if result:
                x, y, confidence = result
                print(f"✅ {name}: Found at ({x}, {y}) confidence {confidence:.3f}")
            else:
                print(f"❌ {name}: Not found")
        else:
            print(f"⚠️ {name}: Template file missing")
```

### Template Quality Check
```python
def assess_template_quality(template_path):
    """Quick template quality assessment"""
    if not os.path.exists(template_path):
        return {"error": "Template not found"}
    
    template = cv2.imread(template_path)
    gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Basic metrics
    metrics = {
        'size': template.shape[:2],
        'contrast': np.std(gray),
        'edge_density': cv2.Canny(gray, 50, 150).sum() / gray.size
    }
    
    # Simple scoring
    score = 0
    if 50 <= metrics['size'][0] <= 200: score += 25
    if metrics['contrast'] > 30: score += 25  
    if metrics['edge_density'] > 0.1: score += 25
    
    metrics['quality_score'] = score
    return metrics
```

---

## 📝 OCR Debug Techniques

### Quick OCR Test
```python
def test_ocr_quickly():
    """Test OCR without full detection workflow"""
    from features.tone_detector import ToneDetector
    
    detector = ToneDetector()
    
    # Direct OCR test
    result = detector._check_current_tone()
    print(f"OCR Result: {result}")
    
    # Check debug files
    if os.path.exists("result/plugin_ocr_debug.png"):
        print("✅ OCR debug image available")
    else:
        print("❌ No OCR debug image found")
```

### OCR Configuration Test
```python
def test_ocr_configs():
    """Test different OCR configurations"""
    # Sample image for testing
    test_image = Image.new('RGB', (200, 50), 'white')
    
    configs = {
        'default': "--psm 6",
        'single_line': "--psm 7",
        'word_mode': "--psm 8"
    }
    
    for name, config in configs.items():
        try:
            result = pytesseract.image_to_string(test_image, config=config)
            print(f"✅ {name}: Working")
        except Exception as e:
            print(f"❌ {name}: {e}")
```

---

## 🧵 Threading Debug

### Thread Status Check
```python
def check_thread_status(detector):
    """Quick thread status check"""
    print(f"Auto detect active: {detector.auto_detect_active}")
    print(f"Auto detect thread: {detector.auto_detect_thread}")
    
    if detector.auto_detect_thread:
        print(f"Thread alive: {detector.auto_detect_thread.is_alive()}")
    
    print(f"Manual active flag: {detector._manual_active}")
    
    # Test lock availability
    lock_available = detector._detection_lock.acquire(blocking=False)
    if lock_available:
        detector._detection_lock.release()
        print("✅ Detection lock available")
    else:
        print("❌ Detection lock is held")
```

### Auto-Detection Restart
```python
def restart_auto_detection(gui):
    """Quick restart auto-detection"""
    print("Stopping auto-detect...")
    gui.tone_detector.stop_auto_detect()
    
    time.sleep(1)
    
    print("Starting auto-detect...")
    gui.tone_detector.start_auto_detect(
        tone_callback=gui.update_current_tone,
        current_tone_getter=lambda: gui.current_tone_var.get()
    )
    
    print("✅ Auto-detect restarted")
```

---

## ⚡ Performance Optimization

### Quick Performance Check
```python
def performance_check():
    """Check basic performance metrics"""
    import psutil
    
    # Memory usage
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    print(f"Memory usage: {memory_mb:.1f} MB")
    print(f"CPU percent: {process.cpu_percent():.1f}%")
    
    # Template cache size
    cache_size = len(TemplateHelper._template_cache) if hasattr(TemplateHelper, '_template_cache') else 0
    print(f"Template cache size: {cache_size}")
```

### Timing Decorator
```python
def time_function(func):
    """Simple timing decorator"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.3f} seconds")
        return result
    return wrapper

# Usage: @time_function
```

---

## 🛠️ Development Tools

### Configuration Validator
```python
def validate_setup():
    """Quick setup validation"""
    issues = []
    
    # Check config.py
    try:
        import config
        print("✅ config.py imported")
    except ImportError:
        issues.append("config.py missing")
    
    # Check templates
    template_dir = "templates"
    if os.path.exists(template_dir):
        templates = os.listdir(template_dir)
        print(f"✅ Templates found: {len(templates)}")
    else:
        issues.append("Templates directory missing")
    
    # Check result directory
    if not os.path.exists("result"):
        os.makedirs("result")
        print("✅ Created result directory")
    
    # Check Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract working")
    except Exception:
        issues.append("Tesseract not working")
    
    if issues:
        print("❌ Issues found:", issues)
        return False
    else:
        print("✅ All checks passed")
        return True
```

### Quick Test Runner
```python
def run_quick_tests():
    """Run essential quick tests"""
    print("🧪 Running Quick Tests...")
    print("=" * 30)
    
    # Test 1: Setup validation
    print("1. Setup Validation:")
    validate_setup()
    
    # Test 2: Template test
    print("\n2. Template Test:")
    quick_template_test()
    
    # Test 3: OCR test
    print("\n3. OCR Test:")
    test_ocr_quickly()
    
    # Test 4: Performance check
    print("\n4. Performance Check:")
    performance_check()
    
    print("\n✅ Quick tests completed!")
```

### GUI Mock Test
```python
def test_gui_without_cubase():
    """Test GUI without Cubase dependency"""
    class MockDetector:
        def execute(self): 
            print("Mock execution")
            return True
        def get_name(self): 
            return "Mock Detector"
        def start_auto_detect(self, **kwargs):
            print("Mock auto-detect started")
        def stop_auto_detect(self):
            print("Mock auto-detect stopped")
    
    # Test GUI creation
    try:
        from gui import CubaseAutoToolGUI
        gui = CubaseAutoToolGUI()
        
        # Replace with mock
        gui.tone_detector = MockDetector()
        
        # Test basic functionality
        gui.update_current_tone("Test Tone")
        print("✅ GUI test passed")
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
```

---

## 🎯 Quick Debug Commands

### Essential Debug Commands
```python
# Quick OCR check
td = ToneDetector()
tone = td._check_current_tone()
print(f"Current tone: {tone}")

# Quick template check  
result = TemplateHelper.match_template("templates/auto_tune_template.png")
print(f"Template match: {result}")

# Quick thread check
print(f"Auto active: {td.auto_detect_active}")
print(f"Manual active: {td._manual_active}")

# Quick restart auto-detect
td.stop_auto_detect()
time.sleep(1)
td.start_auto_detect()
```

### Debug File Locations
```
result/plugin_ocr_debug.png     # OCR bounding boxes
result/template_debug_*.png     # Template match visualization  
result/ocr_processed.png        # Processed OCR image
settings.json                   # User settings
```

### Common Debug Scenarios

**Scenario 1: OCR not working**
1. Check `result/plugin_ocr_debug.png`
2. Verify plugin window visibility
3. Test OCR configuration
4. Adjust crop ratios

**Scenario 2: Template matching fails**
1. Update template image
2. Check confidence thresholds
3. Verify plugin appearance
4. Test screen scaling

**Scenario 3: Auto-detect stops**
1. Check thread status
2. Restart auto-detect
3. Verify flag states
4. Review lock usage

**Scenario 4: GUI freezes**
1. Check for blocking operations
2. Add threading for long tasks
3. Implement timeouts
4. Use progress feedback

---

*🔧 **Quick Debug Guide** - Essential troubleshooting commands và techniques!*
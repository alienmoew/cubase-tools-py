# 🎛️ FEATURES GUIDE - Plugin Detectors Deep Dive

> **Hướng dẫn chi tiết từng plugin detector: cách hoạt động, template matching, troubleshooting**

---

## 📋 Mục lục

1. [**Template Matching System**](#-template-matching-system)
2. [**Auto-Tune Pro Detector**](#-auto-tune-pro-detector)  
3. [**SoundShifter Detector**](#-soundshifter-detector)
4. [**Plugin Bypass Detector**](#-plugin-bypass-detector)
5. [**Tone Detector (AUTO-KEY)**](#-tone-detector-auto-key)
6. [**Other Plugin Detectors**](#-other-plugin-detectors)
7. [**Troubleshooting Guide**](#-troubleshooting-guide)

---

## 🔍 Template Matching System

### Cách hoạt động

**Template Matching** là core technology của Cubase Tools, sử dụng **OpenCV** để nhận diện giao diện plugin.

#### Algorithm Flow
```
1. Load Template Image (PNG)
   ↓
2. Capture Current Screen
   ↓  
3. cv2.matchTemplate() với TM_CCOEFF_NORMED
   ↓
4. Find Max Confidence Location
   ↓
5. Check Threshold (>= 0.9)
   ↓
6. Return Coordinates hoặc None
```

#### Template Requirements
- **Format:** PNG với transparent background
- **Size:** Tối ưu 50x50 đến 200x200 pixels  
- **Content:** Unique visual elements của plugin
- **Quality:** High contrast, sharp edges
- **Background:** Avoid generic UI elements

#### Confidence Levels
```python
CONFIDENCE_THRESHOLD = 0.9  # 90% match required

# Typical results:
Perfect Match: 0.95-1.00    # ✅ Reliable
Good Match:    0.90-0.95    # ✅ Acceptable  
Poor Match:    0.80-0.90    # ⚠️ Unstable
No Match:      < 0.80       # ❌ Failed
```

---

## 🎚️ Auto-Tune Pro Detector

### Overview
**Plugin:** Antares Auto-Tune Pro  
**Function:** Pitch correction control (±12 semitones)  
**Template:** Standard Auto-Tune interface elements

### Features

#### Tone Control
```python
detector.raise_tone()    # +1 semitone
detector.lower_tone()    # -1 semitone  
detector.reset_pitch()   # Reset to 0
```

#### Template Matching
- **Template File:** `auto_tune_template.png`
- **Target Element:** Pitch correction slider/knob
- **Click Position:** 50% from top (centered)
- **Confidence:** 0.9+ required

#### Usage Example
```python
from features.auto_tune_detector import AutoTuneDetector

detector = AutoTuneDetector()

# Raise pitch by 1 semitone
success = detector.raise_tone()
if success:
    print("✅ Pitch raised successfully")
else:
    print("❌ Failed to find Auto-Tune interface")

# Reset to neutral
detector.reset_pitch()
```

#### Troubleshooting

**❌ Template not found:**
- Ensure Auto-Tune Pro is visible on screen
- Check plugin window is not minimized
- Verify correct Auto-Tune version (Pro vs Artist)

**❌ Click position wrong:**
- Update template with current plugin appearance
- Adjust click position in code if needed
- Check screen scaling (150% vs 100%)

**❌ Low confidence:**
- Plugin theme might be different
- Try updating template image
- Check lighting/contrast settings

---

## 🔄 SoundShifter Detector  

### Overview
**Plugin:** Eventide SoundShifter Pitch Stereo  
**Function:** Pitch shifting (±4 tones range)  
**Template:** SoundShifter-specific interface

### Special Features

#### Tone Calculation Logic
```python
# SoundShifter uses ±2 per tone
PITCH_PER_TONE = 2

def raise_tone(self):
    """Raise by 2 pitch units (1 tone)"""
    return self.set_pitch_value(self.current_pitch + 2)

def lower_tone(self):  
    """Lower by 2 pitch units (1 tone)"""
    return self.set_pitch_value(self.current_pitch - 2)
```

#### Double-Click Input Method
```python
def set_pitch_value(self, target_value):
    """
    Set exact pitch value using double-click input
    
    Steps:
    1. Find pitch input field
    2. Double-click to select all
    3. Type new value  
    4. Press Enter to confirm
    """
```

#### Click Position Override
```python
def _find_template_match(self):
    """Override parent với 40% click position"""
    # SoundShifter cần click cao hơn normal position
    click_y = match_top + int(match_height * 0.4)  # 40% from top
```

#### Template Matching
- **Template File:** `soundshifter_pitch_template.png`
- **Target Element:** Pitch input field  
- **Click Position:** 40% from top (optimized)
- **Confidence:** 0.94+ typical

#### Usage Example
```python
from features.soundshifter_detector import SoundShifterDetector

detector = SoundShifterDetector()

# Raise by 1 tone (+2 pitch)
detector.raise_tone()

# Set exact value
detector.set_pitch_value(-4)  # Minimum value

# Get description
desc = detector.get_tone_description(-2)  # "Giảm 1 tone"
```

#### Troubleshooting

**❌ Double-click fails:**
- Input field might be disabled
- Check plugin focus state
- Try single click first

**❌ Value not accepted:**
- Check range limits (-4 to +4)
- Ensure numeric input only
- Verify Enter key press

**❌ 40% position wrong:**
- Template might need updating
- Check window size variations
- Test with different plugin sizes

---

## 🔀 Plugin Bypass Detector

### Overview  
**Plugin:** Universal (any plugin với bypass)  
**Function:** Toggle bypass ON/OFF state  
**Templates:** Dual template system

### Dual Template System

#### Template Files
```python
BYPASS_ON_TEMPLATE = "bypass_on_template.png"    # Bypass enabled
BYPASS_OFF_TEMPLATE = "bypass_off_template.png"  # Bypass disabled  
```

#### State Detection
```python
def get_current_state(self, silent=True):
    """
    Detect current bypass state
    
    Returns:
        "ON"  - Bypass is enabled  
        "OFF" - Bypass is disabled
        None  - Cannot determine state
    """
```

#### Toggle Logic
```python
def toggle_bypass(self):
    """
    Smart toggle based on current state
    
    Logic:
    1. Detect current state
    2. Click appropriate button  
    3. Verify state changed
    4. Return success/failure
    """
```

#### Infinite Loop Fix
```python
def _revert_toggle_state(self):
    """
    Fix infinite loop in GUI callbacks
    
    Problem: Toggle callbacks triggering each other
    Solution: Temporarily disable callbacks
    """
```

#### Usage Example
```python
from features.plugin_bypass_detector import PluginBypassDetector

detector = PluginBypassDetector()

# Get current state
state = detector.get_current_state()
print(f"Current bypass state: {state}")

# Toggle bypass
success = detector.toggle_bypass()
if success:
    print("✅ Bypass toggled successfully")

# Revert GUI state if needed
detector._revert_toggle_state()
```

#### Troubleshooting

**❌ State detection fails:**
- Update both ON and OFF templates
- Check bypass button visibility
- Verify plugin supports bypass

**❌ Infinite loop in GUI:**
- Use `_revert_toggle_state()` method
- Disable callbacks during operations
- Check GUI toggle switch logic

**❌ Toggle doesn't work:**
- Button might be disabled
- Check plugin state
- Verify click coordinates

---

## 🎹 Tone Detector (AUTO-KEY)

### Overview
**Plugin:** Mixed In Key AUTO-KEY  
**Function:** Automatic tone detection và sending  
**Method:** OCR-based text recognition

### Core Functionality

#### Manual Detection Workflow
```
1. Find Cubase process
   ↓
2. Focus Cubase window  
   ↓
3. Find AUTO-KEY plugin window
   ↓
4. Screenshot và crop plugin area
   ↓  
5. OCR text extraction
   ↓
6. Parse tone information
   ↓
7. Click detected tone button
   ↓
8. Wait for analysis completion
   ↓
9. Click Send button
```

#### Auto-Detection System
```python
# Background thread monitoring
def _auto_detect_loop(self):
    """
    Continuous monitoring:
    1. Check for manual operations
    2. OCR current tone
    3. Compare with app current tone  
    4. Auto-send if different
    5. Sleep and repeat
    """
```

#### OCR Processing
```python
def _extract_current_tone(self, words_list):
    """
    Parse tone từ OCR text
    
    Input: ["AUTO-KEY", "A", "Major", "Send", "to", "Auto-Tune"]
    Output: "A Major"
    
    Logic:
    1. Find "AUTO-KEY" và "Send" markers
    2. Extract text between markers  
    3. Identify note (A-G) và mode (Major/Minor)
    4. Combine và return
    """
```

#### Listening State Detection
```python
def _is_listening(self, ocr_data):
    """
    Detect if plugin is analyzing audio
    
    Keywords: "listening", "analyzing", "processing", "detecting"
    
    Action: Wait for completion before clicking
    """
```

#### Thread Safety
```python
# Mutual exclusion system
_detection_lock = threading.Lock()
_manual_active = False  # Manual operation flag

# Priority system: Manual operations pause auto-detection
```

#### Usage Example
```python
from features.tone_detector import ToneDetector

detector = ToneDetector()

# Manual detection
success = detector.execute(tone_callback=update_gui)

# Auto-detection
detector.start_auto_detect(
    tone_callback=update_gui,
    current_tone_getter=lambda: current_tone_var.get()
)

# Stop auto-detection
detector.stop_auto_detect()
```

#### Troubleshooting

**❌ OCR fails:**
- Check AUTO-KEY window visibility
- Verify text contrast
- Update Tesseract configuration

**❌ Tone parsing wrong:**
- Check OCR word boundaries
- Verify "AUTO-KEY" và "Send" markers
- Update parsing logic if needed

**❌ Auto-detection conflicts:**
- Check thread safety locks
- Verify manual operation flags
- Review priority system

**❌ Listening detection fails:**
- Update listening keywords
- Check OCR accuracy
- Adjust timeout values

---

## 🎛️ Other Plugin Detectors

### TransposeDetector
**Plugin:** Cubase built-in Transpose  
**Function:** Key transposition (±12 semitones)

```python
# Template: transpose_template.png
# Click Position: 60% from top
# Range: -12 to +12 semitones

detector.transpose_up()    # +1 semitone
detector.transpose_down()  # -1 semitone
```

### FlexTuneDetector  
**Plugin:** FlexTune pitch correction  
**Function:** Fine pitch adjustment

```python
# Template: flex_tune_template.png
# Method: Parameter adjustment
# Range: Fine-grained pitch control

detector.adjust_flex_tune("up")
detector.adjust_flex_tune("down")
```

### NaturalVibratoDetector
**Plugin:** Natural Vibrato effect  
**Function:** Vibrato amount control

```python
# Template: natural_vibrato_template.png  
# Method: Vibrato parameter adjustment
# Range: 0.0 to 1.0

detector.adjust_vibrato(0.5)  # 50% vibrato
```

### HumanizeDetector
**Plugin:** Humanization effects  
**Function:** Toggle humanization ON/OFF

```python
# Template: humanize_template.png
# Method: Toggle button click
# States: ON/OFF

detector.toggle_humanize()
```

### ReturnSpeedDetector
**Plugin:** Return Speed parameter  
**Function:** Speed adjustment control

```python
# Template: return_speed_template.png
# Method: Speed parameter control
# Range: Variable speed values

detector.adjust_return_speed(75)  # 75% speed
```

---

## 🔧 Troubleshooting Guide

### Common Issues

#### Template Matching Failures

**❌ Low Confidence (< 0.9)**
```
Causes:
- Plugin appearance changed
- Screen scaling issues  
- Theme/color differences
- Window size variations

Solutions:
- Update template images
- Check screen DPI settings
- Test with default plugin themes
- Capture templates at standard size
```

**❌ Template Not Found**
```
Causes:
- Plugin window not visible
- Plugin minimized/hidden
- Wrong plugin version
- UI elements overlapped

Solutions:  
- Ensure plugin visibility
- Check window focus state
- Verify correct plugin version
- Clear overlapping windows
```

**❌ Wrong Click Position**
```
Causes:
- Template position changed
- Click offset incorrect
- Plugin size variations
- DPI scaling issues

Solutions:
- Adjust click position percentages
- Test with multiple plugin sizes  
- Check coordinate calculations
- Update position overrides
```

#### OCR Issues

**❌ Text Recognition Failed**
```
Causes:
- Low text contrast
- Font rendering issues
- Image quality poor
- OCR configuration wrong

Solutions:
- Improve image quality
- Update OCR whitelist
- Adjust confidence thresholds
- Check Tesseract installation
```

**❌ Parsing Errors**
```
Causes:
- Text boundary detection wrong  
- Marker keywords missing
- Text format changed
- Character substitution

Solutions:
- Update parsing logic
- Check marker detection
- Review character cleaning
- Test with different text samples
```

#### Threading Problems

**❌ Deadlocks**
```  
Causes:
- Lock acquisition conflicts
- Thread synchronization issues
- Nested lock scenarios
- Priority inversion

Solutions:
- Review lock acquisition order
- Use timeout-based locks
- Implement proper cleanup
- Check thread lifecycle
```

**❌ Race Conditions**
```
Causes:
- Shared state mutations
- Unsynchronized access
- Event timing issues
- Flag management problems

Solutions:
- Add proper synchronization
- Use atomic operations
- Implement event queues
- Review state management
```

### Debug Techniques

#### Template Debugging
```python
# Save debug screenshots
TemplateHelper.save_debug_screenshot("debug_capture.png")

# Check match confidence
match_result = TemplateHelper.match_template("template.png")
if match_result:
    x, y, confidence = match_result
    print(f"Match confidence: {confidence:.3f}")
```

#### OCR Debugging  
```python
# Save OCR debug image với bounding boxes
debug_path = ImageHelper.save_debug_image_with_boxes(
    image, ocr_data, "ocr_debug.png"
)

# Check extracted text
words = OCRHelper.get_text_words(ocr_data)
print(f"OCR words: {words}")
```

#### Threading Debugging
```python
# Add logging to thread operations
print(f"Thread {threading.current_thread().name}: Acquiring lock")
print(f"Manual active: {self._manual_active}")
print(f"Auto detect active: {self.auto_detect_active}")
```

### Performance Optimization

#### Template Matching Optimization
- **Cache templates** in memory
- **Reduce search area** with ROI
- **Use multi-scale matching** for DPI variations  
- **Parallel processing** for multiple templates

#### OCR Optimization
- **Crop to relevant areas** only
- **Preprocess images** (contrast, sharpening)
- **Cache OCR results** for repeated text
- **Use confidence filtering**

#### Threading Optimization
- **Non-blocking lock acquisition**
- **Responsive sleep intervals**
- **Priority-based scheduling**
- **Proper resource cleanup**

---

*🎯 **Features Guide Complete** - Mọi thông tin cần thiết để master từng plugin detector!*
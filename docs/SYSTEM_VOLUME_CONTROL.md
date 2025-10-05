# System Volume Control - Điều Chỉnh Âm Lượng Ứng Dụng

## 📌 Tổng Quan

Tính năng **System Volume Control** cho phép điều chỉnh âm lượng của một ứng dụng cụ thể (như Chrome, Spotify, Edge, v.v.) trực tiếp từ GUI của Cubase Auto Tool, sử dụng **Windows Audio Session API** thông qua thư viện `pycaw`.

### 🆕 Thay Đổi So Với Cũ

| **Trước** | **Sau** |
|-----------|---------|
| Slider + nút "OK" + nút "M" | Nút "-" / "+" / "🔊" |
| Điều chỉnh volume trong Cubase | Điều chỉnh volume của app (Chrome, etc.) |
| Giá trị từ -7 đến 0 | Phần trăm từ 0% đến 100% |
| Cần bấm "OK" để áp dụng | Áp dụng ngay lập tức |

---

## 🛠️ Cấu Hình

### **File: `default_values.txt`**

```txt
# System Volume Control (Windows Audio Session)
system_volume_app_name=chrome.exe
system_volume_step=5
```

### **Tham Số**

| Tham số | Mô tả | Giá trị mặc định | Ví dụ |
|---------|-------|------------------|-------|
| `system_volume_app_name` | Tên process của ứng dụng cần điều khiển | `chrome.exe` | `msedge.exe`, `spotify.exe`, `firefox.exe` |
| `system_volume_step` | Bước tăng/giảm volume (phần trăm) | `5` | `10`, `2`, `1` |

---

## 🎮 Cách Sử Dụng

### **1. Tăng Volume**
- Bấm nút **"+"** để tăng volume theo `system_volume_step`
- Giá trị hiển thị sẽ cập nhật ngay lập tức (ví dụ: `50%` → `55%`)

### **2. Giảm Volume**
- Bấm nút **"-"** để giảm volume theo `system_volume_step`
- Giá trị hiển thị sẽ cập nhật ngay lập tức (ví dụ: `50%` → `45%`)

### **3. Mute/Unmute**
- Bấm nút **"🔊"** để mute
  - Icon đổi thành **"🔇"**
  - Màu đổi thành đỏ (`#E91E63`)
  - Volume set về 0%
- Bấm lại để unmute
  - Icon đổi thành **"🔊"**
  - Màu đổi thành xanh (`#4CAF50`)
  - Volume restore về 50%

---

## 🔧 Chi Tiết Kỹ Thuật

### **Class: `SystemVolumeDetector`**

**File:** `features/system_volume_detector.py`

#### **Khởi tạo**
```python
from features.system_volume_detector import SystemVolumeDetector

detector = SystemVolumeDetector("chrome.exe")
```

#### **Methods**

| Method | Mô tả | Return |
|--------|-------|--------|
| `get_volume()` | Lấy volume hiện tại (0.0 - 1.0) | `float` |
| `set_volume(value)` | Set volume (0.0 - 1.0) | `bool` |
| `get_volume_percent()` | Lấy volume theo % (0 - 100) | `int` |
| `set_volume_percent(percent)` | Set volume theo % | `bool` |
| `increase_volume(step_percent)` | Tăng volume | `bool` |
| `decrease_volume(step_percent)` | Giảm volume | `bool` |
| `toggle_mute()` | Toggle mute/unmute | `bool` |
| `is_muted()` | Kiểm tra mute status | `bool` |
| `get_app_name()` | Lấy tên app đang điều khiển | `str` |
| `set_app_name(app_name)` | Đổi app cần điều khiển | `None` |

#### **Ví dụ sử dụng**

```python
# Khởi tạo
detector = SystemVolumeDetector("chrome.exe")

# Lấy volume hiện tại
current = detector.get_volume_percent()  # 50

# Tăng 5%
detector.increase_volume(5)  # 55%

# Giảm 10%
detector.decrease_volume(10)  # 45%

# Set trực tiếp
detector.set_volume_percent(75)  # 75%

# Mute
detector.toggle_mute()  # Muted

# Kiểm tra
if detector.is_muted():
    print("Currently muted")

# Đổi app
detector.set_app_name("spotify.exe")
```

---

## 🖥️ UI Integration

### **Music Section Component**

**File:** `gui/components/music_section.py`

#### **Layout**
```
┌─────────────────────────────────────┐
│ Volume  [ - ]  50%  [ + ]  🔊      │
└─────────────────────────────────────┘
```

#### **Event Handlers**
- `_increase_volume()` → `main_window._increase_system_volume()`
- `_decrease_volume()` → `main_window._decrease_system_volume()`
- `_toggle_mute()` → `main_window._toggle_system_mute()`

---

## ⚠️ Lưu Ý

### **1. App Phải Đang Chạy**
- Nếu app không chạy, sẽ hiển thị: `⚠️ Failed to ... (app may not be running)`
- Giá trị hiển thị không thay đổi

### **2. Tên Process Phải Chính Xác**
- Sử dụng **tên process**, không phải tên ứng dụng
- Ví dụ:
  - ✅ `chrome.exe`
  - ❌ `Google Chrome`

### **3. Cách Tìm Tên Process**
1. Mở **Task Manager** (Ctrl+Shift+Esc)
2. Tab **Details**
3. Tìm ứng dụng → xem cột **Name**

### **4. Một Số Tên Process Phổ Biến**
| Ứng dụng | Process Name |
|----------|--------------|
| Google Chrome | `chrome.exe` |
| Microsoft Edge | `msedge.exe` |
| Firefox | `firefox.exe` |
| Spotify | `spotify.exe` |
| VLC Media Player | `vlc.exe` |
| Discord | `Discord.exe` |

---

## 🐛 Troubleshooting

### **❌ "ModuleNotFoundError: No module named 'pycaw'"**

**Giải pháp:**
```bash
.\venv\Scripts\activate
pip install pycaw
```

### **❌ "Failed to get/set volume"**

**Nguyên nhân:**
- App không đang chạy
- Tên process sai
- App không phát audio (chưa tạo audio session)

**Giải pháp:**
1. Kiểm tra app đang chạy
2. Phát audio một lần (để tạo audio session)
3. Thử lại

### **⚠️ Volume display không update**

**Nguyên nhân:**
- App bị crash
- Audio session bị đóng

**Giải pháp:**
- Restart app cần điều khiển
- Restart Cubase Auto Tool

---

## 🎯 Use Cases

### **1. Điều Chỉnh Volume Nhạc Beat**
```txt
system_volume_app_name=chrome.exe  # YouTube beats
system_volume_step=5
```
→ Tăng/giảm volume beat từ Chrome trực tiếp

### **2. Điều Chỉnh Volume Spotify**
```txt
system_volume_app_name=spotify.exe
system_volume_step=10
```
→ Tăng/giảm volume Spotify nhanh hơn

### **3. Mute Nhanh Khi Cần**
- Bấm **🔊** để mute ngay lập tức
- Không cần alt-tab sang Spotify/Chrome

---

## 📊 Debug Logs

Khi thao tác với System Volume, logs sẽ hiển thị:

```
🔊 System Volume Detector initialized for: chrome.exe
🔊 Initial system volume: 50% (muted: False)
✅ Increased system volume to 55%
✅ Decreased system volume to 45%
✅ System volume muted
✅ System volume unmuted
⚠️ Application chrome.exe not found in audio sessions
```

---

## 🚀 Future Enhancements

- [ ] Dropdown để chọn app từ list
- [ ] Auto-detect app đang phát audio
- [ ] Preset volume levels (Low/Med/High)
- [ ] Volume sync với Cubase
- [ ] Multi-app control (điều khiển nhiều app cùng lúc)

---

**Updated:** October 5, 2025  
**Author:** Cubase Auto Tool Development Team


# Auto-Pause System Documentation

## Tổng quan
Hệ thống Auto-Pause đảm bảo auto-detect luôn có priority thấp nhất và sẽ tạm dừng khi có bất kỳ manual operation nào.

## Cách sử dụng cho chức năng mới

### 1. Trong GUI Method
```python
def _your_new_feature(self):
    """Chức năng mới của bạn."""
    # Pause auto-detect
    self.pause_auto_detect_for_manual_action()
    
    try:
        # Code chức năng của bạn ở đây
        print("🚀 Đang thực hiện chức năng...")
        # ... thực hiện logic ...
        print("✅ Chức năng hoàn thành!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        
    finally:
        # Luôn resume auto-detect (dù có lỗi hay không)
        self.resume_auto_detect_after_manual_action()
```

### 2. Sử dụng Decorator (Alternative)
```python
from utils.auto_pause_decorator import pause_auto_on_manual

@pause_auto_on_manual(self)  # self là GUI instance
def _your_new_feature(self):
    """Chức năng mới với decorator."""
    # Code chức năng ở đây, decorator tự động pause/resume
    print("🚀 Chức năng chạy...")
```

## Workflow
1. **Manual operation bắt đầu** → `pause_auto_detect_for_manual_action()`
2. **Auto-detect thấy flag** → tạm dừng ngay lập tức
3. **Manual operation hoàn thành** → `resume_auto_detect_after_manual_action()`  
4. **Auto-detect tiếp tục** bình thường

## Lưu ý quan trọng
- **Luôn dùng try/finally** để đảm bảo resume được gọi
- **Auto-detect sẽ đợi 0.5 giây** mỗi lần check flag
- **Áp dụng cho TẤT CẢ manual operations** để tránh conflict

## Example Implementation
Xem `_example_music_feature()` trong `gui.py` làm template.
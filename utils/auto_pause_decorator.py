"""Decorator để tự động pause/resume auto-detect cho manual operations."""

import functools

def pause_auto_on_manual(gui_instance):
    """
    Decorator tự động pause auto-detect khi chạy manual function,
    và resume lại sau khi hoàn thành.
    
    Args:
        gui_instance: Instance của GUI có methods pause/resume auto-detect
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Pause auto-detect
            gui_instance.pause_auto_detect_for_manual_action()
            
            try:
                # Chạy function gốc
                result = func(*args, **kwargs)
                return result
            finally:
                # Luôn resume auto-detect dù có lỗi hay không
                gui_instance.resume_auto_detect_after_manual_action()
        
        return wrapper
    return decorator
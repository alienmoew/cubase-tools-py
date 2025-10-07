"""
Fast Batch Operations for Auto-Tune Parameters
Tối ưu hóa timing và batch processing
"""
import time
import config

class FastBatchProcessor:
    """Class xử lý batch operations nhanh cho Auto-Tune parameters."""
    
    @staticmethod 
    def set_fast_timing():
        """Tạm thời set timing nhanh cho batch operations."""
        # Backup original timings
        original_timings = {
            'click_delay': config.UI_DELAYS.get('click_delay', 0.15),
            'click_delay_short': config.UI_DELAYS.get('click_delay_short', 0.2),
            'window_focus': config.UI_DELAYS.get('window_focus', 0.3)
        }
        
        # Set fast timings
        config.UI_DELAYS['click_delay'] = config.UI_DELAYS.get('fast_click_delay', 0.05)
        config.UI_DELAYS['click_delay_short'] = config.UI_DELAYS.get('fast_click_delay', 0.05) 
        config.UI_DELAYS['window_focus'] = 0.1
        
        return original_timings
    
    @staticmethod
    def restore_timing(original_timings):
        """Khôi phục timing gốc."""
        config.UI_DELAYS.update(original_timings)
    
    @staticmethod
    def execute_fast_batch(operations, window_manager=None):
        """
        Thực hiện batch operations với timing tối ưu và cursor management.
        
        Args:
            operations: List of dict containing operation info
            window_manager: Optional pre-focused window manager
            
        Returns:
            tuple: (success_count, total_count)
        """
        if not operations:
            return 0, 0
            
        # Set fast timing
        original_timings = FastBatchProcessor.set_fast_timing()
        
        # Start batch cursor management
        from utils.helpers import MouseHelper
        original_cursor_pos = MouseHelper.batch_click_start()
        print(f"🖱️ Starting batch mode - cursor saved at {original_cursor_pos}")
        
        try:
            success_count = 0
            
            # Focus window once if needed
            if window_manager:
                try:
                    cubase_window = window_manager.find_cubase_window()
                    if cubase_window:
                        window_manager.focus_window(cubase_window)
                        time.sleep(0.1)  # Minimal focus delay
                except Exception as e:
                    print(f"⚠️ Window focus warning: {e}")
            
            # Execute operations rapidly with batch cursor management
            for i, operation in enumerate(operations):
                try:
                    # Execute the operation
                    if 'detector' in operation and 'method' in operation:
                        detector = operation['detector']
                        method_name = operation['method']
                        args = operation.get('args', [])
                        
                        # Use batch method if available
                        if method_name == 'reset_to_default' and hasattr(detector, 'set_auto_tune_value_batch'):
                            # Use batch version for AutoTune detectors
                            default_value = getattr(detector, 'default_value', 0)
                            result = detector.set_auto_tune_value_batch(default_value, original_cursor_pos)
                        elif hasattr(detector, method_name):
                            method = getattr(detector, method_name)
                            result = method(*args) if args else method()
                        else:
                            print(f"❌ Method {method_name} not found in detector")
                            continue
                        
                        if result:
                            success_count += 1
                            print(f"✅ {operation.get('name', f'Operation {i+1}')}")
                        else:
                            print(f"❌ {operation.get('name', f'Operation {i+1}')} failed")
                    
                    # Minimal delay between operations
                    if i < len(operations) - 1:
                        time.sleep(config.UI_DELAYS.get('batch_reset_delay', 0.1))
                        
                except Exception as e:
                    print(f"❌ Error in operation {operation.get('name', i)}: {e}")
            
            return success_count, len(operations)
            
        finally:
            # Restore cursor position once at the end
            MouseHelper.batch_click_end(original_cursor_pos, return_mode="instant", delay=0.1)
            print(f"🖱️ Batch completed - cursor restored to {original_cursor_pos}")
            
            # Always restore original timing
            FastBatchProcessor.restore_timing(original_timings)
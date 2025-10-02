"""
Ultra Fast Batch AutoTune Processor
Tối ưu hóa cực kỳ để set nhiều giá trị AutoTune cùng lúc
"""
import time
import config
from utils.helpers import MouseHelper
from utils.process_finder import CubaseProcessFinder
from utils.window_manager import WindowManager
import pyautogui

class UltraFastAutoTuneProcessor:
    """Processor siêu nhanh cho batch AutoTune operations."""
    
    def __init__(self):
        self.cubase_proc = None
        self.plugin_window = None
        self.original_cursor_pos = None
        
    def prepare_batch_session(self):
        """Chuẩn bị session - chỉ cần làm 1 lần cho toàn bộ batch."""
        try:
            # 1. Save cursor position
            self.original_cursor_pos = MouseHelper.batch_click_start()
            print("🖱️ Cursor position saved for ultra fast batch")
            
            # 2. Find Cubase process once
            self.cubase_proc = CubaseProcessFinder.find()
            if not self.cubase_proc:
                print("❌ Cubase process not found")
                return False
                
            # 3. Focus Cubase window once
            hwnd = WindowManager.focus_window_by_pid(self.cubase_proc.info["pid"])
            if not hwnd:
                print("❌ Cannot focus Cubase window")
                return False
                
            # Fast focus delay
            time.sleep(config.FOCUS_DELAY_FAST)
            
            # 4. Find plugin window once
            self.plugin_window = WindowManager.find_window("AUTO-TUNE")
            if not self.plugin_window:
                print("❌ AUTO-TUNE plugin window not found")
                return False
                
            self.plugin_window.activate()
            time.sleep(config.FOCUS_DELAY_FAST)
            
            print("✅ Batch session prepared successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error preparing batch session: {e}")
            return False
    
    def execute_ultra_fast_batch(self, parameters_list):
        """
        Thực hiện ultra fast batch với list parameters.
        
        Args:
            parameters_list: List of dict với format:
            [
                {'detector': detector_instance, 'value': target_value, 'name': 'Parameter Name'},
                ...
            ]
        """
        if not parameters_list:
            return 0, 0
            
        if not self.prepare_batch_session():
            return 0, 0
            
        try:
            success_count = 0
            total_count = len(parameters_list)
            
            print(f"🚀 Starting ultra fast batch for {total_count} parameters")
            
            # Phase 1: Find all templates at once (parallel preparation)
            template_positions = {}
            for param in parameters_list:
                try:
                    detector = param['detector']
                    name = param['name']
                    
                    # Find template position
                    click_pos, confidence = detector._find_template_match(self.plugin_window)
                    if click_pos:
                        template_positions[name] = {
                            'click_pos': click_pos,
                            'detector': detector,
                            'value': param['value'],
                            'confidence': confidence
                        }
                        print(f"📍 {name} template found at {click_pos} (confidence: {confidence:.3f})")
                    else:
                        print(f"❌ {name} template not found")
                        
                except Exception as e:
                    print(f"❌ Error finding template for {param['name']}: {e}")
            
            # Phase 2: Execute all operations super fast
            fast_delay = config.UI_DELAYS.get('auto_tune_input_delay', 0.05)
            
            for name, template_info in template_positions.items():
                try:
                    click_pos = template_info['click_pos']
                    value = template_info['value']
                    detector = template_info['detector']
                    
                    # Ultra fast click and input
                    click_x, click_y = click_pos
                    
                    # Fast click without cursor restoration
                    MouseHelper.batch_click(click_x, click_y, delay=fast_delay)
                    
                    # Ultra fast input sequence
                    time.sleep(fast_delay)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(fast_delay) 
                    pyautogui.typewrite(str(value))
                    time.sleep(fast_delay)
                    pyautogui.press('enter')
                    
                    # Update detector internal value
                    detector.set_value(value)
                    
                    success_count += 1
                    print(f"⚡ {name}: {value} (ultra fast)")
                    
                    # Minimal delay between parameters
                    if name != list(template_positions.keys())[-1]:
                        time.sleep(config.UI_DELAYS.get('batch_reset_delay', 0.05))
                    
                except Exception as e:
                    print(f"❌ Error processing {name}: {e}")
            
            print(f"✅ Ultra fast batch completed: {success_count}/{total_count}")
            return success_count, total_count
            
        except Exception as e:
            print(f"❌ Ultra fast batch error: {e}")
            return 0, len(parameters_list)
        finally:
            self.cleanup_batch_session()
    
    def cleanup_batch_session(self):
        """Dọn dẹp sau batch session."""
        try:
            if self.original_cursor_pos:
                MouseHelper.batch_click_end(self.original_cursor_pos, return_mode="instant", delay=0.1)
                print("🖱️ Cursor restored to original position")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
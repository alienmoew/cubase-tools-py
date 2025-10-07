"""
Helper class để quản lý các bypass toggle trong GUI, tránh code trùng lặp.
"""
from utils.debug_helper import DebugHelper


class BypassToggleManager:
    """Quản lý tất cả bypass toggles để tránh code trùng lặp."""
    
    def __init__(self, gui_instance):
        """Khởi tạo với reference tới GUI instance."""
        self.gui = gui_instance
        
        # Dictionary lưu thông tin tất cả bypass toggles
        self.toggles = {
            'plugin': {
                'detector': None,  # Sẽ được set từ GUI
                'toggle_widget': None,
                'status_label': None,
                'state': False,
                'plugin_name': 'AUTO-TUNE PRO'
            },
            'soundshifter': {
                'detector': None,
                'toggle_widget': None,
                'status_label': None,
                'state': False,
                'plugin_name': 'SoundShifter Pitch Stereo'
            },
            'proq3': {
                'detector': None,
                'toggle_widget': None,
                'status_label': None,
                'state': False,
                'plugin_name': 'Pro-Q 3 (Lofi)'
            }
        }
    
    def register_toggle(self, toggle_id, detector, toggle_widget, status_label):
        """Đăng ký một bypass toggle."""
        if toggle_id in self.toggles:
            self.toggles[toggle_id]['detector'] = detector
            self.toggles[toggle_id]['toggle_widget'] = toggle_widget
            self.toggles[toggle_id]['status_label'] = status_label
            DebugHelper.print_init_debug(f"✅ Registered bypass toggle: {toggle_id}")
        else:
            DebugHelper.print_always(f"❌ Unknown toggle ID: {toggle_id}")
    
    def toggle_bypass(self, toggle_id):
        """Generic bypass toggle handler."""
        if toggle_id not in self.toggles:
            print(f"❌ Unknown toggle ID: {toggle_id}")
            return
        
        toggle_info = self.toggles[toggle_id]
        detector = toggle_info['detector']
        toggle_widget = toggle_info['toggle_widget']
        plugin_name = toggle_info['plugin_name']
        
        # Pause auto-detect during operation
        self.gui.pause_auto_detect_for_manual_action()
        
        # Đợi một chút để đảm bảo auto-detect hoàn toàn pause
        import time
        time.sleep(0.2)
        
        try:
            # Lấy trạng thái hiện tại của toggle
            toggle_value = toggle_widget.get()
            
            DebugHelper.print_general_debug(f"🎚️ {plugin_name} bypass toggle changed to: {'ON' if toggle_value else 'OFF'}")
            
            # Cập nhật UI trước
            self.update_bypass_ui(toggle_id, toggle_value)
            
            # Thực hiện toggle trong Cubase
            success = detector.toggle_plugin_bypass()
            
            if success:
                DebugHelper.print_always(f"✅ {plugin_name} bypass toggled successfully")
                # Sync toggle state với actual plugin state nếu có thể
                self.sync_toggle_with_plugin_state(toggle_id)
            else:
                DebugHelper.print_always(f"❌ {plugin_name} bypass toggle failed")
                # Revert toggle nếu thất bại
                self.revert_toggle_state(toggle_id)
                
        except Exception as e:
            DebugHelper.print_always(f"❌ Error in {plugin_name} bypass toggle: {e}")
            self.revert_toggle_state(toggle_id)
        finally:
            # Resume auto-detect
            self.gui.resume_auto_detect_after_manual_action()
    
    def update_bypass_ui(self, toggle_id, is_on):
        """Generic UI update cho bypass toggle."""
        if toggle_id not in self.toggles:
            return
        
        toggle_info = self.toggles[toggle_id]
        status_label = toggle_info['status_label']
        
        # Lấy tên ngắn gọn của plugin
        plugin_names = {
            'plugin': 'Auto-Tune',
            'soundshifter': 'Tone Nhạc',
            'proq3': 'Lofi'
        }
        plugin_name = plugin_names.get(toggle_id, 'Plugin')
        
        if is_on:  # Plugin ON (active)
            status_label.configure(
                text=plugin_name,
                text_color="#4CAF50"  # Green
            )
            toggle_info['state'] = False  # ON means not bypassed
        else:  # Plugin OFF (bypassed)
            status_label.configure(
                text=plugin_name,
                text_color="#FF4444"  # Red
            )
            toggle_info['state'] = True  # OFF means bypassed
    
    def sync_toggle_with_plugin_state(self, toggle_id):
        """Generic sync toggle state với plugin state."""
        if toggle_id not in self.toggles:
            return
        
        toggle_info = self.toggles[toggle_id]
        detector = toggle_info['detector']
        toggle_widget = toggle_info['toggle_widget']
        
        try:
            # Lấy trạng thái hiện tại từ detector
            if hasattr(detector, 'current_state'):
                actual_state = detector.current_state
                if actual_state is not None:
                    # Cập nhật toggle để match với trạng thái thực tế
                    if actual_state != toggle_widget.get():
                        # Tạm thời tắt callback để tránh recursive call
                        old_command = toggle_widget.cget("command")
                        toggle_widget.configure(command=None)
                        toggle_widget.select() if actual_state else toggle_widget.deselect()
                        toggle_widget.configure(command=old_command)
                        # Cập nhật UI
                        self.update_bypass_ui(toggle_id, actual_state)
        except Exception as e:
            plugin_name = toggle_info['plugin_name']
            DebugHelper.print_general_debug(f"❌ Error syncing {plugin_name} toggle state: {e}")
    
    def revert_toggle_state(self, toggle_id):
        """Generic revert toggle state nếu operation thất bại."""
        if toggle_id not in self.toggles:
            return
        
        toggle_info = self.toggles[toggle_id]
        toggle_widget = toggle_info['toggle_widget']
        plugin_name = toggle_info['plugin_name']
        
        try:
            # Tắt callback tạm thời để tránh recursive call
            old_command = toggle_widget.cget("command")
            toggle_widget.configure(command=None)
            
            # Revert toggle state
            current_toggle_state = toggle_widget.get()
            if current_toggle_state:
                toggle_widget.deselect()
                self.update_bypass_ui(toggle_id, False)
            else:
                toggle_widget.select()
                self.update_bypass_ui(toggle_id, True)
            
            # Khôi phục callback
            toggle_widget.configure(command=old_command)
            
        except Exception as e:
            DebugHelper.print_general_debug(f"❌ Error reverting {plugin_name} toggle state: {e}")
    
    def initialize_toggle_state(self, toggle_id):
        """Generic initialization cho toggle state."""
        if toggle_id not in self.toggles:
            return
        
        toggle_info = self.toggles[toggle_id]
        detector = toggle_info['detector']
        toggle_widget = toggle_info['toggle_widget']
        plugin_name = toggle_info['plugin_name']
        
        try:
            DebugHelper.print_init_debug(f"🔄 Checking initial {plugin_name} plugin state...")
            
            # Thử detect trạng thái plugin hiện tại - silent mode
            state_result = detector.get_current_state(silent=True)
            
            if state_result and state_result[0] is not None:
                current_state = state_result[0]
                DebugHelper.print_init_debug(f"✅ Detected {plugin_name} plugin state: {'ON' if current_state else 'OFF'}")
                
                # Tạm thời tắt callback
                toggle_widget.configure(command=None)
                
                # Set toggle theo trạng thái thực tế
                if current_state:  # Plugin ON
                    toggle_widget.select()
                else:  # Plugin OFF
                    toggle_widget.deselect()
                
                # Restore callback và cập nhật UI
                toggle_widget.configure(command=lambda t_id=toggle_id: self.toggle_bypass(t_id))
                self.update_bypass_ui(toggle_id, current_state)
            else:
                DebugHelper.print_init_debug(f"❓ Cannot detect {plugin_name} plugin state - setting default to ON")
                # Default state khi không detect được
                toggle_widget.select()  # Default ON
                self.update_bypass_ui(toggle_id, True)
                
        except Exception as e:
            DebugHelper.print_init_debug(f"❌ Error initializing {plugin_name} plugin toggle state: {e}")
            # Fallback to default state
            toggle_widget.select()
            self.update_bypass_ui(toggle_id, True)
    
    def initialize_all_toggles(self):
        """Khởi tạo tất cả toggle states."""
        for toggle_id in self.toggles:
            if self.toggles[toggle_id]['detector'] is not None:
                self.initialize_toggle_state(toggle_id)
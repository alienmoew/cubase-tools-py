"""
Shared window management utilities để loại bỏ code trùng lặp.
"""
import time
import config
from utils.window_manager import WindowManager
from utils.helpers import MessageHelper


class SharedWindowManager:
    """Unified window management cho tất cả plugins."""
    
    @staticmethod
    def focus_plugin_window(plugin_key, proc, silent=False):
        """
        Focus và activate plugin window.
        
        Args:
            plugin_key: Key trong config.PLUGIN_NAMES ('autotune', 'soundshifter', etc.)
            proc: Cubase process object
            silent: Có in debug messages không
            
        Returns:
            plugin_win object hoặc None nếu thất bại
        """
        plugin_name = config.PLUGIN_NAMES.get(plugin_key)
        if not plugin_name:
            if not silent:
                print(f"❌ Unknown plugin key: {plugin_key}")
            return None
        
        try:
            # 1. Focus Cubase process
            hwnd = WindowManager.focus_window_by_pid(proc.info["pid"])
            if not hwnd:
                if not silent:
                    print("❌ Không thể focus cửa sổ Cubase!")
                    MessageHelper.show_error(
                        "Lỗi Focus Window", 
                        "Không thể focus cửa sổ Cubase!"
                    )
                return None
            
            time.sleep(config.UI_DELAYS['window_focus'])
            
            # 2. Tìm cửa sổ plugin
            plugin_win = WindowManager.find_window(plugin_name)
            if not plugin_win:
                if not silent:
                    print(f"❌ Không tìm thấy cửa sổ {plugin_name}!")
                    MessageHelper.show_error(
                        f"Lỗi Plugin {plugin_name}", 
                        f"Không tìm thấy plugin {plugin_name}!\n\n"
                        f"Vui lòng:\n"
                        f"• Mở plugin {plugin_name} trong Cubase\n"
                        f"• Đảm bảo cửa sổ plugin hiển thị trên màn hình"
                    )
                return None

            # 3. Activate plugin window
            plugin_win.activate()
            time.sleep(config.UI_DELAYS['plugin_activate'])
            
            if not silent:
                print(f"✅ Đã tìm thấy và activated cửa sổ {plugin_name}")
            
            return plugin_win
            
        except Exception as e:
            if not silent:
                print(f"❌ Error focusing {plugin_name} window: {e}")
            return None
    
    @staticmethod
    def focus_plugin_window_silent(plugin_key, proc):
        """Silent version của focus_plugin_window."""
        return SharedWindowManager.focus_plugin_window(plugin_key, proc, silent=True)
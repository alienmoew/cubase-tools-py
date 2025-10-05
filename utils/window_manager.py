import pygetwindow as gw
import pyautogui
import win32gui
import win32con
import win32process

class WindowManager:
    """Quản lý focus window và chụp screenshot."""

    @staticmethod
    def focus_window_by_pid(pid):
        hwnd_found = []

        def callback(hwnd, extra):
            try:
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid:
                        # Try different methods to ensure focus
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # restore nếu minimize
                        win32gui.BringWindowToTop(hwnd)  # Bring to top first
                        win32gui.SetForegroundWindow(hwnd)
                        hwnd_found.append(hwnd)
            except Exception as e:
                print(f"⚠️ Window focus callback error: {e}")
                pass

        try:
            win32gui.EnumWindows(callback, None)
            
            # Additional fallback: try pygetwindow if win32 fails
            if not hwnd_found:
                print("🔄 Trying pygetwindow fallback...")
                import psutil
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                    windows = gw.getWindowsWithTitle("")  # Get all windows
                    for window in windows:
                        if "cubase" in window.title.lower() or proc_name.lower() in window.title.lower():
                            try:
                                window.activate()
                                print(f"✅ Fallback focus successful: {window.title}")
                                return True
                            except:
                                continue
                except Exception as e:
                    print(f"⚠️ Fallback focus error: {e}")
            
            return hwnd_found[0] if hwnd_found else None
            
        except Exception as e:
            print(f"❌ Critical error in focus_window_by_pid: {e}")
            return None

    @staticmethod
    def find_window(title_keyword):
        windows = gw.getWindowsWithTitle(title_keyword)
        if windows:
            return windows[0]
        return None

    @staticmethod
    def screenshot_window(window, save_path):
        left, top, right, bottom = window.left, window.top, window.right, window.bottom
        screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
        screenshot.save(save_path)
        return save_path
    
    @staticmethod
    def get_window_rect(hwnd):
        """Lấy kích thước và vị trí window từ hwnd."""
        try:
            import win32gui
            rect = win32gui.GetWindowRect(hwnd)
            if rect:
                left, top, right, bottom = rect
                return (left, top, right - left, bottom - top)  # (x, y, width, height)
            return None
        except Exception as e:
            print(f"❌ Error getting window rect: {e}")
            return None

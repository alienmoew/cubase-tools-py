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
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # restore nếu minimize
                    win32gui.SetForegroundWindow(hwnd)
                    hwnd_found.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return hwnd_found[0] if hwnd_found else None

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

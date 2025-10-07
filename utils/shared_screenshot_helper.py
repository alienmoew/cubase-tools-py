"""
Shared screenshot utilities để loại bỏ code trùng lặp.
"""
import pyautogui
import numpy as np
import cv2


class SharedScreenshotHelper:
    """Unified screenshot handling cho tất cả plugins."""
    
    @staticmethod
    def capture_plugin_region(plugin_win):
        """
        Chụp ảnh plugin window và convert sang numpy arrays.
        
        Args:
            plugin_win: Plugin window object
            
        Returns:
            tuple: (x, y, w, h, screenshot_np, screenshot_gray)
        """
        # Get window dimensions
        x, y, w, h = plugin_win.left, plugin_win.top, plugin_win.width, plugin_win.height
        
        # Capture screenshot
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        
        return x, y, w, h, screenshot_np, screenshot_gray
    
    @staticmethod
    def calculate_click_position(x, y, location, template_size):
        """
        Tính toán vị trí click ở giữa template.
        
        Args:
            x, y: Window position
            location: Template match location
            template_size: (width, height) of template
            
        Returns:
            tuple: (click_x, click_y)
        """
        template_w, template_h = template_size
        click_x = x + location[0] + template_w // 2
        click_y = y + location[1] + template_h // 2
        
        return click_x, click_y
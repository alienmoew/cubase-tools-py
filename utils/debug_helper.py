"""
Debug helper để quản lý debug output và giảm noise khi initialization.
"""
import config


class DebugHelper:
    """Helper class để quản lý debug output."""
    
    @staticmethod
    def should_debug_initialization():
        """Kiểm tra có nên debug khi initialization không."""
        return config.DEBUG_INITIALIZATION and config.DEBUG_MODE
    
    @staticmethod
    def should_debug_template_matching():
        """Kiểm tra có nên debug template matching không."""
        return config.DEBUG_TEMPLATE_MATCHING and config.DEBUG_MODE
    
    @staticmethod
    def should_save_debug_images():
        """Kiểm tra có nên lưu debug images không."""
        return config.DEBUG_SAVE_IMAGES and config.DEBUG_MODE
    
    @staticmethod
    def print_init_debug(message):
        """In debug message cho initialization nếu được bật."""
        if DebugHelper.should_debug_initialization():
            print(message)
        elif not config.SILENT_INITIALIZATION:
            print(message)
    
    @staticmethod
    def print_template_debug(message):
        """In debug message cho template matching nếu được bật."""
        if DebugHelper.should_debug_template_matching():
            print(message)
    
    @staticmethod
    def print_general_debug(message):
        """In general debug message nếu debug mode được bật."""
        if config.DEBUG_MODE:
            print(message)
    
    @staticmethod
    def print_always(message):
        """In message luôn luôn (cho success/error messages quan trọng)."""
        print(message)
"""Settings manager để lưu trữ user preferences."""
import json
import os
import config

class SettingsManager:
    """Quản lý settings của ứng dụng."""
    
    def __init__(self):
        self.settings_file = config.SETTINGS_FILE
        self.default_settings = {
            "theme": config.DEFAULT_THEME,
            "auto_detect": False
        }
    
    def load_settings(self):
        """Load settings từ file, trả về default nếu file không tồn tại."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # Ensure all default keys exist
                for key, value in self.default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Error loading settings: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self, settings):
        """Lưu settings vào file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error saving settings: {e}")
    
    def get_theme(self):
        """Lấy theme hiện tại từ settings."""
        settings = self.load_settings()
        return settings.get("theme", config.DEFAULT_THEME)
    
    def set_theme(self, theme):
        """Lưu theme mới."""
        settings = self.load_settings()
        settings["theme"] = theme
        self.save_settings(settings)
    
    def get_auto_detect(self):
        """Lấy trạng thái auto detect."""
        settings = self.load_settings()
        auto_detect_value = settings.get("auto_detect", False)
        # Handle both boolean and numeric values for backward compatibility
        return bool(auto_detect_value)
    
    def set_auto_detect(self, enabled):
        """Lưu trạng thái auto detect."""
        settings = self.load_settings()
        settings["auto_detect"] = bool(enabled)  # Ensure boolean type
        self.save_settings(settings)
from features.plugin_bypass_detector import PluginBypassDetector


class ProQ3BypassDetector(PluginBypassDetector):
    """Tính năng Bật/Tắt plugin cho Pro-Q 3 (đặt tên Lofi)."""

    def __init__(self):
        super().__init__(plugin_name="Pro-Q 3")
        
        # Sử dụng chung template bypass với PluginBypassDetector (AUTO-TUNE PRO)
        # Không override template paths để dùng chung
        
        # Override feature info
        self.feature_name = "Lofi Toggle"
        self.config_prefix = "proq3_bypass"
    
    # Methods được inherit từ parent class với SharedWindowManager
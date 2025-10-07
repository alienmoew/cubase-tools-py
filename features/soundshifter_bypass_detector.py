from features.plugin_bypass_detector import PluginBypassDetector


class SoundShifterBypassDetector(PluginBypassDetector):
    """Tính năng Bật/Tắt plugin cho SoundShifter Pitch Stereo."""

    def __init__(self):
        super().__init__(plugin_name="SoundShifter Pitch Stereo")
        
        # Sử dụng chung template bypass với PluginBypassDetector (AUTO-TUNE PRO)
        # Không override template paths để dùng chung
        
        # Override feature info
        self.feature_name = "SoundShifter Bypass"
        self.config_prefix = "soundshifter_bypass"
    
    # Methods được inherit từ parent class với SharedWindowManager
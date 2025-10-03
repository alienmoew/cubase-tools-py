"""
AutoTune Controls Detector - Điều chỉnh tất cả controls của plugin AUTO-TUNE PRO
Bao gồm: Return Speed, Flex Tune, Natural Vibrato, Humanize
"""
from features.auto_tune_detector import AutoTuneDetector
from utils.helpers import ConfigHelper

class AutoTuneControlsDetector:
    """Tính năng điều chỉnh tất cả controls của AUTO-TUNE PRO plugin."""
    
    def __init__(self):
        # Load default values
        self.default_values = ConfigHelper.load_default_values()
        
        # Initialize individual detectors for each control
        self.return_speed_detector = AutoTuneDetector(
            feature_name="Return Speed",
            template_filename="return_speed_template.png",
            config_prefix="return_speed"
        )
        
        self.flex_tune_detector = AutoTuneDetector(
            feature_name="Flex Tune", 
            template_filename="flex_tune_template.png",
            config_prefix="flex_tune"
        )
        
        self.natural_vibrato_detector = AutoTuneDetector(
            feature_name="Natural Vibrato",
            template_filename="natural_vibrato_template.png", 
            config_prefix="natural_vibrato"
        )
        
        self.humanize_detector = AutoTuneDetector(
            feature_name="Humanize",
            template_filename="humanize_template.png",
            config_prefix="humanize"
        )
        
        # Current values
        self.current_return_speed = self.default_values.get('return_speed_default', 5)
        self.current_flex_tune = self.default_values.get('flex_tune_default', 5)
        self.current_natural_vibrato = self.default_values.get('natural_vibrato_default', 5)
        self.current_humanize = self.default_values.get('humanize_default', 5)
        
    def get_name(self):
        """Trả về tên hiển thị của detector."""
        return "AutoTune Controls"
    
    # ==================== RETURN SPEED METHODS ====================
    
    def set_return_speed_value(self, speed_value):
        """Set giá trị return speed."""
        print(f"⚡ AutoTune Return Speed - Setting value to: {speed_value}")
        
        success = self.return_speed_detector.set_auto_tune_value(speed_value)
        if success:
            self.current_return_speed = speed_value
            print(f"✅ Return Speed set to {speed_value} successfully")
        else:
            print(f"❌ Failed to set Return Speed to {speed_value}")
        return success
    
    # ==================== FLEX TUNE METHODS ====================
    
    def set_flex_tune_value(self, flex_value):
        """Set giá trị flex tune.""" 
        print(f"🎵 AutoTune Flex Tune - Setting value to: {flex_value}")
        
        success = self.flex_tune_detector.set_auto_tune_value(flex_value)
        if success:
            self.current_flex_tune = flex_value
            print(f"✅ Flex Tune set to {flex_value} successfully")
        else:
            print(f"❌ Failed to set Flex Tune to {flex_value}")
        return success
    
    # ==================== NATURAL VIBRATO METHODS ====================
    
    def set_natural_vibrato_value(self, vibrato_value):
        """Set giá trị natural vibrato."""
        print(f"🌊 AutoTune Natural Vibrato - Setting value to: {vibrato_value}")
        
        success = self.natural_vibrato_detector.set_auto_tune_value(vibrato_value)
        if success:
            self.current_natural_vibrato = vibrato_value
            print(f"✅ Natural Vibrato set to {vibrato_value} successfully")
        else:
            print(f"❌ Failed to set Natural Vibrato to {vibrato_value}")
        return success
    
    # ==================== HUMANIZE METHODS ====================
    
    def set_humanize_value(self, humanize_value):
        """Set giá trị humanize."""
        print(f"🤖 AutoTune Humanize - Setting value to: {humanize_value}")
        
        success = self.humanize_detector.set_auto_tune_value(humanize_value)
        if success:
            self.current_humanize = humanize_value
            print(f"✅ Humanize set to {humanize_value} successfully")
        else:
            print(f"❌ Failed to set Humanize to {humanize_value}")
        return success
    
    # ==================== UTILITY METHODS ====================
    
    def get_current_values(self):
        """Lấy tất cả giá trị hiện tại."""
        return {
            'return_speed': self.current_return_speed,
            'flex_tune': self.current_flex_tune,
            'natural_vibrato': self.current_natural_vibrato,
            'humanize': self.current_humanize
        }
    
    def reset_to_defaults(self):
        """Reset tất cả về giá trị mặc định."""
        results = {}
        
        # Reset Return Speed
        default_return_speed = self.default_values.get('return_speed_default', 5)
        results['return_speed'] = self.set_return_speed_value(default_return_speed)
        
        # Reset Flex Tune
        default_flex_tune = self.default_values.get('flex_tune_default', 5)
        results['flex_tune'] = self.set_flex_tune_value(default_flex_tune)
        
        # Reset Natural Vibrato
        default_natural_vibrato = self.default_values.get('natural_vibrato_default', 5)
        results['natural_vibrato'] = self.set_natural_vibrato_value(default_natural_vibrato)
        
        # Reset Humanize
        default_humanize = self.default_values.get('humanize_default', 5)
        results['humanize'] = self.set_humanize_value(default_humanize)
        
        success_count = sum(1 for success in results.values() if success)
        print(f"✅ Reset completed: {success_count}/4 controls successful")
        
        return all(results.values())
    
    def execute(self):
        """Execute AutoTune controls detection."""
        # Test if any of the detectors can find AUTO-TUNE PRO
        return (self.return_speed_detector.execute() or 
                self.flex_tune_detector.execute() or
                self.natural_vibrato_detector.execute() or
                self.humanize_detector.execute())
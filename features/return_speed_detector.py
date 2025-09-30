from features.auto_tune_detector import AutoTuneDetector


class ReturnSpeedDetector(AutoTuneDetector):
    """Tính năng Return Speed adjustment với AUTO-TUNE PRO plugin."""

    def __init__(self):
        super().__init__(
            feature_name="Return Speed",
            template_filename="return_speed_template.png",
            config_prefix="return_speed"
        )
    
    def set_return_speed_value(self, speed_value):
        """Set giá trị return speed - wrapper cho compatibility."""
        return self.set_auto_tune_value(speed_value)
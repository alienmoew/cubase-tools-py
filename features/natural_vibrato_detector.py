from features.auto_tune_detector import AutoTuneDetector


class NaturalVibratoDetector(AutoTuneDetector):
    """Tính năng Natural Vibrato adjustment với AUTO-TUNE PRO plugin."""

    def __init__(self):
        super().__init__(
            feature_name="Natural Vibrato",
            template_filename="natural_vibrato_template.png",
            config_prefix="natural_vibrato"
        )
    
    def set_natural_vibrato_value(self, vibrato_value):
        """Set giá trị natural vibrato - wrapper cho compatibility."""
        return self.set_auto_tune_value(vibrato_value)
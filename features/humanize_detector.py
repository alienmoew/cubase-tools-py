from features.auto_tune_detector import AutoTuneDetector


class HumanizeDetector(AutoTuneDetector):
    """Tính năng Humanize adjustment với AUTO-TUNE PRO plugin."""

    def __init__(self):
        super().__init__(
            feature_name="Humanize",
            template_filename="humanize_template.png",
            config_prefix="humanize"
        )
    
    def set_humanize_value(self, humanize_value):
        """Set giá trị humanize - wrapper cho compatibility."""
        return self.set_auto_tune_value(humanize_value)
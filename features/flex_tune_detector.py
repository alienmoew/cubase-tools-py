from features.auto_tune_detector import AutoTuneDetector


class FlexTuneDetector(AutoTuneDetector):
    """Tính năng Flex Tune adjustment với AUTO-TUNE PRO plugin."""

    def __init__(self):
        super().__init__(
            feature_name="Flex Tune",
            template_filename="flex_tune_template.png",
            config_prefix="flex_tune"
        )
    
    def set_flex_tune_value(self, flex_value):
        """Set giá trị flex tune - wrapper cho compatibility."""
        return self.set_auto_tune_value(flex_value)
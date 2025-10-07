"""
Music Presets Manager - Quản lý template nhạc Bolero và Nhạc trẻ
"""
import os
import config
from .external_config_manager import ExternalConfigManager

class MusicPresetsManager:
    """Class quản lý presets cho nhạc Bolero và Nhạc trẻ."""
    
    def __init__(self):
        # Create default music presets content
        default_presets_content = """# Music Presets Configuration
# Format: music_type:level:return_speed:flex_tune:natural_vibrato:humanize
# Levels: -2, -1, 0, +1, +2

# Bolero presets
bolero:-2:30:20:15:25
bolero:-1:35:25:20:30
bolero:0:40:30:25:35
bolero:+1:45:35:30:40
bolero:+2:50:40:35:45

# Nhạc trẻ presets  
nhac_tre:-2:25:15:10:20
nhac_tre:-1:30:20:15:25
nhac_tre:0:35:25:20:30
nhac_tre:+1:40:30:25:35
nhac_tre:+2:45:35:30:40"""

        # Ensure external config file exists
        self.presets_file = ExternalConfigManager.ensure_external_config_exists(
            "music_presets.txt",
            default_presets_content
        )
        
        self.presets = {}
        self.current_levels = {
            'bolero': 0,      # Mức hiện tại: -2, -1, 0, +1, +2
            'nhac_tre': 0
        }
        self.load_presets()
    
    def load_presets(self):
        """Load presets từ file."""
        try:
            if not os.path.exists(self.presets_file):
                print(f"❌ Không tìm thấy file preset: {self.presets_file}")
                return False
            
            with open(self.presets_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                # Skip comments và dòng trống
                if line.startswith('#') or not line:
                    continue
                
                try:
                    # Format: music_type:level:return_speed:flex_tune:natural_vibrato:humanize
                    parts = line.split(':')
                    if len(parts) != 6:
                        continue
                    
                    music_type, level, return_speed, flex_tune, natural_vibrato, humanize = parts
                    
                    if music_type not in self.presets:
                        self.presets[music_type] = {}
                    
                    self.presets[music_type][level] = {
                        'return_speed': int(return_speed),
                        'flex_tune': int(flex_tune),
                        'natural_vibrato': int(natural_vibrato),
                        'humanize': int(humanize)
                    }
                    
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Lỗi parse dòng preset: {line} - {e}")
                    continue
            
            print(f"✅ Đã load {len(self.presets)} loại nhạc preset")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi load presets: {e}")
            return False
    
    def get_preset_values(self, music_type, level):
        """Lấy giá trị preset cho loại nhạc và mức độ cụ thể."""
        try:
            if music_type in self.presets and level in self.presets[music_type]:
                return self.presets[music_type][level]
            else:
                print(f"❌ Không tìm thấy preset cho {music_type}:{level}")
                return None
        except Exception as e:
            print(f"❌ Lỗi get preset: {e}")
            return None
    
    def increase_level(self, music_type):
        """Tăng mức độ của loại nhạc (+1, max là +2)."""
        if music_type not in self.current_levels:
            return False
        
        current = self.current_levels[music_type]
        if current < 2:  # Max là +2
            self.current_levels[music_type] = current + 1
            return True
        return False
    
    def decrease_level(self, music_type):
        """Giảm mức độ của loại nhạc (-1, min là -2)."""
        if music_type not in self.current_levels:
            return False
        
        current = self.current_levels[music_type]
        if current > -2:  # Min là -2
            self.current_levels[music_type] = current - 1
            return True
        return False
    
    def get_current_level(self, music_type):
        """Lấy mức độ hiện tại của loại nhạc."""
        return self.current_levels.get(music_type, 0)
    
    def get_level_string(self, level):
        """Convert level number thành string format."""
        if level > 0:
            return f"+{level}"
        elif level < 0:
            return str(level)
        else:
            return "0"
    
    def get_level_description(self, level):
        """Lấy mô tả cho mức độ."""
        descriptions = {
            2: "Cực mạnh",
            1: "Mạnh", 
            0: "Bình thường",
            -1: "Nhẹ",
            -2: "Cực nhẹ"
        }
        return descriptions.get(level, "Không rõ")
    
    def apply_preset(self, music_type, gui_instance):
        """Áp dụng preset hiện tại cho loại nhạc vào GUI với ultra fast processing."""
        try:
            current_level = self.get_current_level(music_type)
            level_string = self.get_level_string(current_level)
            
            preset_values = self.get_preset_values(music_type, level_string)
            if not preset_values:
                print(f"❌ Không thể áp dụng preset {music_type}:{level_string}")
                return False
            
            # Prepare ultra fast batch parameters
            parameters_list = [
                {
                    'detector': gui_instance.autotune_controls_detector.return_speed_detector,
                    'value': preset_values['return_speed'],
                    'name': 'Return Speed'
                },
                {
                    'detector': gui_instance.autotune_controls_detector.flex_tune_detector,
                    'value': preset_values['flex_tune'],
                    'name': 'Flex Tune'
                },
                {
                    'detector': gui_instance.autotune_controls_detector.natural_vibrato_detector,
                    'value': preset_values['natural_vibrato'],
                    'name': 'Natural Vibrato'
                },
                {
                    'detector': gui_instance.autotune_controls_detector.humanize_detector,
                    'value': preset_values['humanize'],
                    'name': 'Humanize'
                }
            ]
            
            # Execute ultra fast batch
            from utils.ultra_fast_processor import UltraFastAutoTuneProcessor
            
            print(f"⚡ Ultra fast applying {music_type} preset level {level_string}...")
            
            ultra_processor = UltraFastAutoTuneProcessor()
            success_count, total_count = ultra_processor.execute_ultra_fast_batch(parameters_list)
            
            # Update UI sliders instantly
            try:
                gui_instance.return_speed_slider.set(preset_values['return_speed'])
                gui_instance._on_return_speed_slider_change(preset_values['return_speed'])
                
                gui_instance.flex_tune_slider.set(preset_values['flex_tune'])
                gui_instance._on_flex_tune_slider_change(preset_values['flex_tune'])
                
                gui_instance.natural_vibrato_slider.set(preset_values['natural_vibrato'])
                gui_instance._on_natural_vibrato_slider_change(preset_values['natural_vibrato'])
                
                gui_instance.humanize_slider.set(preset_values['humanize'])
                gui_instance._on_humanize_slider_change(preset_values['humanize'])
                
            except Exception as e:
                print(f"⚠️ UI update error: {e}")
            
            print(f"⚡ Ultra fast preset applied: {success_count}/{total_count} successful")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Lỗi apply preset: {e}")
            return False
    
    def get_music_types(self):
        """Lấy danh sách các loại nhạc có sẵn."""
        return list(self.presets.keys())
    
    def reset_all_levels(self):
        """Reset tất cả level về 0."""
        for music_type in self.current_levels:
            self.current_levels[music_type] = 0
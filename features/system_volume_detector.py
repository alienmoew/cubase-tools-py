"""
System Volume Detector - Điều chỉnh âm lượng của ứng dụng cụ thể (Chrome, etc.)
sử dụng Windows Audio Session API (pycaw).
"""
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume


class SystemVolumeDetector:
    """
    Detector để điều chỉnh âm lượng của ứng dụng cụ thể thông qua Windows Audio API.
    Thay thế cho việc điều chỉnh trong Cubase.
    """
    
    def __init__(self, app_name="chrome.exe"):
        """
        Initialize SystemVolumeDetector.
        
        Args:
            app_name: Tên process của ứng dụng cần điều khiển (vd: chrome.exe, msedge.exe, spotify.exe)
        """
        self.app_name = app_name
        print(f"🔊 System Volume Detector initialized for: {app_name}")
    
    def get_volume(self):
        """
        Lấy âm lượng hiện tại của ứng dụng.
        
        Returns:
            float: Giá trị âm lượng từ 0.0 đến 1.0, hoặc 0.0 nếu không tìm thấy
        """
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name().lower() == self.app_name.lower():
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    current_volume = volume.GetMasterVolume()
                    print(f"🔊 Current volume for {self.app_name}: {int(current_volume * 100)}%")
                    return current_volume
            
            print(f"⚠️ Application {self.app_name} not found in audio sessions")
            return 0.0
            
        except Exception as e:
            print(f"❌ Error getting volume: {e}")
            return 0.0
    
    def set_volume(self, value):
        """
        Đặt âm lượng cho ứng dụng.
        
        Args:
            value: Giá trị âm lượng từ 0.0 đến 1.0
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Clamp value to valid range
            value = max(0.0, min(1.0, float(value)))
            
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name().lower() == self.app_name.lower():
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMasterVolume(value, None)
                    print(f"✅ Set volume for {self.app_name} to {int(value * 100)}%")
                    return True
            
            print(f"❌ Application {self.app_name} not found in audio sessions")
            return False
            
        except Exception as e:
            print(f"❌ Error setting volume: {e}")
            return False
    
    def set_volume_percent(self, percent):
        """
        Đặt âm lượng theo phần trăm.
        
        Args:
            percent: Giá trị từ 0 đến 100
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        value = percent / 100.0
        return self.set_volume(value)
    
    def get_volume_percent(self):
        """
        Lấy âm lượng theo phần trăm.
        
        Returns:
            int: Giá trị từ 0 đến 100
        """
        return int(self.get_volume() * 100)
    
    def increase_volume(self, step_percent=5):
        """
        Tăng âm lượng.
        
        Args:
            step_percent: Bước tăng theo phần trăm (mặc định 5%)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        current = self.get_volume()
        new_volume = min(1.0, current + (step_percent / 100.0))
        return self.set_volume(new_volume)
    
    def decrease_volume(self, step_percent=5):
        """
        Giảm âm lượng.
        
        Args:
            step_percent: Bước giảm theo phần trăm (mặc định 5%)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        current = self.get_volume()
        new_volume = max(0.0, current - (step_percent / 100.0))
        return self.set_volume(new_volume)
    
    def toggle_mute(self):
        """
        Toggle mute/unmute.
        
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            current = self.get_volume()
            
            if current > 0.01:  # Currently audible
                # Mute (set to 0)
                success = self.set_volume(0.0)
                if success:
                    print(f"🔇 Muted {self.app_name}")
                return success
            else:
                # Unmute (restore to default or 50%)
                success = self.set_volume(0.5)
                if success:
                    print(f"🔊 Unmuted {self.app_name}")
                return success
                
        except Exception as e:
            print(f"❌ Error toggling mute: {e}")
            return False
    
    def is_muted(self):
        """
        Kiểm tra xem có đang mute không.
        
        Returns:
            bool: True nếu đang mute (volume = 0), False nếu không
        """
        return self.get_volume() < 0.01
    
    def get_app_name(self):
        """Lấy tên ứng dụng đang điều khiển."""
        return self.app_name
    
    def set_app_name(self, app_name):
        """
        Đổi ứng dụng cần điều khiển.
        
        Args:
            app_name: Tên process mới
        """
        self.app_name = app_name
        print(f"🔄 Switched to controlling: {app_name}")


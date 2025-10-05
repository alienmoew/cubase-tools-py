from abc import ABC, abstractmethod
import os
import config

class BaseFeature(ABC):
    """Base class cho tất cả các tính năng."""
    
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Tạo các thư mục cần thiết."""
        try:
            print(f"🔧 Ensuring directories...")
            print(f"   RESULT_DIR: {config.RESULT_DIR}")
            print(f"   DATA_DIR: {config.DATA_DIR}")
            
            os.makedirs(config.RESULT_DIR, exist_ok=True)
            os.makedirs(config.DATA_DIR, exist_ok=True)
            
            print(f"✅ Directories ensured successfully")
        except Exception as e:
            print(f"⚠️ Error ensuring directories: {e}")
    
    @abstractmethod
    def execute(self):
        """Thực thi tính năng chính."""
        pass
    
    @abstractmethod
    def get_name(self):
        """Trả về tên của tính năng."""
        pass
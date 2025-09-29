from abc import ABC, abstractmethod
import os
import config

class BaseFeature(ABC):
    """Base class cho tất cả các tính năng."""
    
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Tạo các thư mục cần thiết."""
        os.makedirs(config.RESULT_DIR, exist_ok=True)
        os.makedirs(config.DATA_DIR, exist_ok=True)
    
    @abstractmethod
    def execute(self):
        """Thực thi tính năng chính."""
        pass
    
    @abstractmethod
    def get_name(self):
        """Trả về tên của tính năng."""
        pass
"""
External Config Manager - Quản lý file config bên ngoài exe
"""
import os
import sys

class ExternalConfigManager:
    """Quản lý đường dẫn tới config files bên ngoài."""
    
    @staticmethod
    def get_external_config_path(filename):
        """
        Lấy đường dẫn tới config file bên ngoài exe.
        Khi chạy từ exe, sẽ tìm file trong cùng thư mục với exe.
        Khi development, sẽ tìm trong thư mục project.
        """
        if hasattr(sys, "_MEIPASS"):
            # Chạy từ PyInstaller exe
            # Tìm file trong cùng thư mục với exe
            exe_dir = os.path.dirname(sys.executable)
            config_path = os.path.join(exe_dir, "config", filename)
            
            # Nếu không có thư mục config, tìm trực tiếp trong thư mục exe
            if not os.path.exists(config_path):
                config_path = os.path.join(exe_dir, filename)
        else:
            # Development mode - tìm trong thư mục project
            project_dir = os.path.dirname(os.path.abspath(__file__))
            # Lùi về thư mục gốc (vì file này ở trong utils/)
            project_dir = os.path.dirname(project_dir)
            config_path = os.path.join(project_dir, filename)
        
        return config_path
    
    @staticmethod
    def ensure_external_config_exists(filename, default_content=None):
        """
        Đảm bảo config file tồn tại bên ngoài.
        Nếu không tồn tại, tạo file với nội dung mặc định.
        """
        config_path = ExternalConfigManager.get_external_config_path(filename)
        
        if not os.path.exists(config_path):
            # Tạo thư mục config nếu cần
            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                try:
                    os.makedirs(config_dir, exist_ok=True)
                except:
                    # Nếu không tạo được thư mục con, dùng thư mục exe
                    if hasattr(sys, "_MEIPASS"):
                        exe_dir = os.path.dirname(sys.executable)
                        config_path = os.path.join(exe_dir, filename)
            
            # Tạo file với nội dung mặc định
            if default_content is not None:
                try:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                    print(f"✅ Created external config: {config_path}")
                except Exception as e:
                    print(f"❌ Failed to create config file {config_path}: {e}")
        
        return config_path
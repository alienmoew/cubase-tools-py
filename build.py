#!/usr/bin/env python3
"""
Build script for Cubase Auto Tools
Tự động build exe và chuẩn bị config files bên ngoài
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

class CubaseToolsBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.dist_dir = self.project_dir / "dist"
        self.exe_name = "CubaseAutoTools.exe"
        self.config_files = [
            "settings.json",
            "default_values.txt", 
            "music_presets.txt"
        ]
        
    def clean_build_dirs(self):
        """Xóa các thư mục build cũ"""
        print("🧹 Cleaning old build directories...")
        
        dirs_to_clean = ["build", "dist", "__pycache__"]
        for dir_name in dirs_to_clean:
            dir_path = self.project_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
    
    def check_tesseract(self):
        """Kiểm tra Tesseract OCR installation"""
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tesseract_path):
            print("✅ Tesseract OCR found - will be included in build")
            return True
        else:
            print("⚠️  Tesseract OCR not found - OCR features may not work")
            print("   Install from: https://github.com/UB-Mannheim/tesseract/wiki")
            return False

    def build_exe(self):
        """Build exe bằng PyInstaller"""
        print("🔨 Building executable with PyInstaller...")
        
        # Check tesseract
        self.check_tesseract()
        
        spec_file = self.project_dir / "cubase_tools.spec"
        if not spec_file.exists():
            print("❌ Spec file not found! Please create cubase_tools.spec first.")
            return False
            
        # Run PyInstaller
        cmd = ["pyinstaller", "--clean", str(spec_file)]
        try:
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ PyInstaller build failed:")
                print(result.stderr)
                return False
            else:
                print("✅ PyInstaller build successful!")
                return True
        except Exception as e:
            print(f"❌ Error running PyInstaller: {e}")
            return False
    
    def create_default_config_files(self):
        """Tạo các file config mặc định"""
        print("📝 Creating default config files...")
        
        config_templates = {
            "settings.json": """{
  "theme": "dark",
  "auto_detect": false
}""",
            
            "default_values.txt": """# Default Values Configuration
# Format: key=value

# Volume settings
default_volume=75
min_volume=0
max_volume=100

# Auto-tune settings  
default_return_speed=40
default_flex_tune=30
default_natural_vibrato=25
default_humanize=35

# Transpose settings
default_transpose=0
min_transpose=-12
max_transpose=12

# Timing settings
detection_delay=0.5
processing_timeout=10""",

            "music_presets.txt": """# Music Presets Configuration
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
        }
        
        return config_templates
    
    def prepare_config_directory(self):
        """Chuẩn bị thư mục config bên ngoài exe"""
        print("📁 Preparing external config directory...")
        
        exe_path = self.dist_dir / self.exe_name
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            return False
            
        # Tạo thư mục config
        config_dir = self.dist_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Copy hoặc tạo các file config
        config_templates = self.create_default_config_files()
        
        for config_file in self.config_files:
            source_path = self.project_dir / config_file
            target_path = config_dir / config_file
            
            if source_path.exists():
                # Copy existing config file
                shutil.copy2(source_path, target_path)
                print(f"   Copied: {config_file}")
            else:
                # Create default config file
                if config_file in config_templates:
                    target_path.write_text(config_templates[config_file], encoding='utf-8')
                    print(f"   Created: {config_file} (default)")
                else:
                    print(f"   ⚠️  Skipped: {config_file} (no template)")
        
        return True
    
    def copy_required_directories(self):
        """Copy các thư mục cần thiết"""
        print("📂 Copying required directories...")
        
        dirs_to_copy = ["templates", "result"]
        
        for dir_name in dirs_to_copy:
            source_dir = self.project_dir / dir_name
            target_dir = self.dist_dir / dir_name
            
            if source_dir.exists():
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(source_dir, target_dir)
                print(f"   Copied: {dir_name}")
            else:
                print(f"   ⚠️  Not found: {dir_name}")
    
    def create_readme(self):
        """Tạo file README cho người dùng"""
        print("📄 Creating user README...")
        
        readme_content = """# Cubase Auto Tools

## Cách sử dụng:
1. Chạy file CubaseAutoTools.exe
2. Các file cấu hình nằm trong thư mục config/:
   - settings.json: Cài đặt giao diện và chế độ tự động
   - default_values.txt: Giá trị mặc định cho các control
   - music_presets.txt: Template cho nhạc Bolero và Nhạc trẻ

## Chỉnh sửa cấu hình:
- Bạn có thể edit các file trong thư mục config/ để tùy chỉnh
- Khởi động lại ứng dụng sau khi chỉnh sửa

## Yêu cầu hệ thống:
- Windows 10 trở lên
- Tesseract OCR đã cài đặt (nếu sử dụng tính năng OCR)
- Cubase phải được mở và có plugin AUTO-TUNE PRO

## Liên hệ hỗ trợ:
- Studio: KT STUDIO  
- Phone: 0948999892
"""
        
        readme_path = self.dist_dir / "README.txt"
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"   Created: README.txt")
    
    def build_all(self):
        """Build toàn bộ project"""
        print("🚀 Starting Cubase Auto Tools build process...\n")
        
        try:
            # Step 1: Clean
            self.clean_build_dirs()
            print()
            
            # Step 2: Build exe
            if not self.build_exe():
                return False
            print()
            
            # Step 3: Prepare config
            if not self.prepare_config_directory():
                return False
            print()
            
            # Step 4: Copy directories
            self.copy_required_directories()
            print()
            
            # Step 5: Create README
            self.create_readme()
            print()
            
            print("✅ Build completed successfully!")
            print(f"📁 Output directory: {self.dist_dir}")
            print(f"🚀 Executable: {self.dist_dir / self.exe_name}")
            print(f"⚙️  Config files: {self.dist_dir / 'config'}")
            print(f"\n🎉 Ready to distribute!")
            
            return True
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False

def main():
    """Main build function"""
    builder = CubaseToolsBuilder()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clean-only":
        builder.clean_build_dirs()
        return
    
    success = builder.build_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
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
        self.exe_name = "Auto Tools - KT Studio.exe"
        self.config_files = [
            "settings.json",
            "default_values.txt",
            "music_presets.txt"
        ]

    def clean_build_dirs(self):
        """Xóa các thư mục build cũ"""
        print("🧹 Cleaning old build directories...")
        for dir_name in ["build", "dist", "__pycache__"]:
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
        print("⚠️  Tesseract OCR not found - OCR features may not work")
        print("   Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

    def build_exe(self):
        """Build exe bằng PyInstaller"""
        print("🔨 Building executable with PyInstaller...")
        self.check_tesseract()

        spec_file = self.project_dir / "cubase_tools.spec"
        if not spec_file.exists():
            print("❌ Spec file not found! Please create cubase_tools.spec first.")
            return False

        cmd = ["pyinstaller", "--clean", str(spec_file)]
        try:
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ PyInstaller build failed:")
                print(result.stderr)
                return False
            print("✅ PyInstaller build successful!")
            return True
        except Exception as e:
            print(f"❌ Error running PyInstaller: {e}")
            return False

    def prepare_config_directory(self):
        """Copy các file config có sẵn từ project"""
        print("📁 Preparing external config directory...")
        exe_path = self.dist_dir / self.exe_name
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            return False

        config_dir = self.dist_dir / "config"
        config_dir.mkdir(exist_ok=True)

        for config_file in self.config_files:
            source_path = self.project_dir / config_file
            target_path = config_dir / config_file
            if source_path.exists():
                shutil.copy2(source_path, target_path)
                print(f"   ✅ Copied: {config_file}")
            else:
                print(f"   ⚠️  Not found: {config_file}")
        return True

    def copy_required_directories(self):
        """Copy các thư mục cần thiết"""
        print("📂 Copying required directories...")
        for dir_name in ["templates", "result"]:
            source_dir = self.project_dir / dir_name
            target_dir = self.dist_dir / dir_name
            if source_dir.exists():
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(source_dir, target_dir)
                print(f"   ✅ Copied: {dir_name}")
            else:
                print(f"   ⚠️  Not found: {dir_name}")

    def build_all(self):
        """Build toàn bộ project"""
        print("🚀 Starting Cubase Auto Tools build process...\n")
        try:
            self.clean_build_dirs()
            print()
            if not self.build_exe():
                return False
            print()
            if not self.prepare_config_directory():
                return False
            print()
            self.copy_required_directories()
            print()
            print("✅ Build completed successfully!")
            print(f"📁 Output directory: {self.dist_dir}")
            print(f"🚀 Executable: {self.dist_dir / self.exe_name}")
            print(f"⚙️  Config files: {self.dist_dir / 'config'}")
            print("\n🎉 Ready to distribute!")
            return True
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False

def main():
    builder = CubaseToolsBuilder()
    if len(sys.argv) > 1 and sys.argv[1] == "--clean-only":
        builder.clean_build_dirs()
        return
    success = builder.build_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

@echo off
echo ========================================
echo   CUBASE AUTO TOOLS - PACKAGE CREATOR
echo ========================================
echo.

:: Check if dist directory exists
if not exist "dist\Auto Tools - KT Studio.exe" (
    echo ❌ Executable not found! Please run build.bat first.
    pause
    exit /b 1
)

:: Create package directory
set "PACKAGE_NAME=final\Auto Tools - KT Studio"
set "PACKAGE_DIR=%PACKAGE_NAME%"

if exist "%PACKAGE_DIR%" (
    echo 🧹 Cleaning old package directory...
    rmdir /s /q "%PACKAGE_DIR%"
)

echo 📦 Creating package directory: %PACKAGE_DIR%
mkdir "%PACKAGE_DIR%"

:: Copy exe and required files
echo 📋 Copying files...
copy "dist\Auto Tools - KT Studio.exe" "%PACKAGE_DIR%\"

:: Copy directories
echo 📂 Copying directories...
xcopy "dist\config" "%PACKAGE_DIR%\config\" /e /i /y
xcopy "dist\templates" "%PACKAGE_DIR%\templates\" /e /i /y

:: Create installation guide
echo 📄 Creating installation guide...
(
echo # CUBASE AUTO TOOLS - HƯỚNG DẪN CÀI ĐẶT
echo.
echo ## Cài đặt và sử dụng:
echo 1. Giải nén file này vào thư mục bất kỳ
echo 2. Chạy file CubaseAutoTools.exe
echo 3. Đảm bảo Cubase đang mở và có plugin
echo.
echo ## Tùy chỉnh cấu hình:
echo - Chỉnh sửa file trong thư mục config/ theo nhu cầu:
echo   * default_values.txt: Giá trị mặc định
echo   * music_presets.txt: Template cho nhạc Bolero và Nhạc trẻ
echo.
echo ## Yêu cầu hệ thống:
echo - Windows 10 trở lên
echo - .NET Framework 4.5 trở lên
echo - Tesseract OCR ^(tùy chọn cho tính năng OCR^)
echo.
echo ## Liên hệ hỗ trợ:
echo - Studio: KT STUDIO
echo - Phone: 0948999892
echo.
echo ## Lưu ý:
echo - Đây là phiên bản portable, không cần cài đặt
echo - Có thể chạy từ USB hoặc thư mục bất kỳ
echo - Config files sẽ được lưu cùng thư mục ứng dụng
) > "%PACKAGE_DIR%\HUONG_DAN_SU_DUNG.txt"

:: Create zip package
echo 📦 Creating ZIP package...
powershell -command "Compress-Archive -Path '%PACKAGE_DIR%' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

if exist "%PACKAGE_NAME%.zip" (
    echo ✅ Package created successfully!
    echo 📁 Portable folder: %PACKAGE_DIR%
    echo 📦 ZIP package: %PACKAGE_NAME%.zip
    echo.
    echo 🎉 Ready to distribute!
) else (
    echo ❌ Failed to create ZIP package
)

echo.
pause
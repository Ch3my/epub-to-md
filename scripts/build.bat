@echo off
REM Build script for creating executables from Python files (Windows)
REM Run this script from the scripts folder or project root

echo ==========================================
echo EPUB to Markdown Converter - Build Script
echo ==========================================
echo.

REM Navigate to project root (works whether run from scripts/ or root)
cd /d "%~dp0\.."

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install -r requirements.txt
    echo.
)

REM Determine how to run PyInstaller (direct command or via python -m)
set PYINSTALLER_CMD=

where pyinstaller >nul 2>&1
if not errorlevel 1 (
    set PYINSTALLER_CMD=pyinstaller
    echo Using: pyinstaller
    goto :build
)

python -m PyInstaller --version >nul 2>&1
if not errorlevel 1 (
    set PYINSTALLER_CMD=python -m PyInstaller
    echo Using: python -m PyInstaller
    goto :build
)

echo ERROR: PyInstaller is not available.
echo Please ensure PyInstaller is installed correctly:
echo   pip install pyinstaller
echo.
pause
exit /b 1

:build
echo.

echo Building GUI executable...
%PYINSTALLER_CMD% --onefile ^
    --windowed ^
    --name "EPUB_to_MD_GUI" ^
    --add-data "src\epub_to_md\assets\app_icon.ico;epub_to_md\assets" ^
    --add-data "src\epub_to_md\assets\app_icon.png;epub_to_md\assets" ^
    --add-data "src\epub_to_md\core;epub_to_md\core" ^
    --icon=src\epub_to_md\assets\app_icon.ico ^
    --paths=src ^
    src\epub_to_md\gui\main.py

echo.
echo Building CLI executable...
%PYINSTALLER_CMD% --onefile ^
    --name "epub_to_md" ^
    --add-data "src\epub_to_md\core;epub_to_md\core" ^
    --icon=src\epub_to_md\assets\app_icon.ico ^
    --paths=src ^
    src\epub_to_md\cli\main.py

echo.
echo ==========================================
echo Build complete!
echo Executables are in the 'dist' folder:
echo   - EPUB_to_MD_GUI.exe (GUI version)
echo   - epub_to_md.exe (CLI version)
echo ==========================================
pause

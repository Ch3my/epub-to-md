@echo off
REM Build script for creating executables from Python files (Windows)

echo ==========================================
echo EPUB to Markdown Converter - Build Script
echo ==========================================
echo.

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
%PYINSTALLER_CMD% --onefile --windowed --name "EPUB_to_MD_GUI" --add-data "epub_converter.py;." --icon=NONE epub_to_md_gui.py

echo.
echo Building CLI executable...
%PYINSTALLER_CMD% --onefile --name "epub_to_md" --add-data "epub_converter.py;." --icon=NONE epub_to_md.py

echo.
echo ==========================================
echo Build complete!
echo Executables are in the 'dist' folder:
echo   - EPUB_to_MD_GUI.exe (GUI version)
echo   - epub_to_md.exe (CLI version)
echo ==========================================
pause

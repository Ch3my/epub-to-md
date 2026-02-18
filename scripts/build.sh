#!/bin/bash
# Build script for creating executables from Python files
# Run this script from the scripts folder or project root

echo "=========================================="
echo "EPUB to Markdown Converter - Build Script"
echo "=========================================="
echo ""

# Navigate to project root (works whether run from scripts/ or root)
cd "$(dirname "$0")/.."

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install -r requirements.txt
    echo ""
fi

# Determine how to run PyInstaller (direct command or via python -m)
PYINSTALLER_CMD=""
if command -v pyinstaller &>/dev/null; then
    PYINSTALLER_CMD="pyinstaller"
    echo "Using: pyinstaller"
elif python -m PyInstaller --version &>/dev/null; then
    PYINSTALLER_CMD="python -m PyInstaller"
    echo "Using: python -m PyInstaller"
else
    echo "ERROR: PyInstaller is not available."
    echo "Please ensure PyInstaller is installed correctly:"
    echo "  pip install pyinstaller"
    echo ""
    exit 1
fi
echo ""

echo "Building GUI executable..."
$PYINSTALLER_CMD --onefile \
    --windowed \
    --name "EPUB_to_MD_GUI" \
    --add-data "src/epub_to_md/assets/app_icon.ico:epub_to_md/assets" \
    --add-data "src/epub_to_md/assets/app_icon.png:epub_to_md/assets" \
    --add-data "src/epub_to_md/core:epub_to_md/core" \
    --icon=src/epub_to_md/assets/app_icon.ico \
    --paths=src \
    src/epub_to_md/gui/main.py

echo ""
echo "Building CLI executable..."
$PYINSTALLER_CMD --onefile \
    --name "epub_to_md" \
    --add-data "src/epub_to_md/core:epub_to_md/core" \
    --icon=src/epub_to_md/assets/app_icon.ico \
    --paths=src \
    src/epub_to_md/cli/main.py

echo ""
echo "=========================================="
echo "Build complete!"
echo "Executables are in the 'dist' folder:"
echo "  - EPUB_to_MD_GUI (GUI version)"
echo "  - epub_to_md (CLI version)"
echo "=========================================="

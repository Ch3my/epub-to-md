# EPUB to Markdown Converter

A Python tool to convert EPUB files to clean Markdown format. Available in both GUI and command-line versions.

## Features

- Converts EPUB e-books to Markdown
- **GUI version** - easy-to-use graphical interface
- **Batch processing** - convert multiple EPUBs at once
- Preserves heading hierarchy (H1-H6)
- Maintains formatting (bold, italic, code)
- Converts lists (ordered and unordered)
- Handles blockquotes and links
- Flexible output options (source folder or custom folder)
- No external dependencies (uses only Python standard library)

## Requirements

- Python 3.6 or higher
- No additional packages needed (uses standard library only)

## Files

The tool consists of three Python files:
- **`epub_converter.py`** - Core conversion module (shared by both versions)
- **`epub_to_md_gui.py`** - GUI version with Tkinter interface
- **`epub_to_md.py`** - Command-line version for scripting

Build files (optional, for creating executables):
- **`requirements.txt`** - Python dependencies (PyInstaller)
- **`build.sh`** - Build script for Linux/Mac
- **`build.bat`** - Build script for Windows

All Python files should be in the same directory.

**Note:** After running PyInstaller, you'll also see:
- `dist/` folder - Contains the final executables
- `build/` folder - Temporary build files (can be deleted)
- `.spec` files - PyInstaller configuration (can be deleted)

## Installation

### Option 1: Run directly with Python (No installation needed)

Simply download the scripts. No installation required!

For the GUI version:
```bash
# Make it executable (optional, Linux/Mac)
chmod +x epub_to_md_gui.py
```

For the command-line version:
```bash
# Make it executable (optional, Linux/Mac)
chmod +x epub_to_md.py
```

### Option 2: Build standalone executables

You can create standalone .exe files (Windows) or executables (Linux/Mac) that don't require Python to be installed.

#### Step 1: Install PyInstaller

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install pyinstaller
```

#### Step 2: Build the executables

**On Windows:**
```bash
# Run the build script
build.bat
```

**On Linux/Mac:**
```bash
# Make build script executable
chmod +x build.sh

# Run the build script
./build.sh
```

**Or build manually:**

For GUI version:
```bash
# Windows
pyinstaller --onefile --windowed --name "EPUB_to_MD_GUI" --add-data "epub_converter.py;." epub_to_md_gui.py

# Linux/Mac
pyinstaller --onefile --windowed --name "EPUB_to_MD_GUI" --add-data "epub_converter.py:." epub_to_md_gui.py
```

For CLI version:
```bash
# Windows
pyinstaller --onefile --name "epub_to_md" --add-data "epub_converter.py;." epub_to_md.py

# Linux/Mac
pyinstaller --onefile --name "epub_to_md" --add-data "epub_converter.py:." epub_to_md.py
```

#### Step 3: Find your executables

After building, executables will be in the `dist/` folder:
- **Windows**: `EPUB_to_MD_GUI.exe` and `epub_to_md.exe`
- **Linux/Mac**: `EPUB_to_MD_GUI` and `epub_to_md`

You can distribute these executables to users who don't have Python installed!

## Usage

### GUI Version (Recommended for most users)

Simply run the GUI version:

```bash
python epub_to_md_gui.py
```

This will open a graphical interface where you can:
1. **Select Files**: Click "Select EPUB Files" to choose one or more EPUB files
2. **Choose Output**: 
   - Check "Save to source folder" to save .md files next to the original .epub files
   - Or uncheck it and select a custom output folder
3. **Convert**: Click "Convert Files" and watch the progress
4. **View Results**: Check the conversion log for details

The GUI shows real-time progress and provides a detailed log of the conversion process.

---

### Command-Line Version

### Convert a single file:

```bash
python epub_to_md.py book.epub
```

This will create `book.md` in the same directory.

### Convert a single file with custom output:

```bash
python epub_to_md.py book.epub -o output.md
```

or

```bash
python epub_to_md.py book.epub --output /path/to/output.md
```

### Convert ALL EPUB files in current folder:

```bash
python epub_to_md.py --all
```

This will convert all `.epub` files in the current directory to `.md` files with the same names.

### Convert all EPUBs in a specific folder:

```bash
python epub_to_md.py --all --folder /path/to/books
```

### Convert all EPUBs and save to a different folder:

```bash
python epub_to_md.py --all --output-folder ./markdown_books
```

### Examples:

```bash
# Convert a single book
python epub_to_md.py "My Book.epub"

# Convert and specify output location
python epub_to_md.py "My Book.epub" -o ~/Documents/book.md

# Convert all EPUBs in current directory
python epub_to_md.py --all

# Convert all EPUBs from Downloads folder
python epub_to_md.py --all --folder ~/Downloads

# Convert all EPUBs and organize in a markdown folder
python epub_to_md.py --all --output-folder ./converted_books

# Convert all EPUBs from one folder to another
python epub_to_md.py --all --folder ~/Books --output-folder ~/Markdown
```

## What gets converted

The script converts:
- ✓ Headings (# ## ### etc.)
- ✓ Paragraphs
- ✓ Bold and italic text
- ✓ Lists (bulleted and numbered)
- ✓ Code blocks and inline code
- ✓ Blockquotes
- ✓ Horizontal rules
- ✓ Line breaks

The script skips:
- Navigation files (TOC)
- Copyright pages
- Scripts and styles

## Output format

The script combines all chapters/sections into a single Markdown file, separated by horizontal rules (`---`).

## Troubleshooting

**"Invalid EPUB file" error:**
- Make sure the file is a valid EPUB (not corrupted)
- Try opening it in an e-reader first to verify

**Missing content:**
- Some EPUBs use complex formatting that may not convert perfectly
- The script focuses on text content and basic formatting

**Encoding issues:**
- The script uses UTF-8 encoding by default
- Most modern EPUBs should work fine

## License

Free to use and modify as needed.

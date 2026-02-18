#!/usr/bin/env python3
"""
EPUB to Markdown Converter - Command Line Version
Converts EPUB files to clean Markdown format
"""

import argparse
from pathlib import Path

# Import converter functions from shared module
from epub_to_md.core.converter import convert_epub_to_md




def convert_single_file(epub_path, output_path=None):
    """Convert a single EPUB file to Markdown (wrapper for CLI)"""

    # Generate output path if not provided
    if output_path is None:
        epub_file = Path(epub_path)
        output_path = epub_file.with_suffix('.md')

    print(f"Converting {epub_path} to Markdown...")

    # Use the shared converter function
    result_path, char_count = convert_epub_to_md(epub_path, str(output_path))

    print(f"✓ Conversion complete: {result_path}")
    print(f"  Output size: {char_count:,} characters")

    return result_path


def convert_all_epubs_in_folder(folder_path='.', output_folder=None):
    """Convert all EPUB files in a folder"""

    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    # Find all EPUB files
    epub_files = list(folder.glob('*.epub'))

    if not epub_files:
        print(f"No EPUB files found in {folder_path}")
        return []

    print(f"Found {len(epub_files)} EPUB file(s) in {folder_path}")
    print()

    converted_files = []
    failed_files = []

    for i, epub_file in enumerate(epub_files, 1):
        print(f"[{i}/{len(epub_files)}] Processing: {epub_file.name}")

        try:
            # Determine output path
            if output_folder:
                output_dir = Path(output_folder)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / epub_file.with_suffix('.md').name
            else:
                output_path = epub_file.with_suffix('.md')

            # Use the shared converter function
            result_path, char_count = convert_epub_to_md(str(epub_file), str(output_path))
            print(f"✓ Conversion complete: {result_path}")
            print(f"  Output size: {char_count:,} characters")

            converted_files.append(str(result_path))
            print()

        except Exception as e:
            print(f"✗ Failed to convert {epub_file.name}: {e}")
            failed_files.append(epub_file.name)
            print()

    # Summary
    print("=" * 60)
    print(f"Conversion Summary:")
    print(f"  Successfully converted: {len(converted_files)}")
    print(f"  Failed: {len(failed_files)}")

    if failed_files:
        print(f"\nFailed files:")
        for file in failed_files:
            print(f"  - {file}")

    return converted_files


def main():
    parser = argparse.ArgumentParser(
        description='Convert EPUB files to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Convert a single file
  python -m epub_to_md.cli.main book.epub

  # Convert with custom output
  python -m epub_to_md.cli.main book.epub -o output.md

  # Convert all EPUBs in current folder
  python -m epub_to_md.cli.main --all

  # Convert all EPUBs in specific folder
  python -m epub_to_md.cli.main --all --folder /path/to/books

  # Convert all EPUBs and save to output folder
  python -m epub_to_md.cli.main --all --output-folder ./markdown_books
        '''
    )

    parser.add_argument('epub_file', nargs='?', help='Path to the EPUB file')
    parser.add_argument('-o', '--output', help='Output Markdown file path (optional)')
    parser.add_argument('--all', action='store_true',
                       help='Convert all EPUB files in the current (or specified) folder')
    parser.add_argument('--folder', default='.',
                       help='Folder to search for EPUB files (used with --all)')
    parser.add_argument('--output-folder',
                       help='Output folder for converted files (used with --all)')

    args = parser.parse_args()

    try:
        if args.all:
            # Batch conversion mode
            convert_all_epubs_in_folder(args.folder, args.output_folder)
        else:
            # Single file conversion mode
            if not args.epub_file:
                parser.error("epub_file is required when not using --all")
            convert_single_file(args.epub_file, args.output)

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())

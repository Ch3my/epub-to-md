"""EPUB to Markdown Converter - Convert EPUB files to clean Markdown format."""

__version__ = "0.1.0"

from epub_to_md.core.converter import convert_epub_to_md, extract_text_from_epub

__all__ = ["convert_epub_to_md", "extract_text_from_epub", "__version__"]

"""Core conversion module for EPUB to Markdown."""

from epub_to_md.core.converter import (
    HTMLToMarkdown,
    convert_epub_to_md,
    extract_text_from_epub,
)

__all__ = ["HTMLToMarkdown", "convert_epub_to_md", "extract_text_from_epub"]

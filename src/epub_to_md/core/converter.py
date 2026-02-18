"""
EPUB to Markdown Converter - Core Module
Shared functions for converting EPUB files to Markdown format
"""

import os
import re
from pathlib import Path
import zipfile
from html.parser import HTMLParser
from io import StringIO


class HTMLToMarkdown(HTMLParser):
    """Convert HTML to Markdown"""

    def __init__(self):
        super().__init__()
        self.output = StringIO()
        self.current_tag = []
        self.list_level = 0
        self.list_item_count = []
        self.in_pre = False
        self.in_code = False
        self.skip_content = False

    def handle_starttag(self, tag, attrs):
        self.current_tag.append(tag)

        # Skip script and style tags
        if tag in ['script', 'style']:
            self.skip_content = True
            return

        if tag == 'h1':
            self.output.write('\n# ')
        elif tag == 'h2':
            self.output.write('\n## ')
        elif tag == 'h3':
            self.output.write('\n### ')
        elif tag == 'h4':
            self.output.write('\n#### ')
        elif tag == 'h5':
            self.output.write('\n##### ')
        elif tag == 'h6':
            self.output.write('\n###### ')
        elif tag == 'p':
            self.output.write('\n\n')
        elif tag == 'br':
            self.output.write('  \n')
        elif tag == 'hr':
            self.output.write('\n\n---\n\n')
        elif tag == 'strong' or tag == 'b':
            self.output.write('**')
        elif tag == 'em' or tag == 'i':
            self.output.write('*')
        elif tag == 'code':
            self.in_code = True
            self.output.write('`')
        elif tag == 'pre':
            self.in_pre = True
            self.output.write('\n\n```\n')
        elif tag == 'ul':
            self.list_level += 1
            self.list_item_count.append(0)
            self.output.write('\n')
        elif tag == 'ol':
            self.list_level += 1
            self.list_item_count.append(1)
            self.output.write('\n')
        elif tag == 'li':
            indent = '  ' * (self.list_level - 1)
            if self.list_item_count[-1] == 0:
                self.output.write(f'{indent}- ')
            else:
                self.output.write(f'{indent}{self.list_item_count[-1]}. ')
                self.list_item_count[-1] += 1
        elif tag == 'blockquote':
            self.output.write('\n> ')
        elif tag == 'a':
            # We'll add the link URL in handle_endtag
            pass

    def handle_endtag(self, tag):
        if self.current_tag and self.current_tag[-1] == tag:
            self.current_tag.pop()

        if tag in ['script', 'style']:
            self.skip_content = False
            return

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.output.write('\n')
        elif tag == 'p':
            self.output.write('\n')
        elif tag == 'strong' or tag == 'b':
            self.output.write('**')
        elif tag == 'em' or tag == 'i':
            self.output.write('*')
        elif tag == 'code':
            self.in_code = False
            self.output.write('`')
        elif tag == 'pre':
            self.in_pre = False
            self.output.write('\n```\n\n')
        elif tag in ['ul', 'ol']:
            self.list_level -= 1
            self.list_item_count.pop()
            self.output.write('\n')
        elif tag == 'li':
            self.output.write('\n')

    def handle_data(self, data):
        if self.skip_content:
            return

        # Clean up whitespace unless in pre/code
        if not self.in_pre and not self.in_code:
            data = re.sub(r'\s+', ' ', data)

        self.output.write(data)

    def get_markdown(self):
        result = self.output.getvalue()
        # Clean up excessive newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()


def extract_text_from_epub(epub_path):
    """Extract and convert text from EPUB file"""

    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    markdown_content = []

    try:
        with zipfile.ZipFile(epub_path, 'r') as epub:
            # Get list of HTML/XHTML files
            html_files = [f for f in epub.namelist()
                         if f.endswith(('.html', '.xhtml', '.htm'))]

            # Sort to maintain reading order
            html_files.sort()

            for html_file in html_files:
                # Skip navigation and metadata files
                if any(skip in html_file.lower() for skip in ['nav', 'toc', 'copyright']):
                    continue

                try:
                    content = epub.read(html_file).decode('utf-8')

                    # Convert HTML to Markdown
                    parser = HTMLToMarkdown()
                    parser.feed(content)
                    md_text = parser.get_markdown()

                    if md_text.strip():
                        markdown_content.append(md_text)

                except Exception as e:
                    print(f"Warning: Could not process {html_file}: {e}")
                    continue

    except zipfile.BadZipFile:
        raise ValueError(f"Invalid EPUB file: {epub_path}")

    return '\n\n---\n\n'.join(markdown_content)


def convert_epub_to_md(epub_path, output_path):
    """Convert EPUB file to Markdown

    Args:
        epub_path: Path to the EPUB file
        output_path: Path where the Markdown file will be saved

    Returns:
        tuple: (output_path, character_count)
    """
    # Extract and convert content
    markdown_content = extract_text_from_epub(epub_path)

    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return output_path, len(markdown_content)

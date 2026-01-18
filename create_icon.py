"""Generate app icon for EPUB to Markdown converter"""
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # Create icons at multiple sizes
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        # Create image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Colors
        bg_color = (99, 102, 241)  # Purple/indigo accent
        book_color = (255, 255, 255)  # White
        arrow_color = (16, 185, 129)  # Green accent

        # Draw rounded rectangle background
        padding = size // 8
        radius = size // 5
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=radius,
            fill=bg_color
        )

        # Draw a simple book icon (left side)
        book_left = size * 0.2
        book_top = size * 0.28
        book_width = size * 0.25
        book_height = size * 0.44

        # Book spine and pages
        draw.rectangle(
            [book_left, book_top, book_left + book_width, book_top + book_height],
            fill=book_color
        )
        # Book spine line
        spine_x = book_left + book_width * 0.2
        draw.line(
            [(spine_x, book_top), (spine_x, book_top + book_height)],
            fill=bg_color,
            width=max(1, size // 32)
        )

        # Draw arrow in the middle
        arrow_start_x = size * 0.48
        arrow_end_x = size * 0.62
        arrow_y = size * 0.5
        arrow_size = size * 0.08
        line_width = max(2, size // 20)

        # Arrow line
        draw.line(
            [(arrow_start_x, arrow_y), (arrow_end_x, arrow_y)],
            fill=arrow_color,
            width=line_width
        )
        # Arrow head
        draw.polygon([
            (arrow_end_x + arrow_size, arrow_y),
            (arrow_end_x - arrow_size * 0.3, arrow_y - arrow_size),
            (arrow_end_x - arrow_size * 0.3, arrow_y + arrow_size)
        ], fill=arrow_color)

        # Draw MD text (right side)
        md_x = size * 0.68
        md_y = size * 0.35
        md_size = size * 0.3

        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", int(md_size * 0.5))
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(md_size * 0.5))
            except:
                font = ImageFont.load_default()

        draw.text((md_x, md_y), "MD", fill=book_color, font=font)

        images.append(img)

    # Save as ICO with multiple sizes
    images[0].save(
        'c:/Github/epub-to-md/app_icon.ico',
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )

    # Also save a PNG version
    images[-1].save('c:/Github/epub-to-md/app_icon.png', format='PNG')

    print("Icon created: app_icon.ico and app_icon.png")

if __name__ == '__main__':
    create_icon()

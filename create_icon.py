"""
MovieFlix Icon Generator
========================

Creates a custom red "M" icon similar to Netflix style.
Generates .ico file for desktop shortcut.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_movieflix_icon():
    """Create a professional red M icon for MovieFlix."""
    
    # Create image with solid background (not transparent)
    size = 256
    dark_bg = (20, 20, 20, 255)
    image = Image.new('RGB', (size, size), dark_bg[:3])
    draw = ImageDraw.Draw(image)
    
    # Netflix-style red
    netflix_red = (229, 9, 20)
    
    # Draw the "M" letter with better proportions
    # M is made of 4 shapes
    
    # Calculate M dimensions
    m_width = 160
    m_height = 140
    m_x = (size - m_width) // 2
    m_y = (size - m_height) // 2 + 10
    
    bar_width = 25
    
    # Left vertical bar of M
    m_left = [
        (m_x, m_y),
        (m_x + bar_width, m_y),
        (m_x + bar_width, m_y + m_height),
        (m_x, m_y + m_height)
    ]
    draw.polygon(m_left, fill=netflix_red)
    
    # Left diagonal of M (going down-right to center)
    m_diag_left = [
        (m_x + bar_width, m_y),
        (m_x + bar_width + 20, m_y),
        (m_x + m_width // 2 + 10, m_y + m_height // 2),
        (m_x + m_width // 2 - 10, m_y + m_height // 2)
    ]
    draw.polygon(m_diag_left, fill=netflix_red)
    
    # Right diagonal of M (going up-right from center)
    m_diag_right = [
        (m_x + m_width // 2 - 10, m_y + m_height // 2),
        (m_x + m_width // 2 + 10, m_y + m_height // 2),
        (m_x + m_width - bar_width - 20, m_y),
        (m_x + m_width - bar_width, m_y)
    ]
    draw.polygon(m_diag_right, fill=netflix_red)
    
    # Right vertical bar of M
    m_right = [
        (m_x + m_width - bar_width, m_y),
        (m_x + m_width, m_y),
        (m_x + m_width, m_y + m_height),
        (m_x + m_width - bar_width, m_y + m_height)
    ]
    draw.polygon(m_right, fill=netflix_red)
    
    # Save as ICO file with multiple sizes
    icon_path = os.path.join(os.path.dirname(__file__), 'MovieFlix.ico')
    
    # Create multiple sizes for Windows
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []
    
    for size_tuple in sizes:
        resized = image.resize(size_tuple, Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Save as ICO
    image.save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    print(f"✓ Icon created: {icon_path}")
    return icon_path


def create_simple_text_icon():
    """Create a simpler text-based icon if font issues."""
    
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Background
    netflix_red = (229, 9, 20, 255)
    dark_bg = (20, 20, 20, 255)
    
    # Draw rounded square background
    margin = 20
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=30,
        fill=dark_bg
    )
    
    # Try to use a nice font, fallback to default
    try:
        # Try common Windows fonts
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
            "C:/Windows/Fonts/impact.ttf",    # Impact
            "C:/Windows/Fonts/verdanab.ttf",  # Verdana Bold
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 140)
                break
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Draw "M" text
    text = "M"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]
    
    # Draw text with shadow for depth
    shadow_offset = 4
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), text, fill=netflix_red, font=font)
    
    # Save
    icon_path = os.path.join(os.path.dirname(__file__), 'MovieFlix.ico')
    
    # Create multiple sizes
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []
    
    for size_tuple in sizes:
        resized = image.resize(size_tuple, Image.Resampling.LANCZOS)
        images.append(resized)
    
    image.save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    print(f"✓ Icon created: {icon_path}")
    return icon_path


if __name__ == "__main__":
    try:
        print("Creating MovieFlix icon...")
        
        # Try the polygon-based approach first
        try:
            create_movieflix_icon()
            print("✓ Custom M icon created successfully!")
        except Exception as e:
            print(f"⚠ Polygon method failed: {e}")
            print("Trying text-based method...")
            create_simple_text_icon()
            print("✓ Text-based icon created successfully!")
        
        print("\nIcon file: MovieFlix.ico")
        print("Location: Current directory")
        print("\nNow run: create_desktop_shortcut.ps1")
        
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        print("\nAlternative: Download a red M icon online")
        print("Save as MovieFlix.ico in the project folder")

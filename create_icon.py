#!/usr/bin/env python3
"""
Simple script to create an icon for the Eviver Code Editor application.
This creates a basic colored square with the letter 'E' in it.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create a 256x256 image with a blue background
img = Image.new('RGBA', (256, 256), color=(41, 128, 185, 255))
draw = ImageDraw.Draw(img)

# Try to load a font, or use default
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 160)
except IOError:
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 160)
    except IOError:
        font = ImageFont.load_default()

# Draw a white 'E' in the center
text = "E"
text_width, text_height = draw.textsize(text, font=font)
position = ((256 - text_width) // 2, (256 - text_height) // 2)
draw.text(position, text, font=font, fill=(255, 255, 255, 255))

# Save the image
img.save("icon.png")
print(f"Icon created at {os.path.abspath('icon.png')}") 
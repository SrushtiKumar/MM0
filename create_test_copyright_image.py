#!/usr/bin/env python3
"""
Create a test image for copyright embedding testing
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """Create a simple test image"""
    # Create a 400x300 image with a light blue background
    image = Image.new('RGB', (400, 300), color=(173, 216, 230))
    
    # Add some text
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add text to the image
    draw.text((50, 100), "TEST IMAGE", fill=(0, 0, 128), font=font)
    draw.text((50, 140), "For Copyright Protection", fill=(0, 0, 128), font=font)
    draw.text((50, 180), "VeilForge Demo", fill=(128, 0, 0), font=font)
    
    # Add a simple border
    draw.rectangle([10, 10, 390, 290], outline=(0, 0, 128), width=3)
    
    # Save the image
    output_path = "test_copyright_carrier.png"
    image.save(output_path, "PNG")
    
    print(f"✅ Test image created: {output_path}")
    print(f"   Size: {image.size}")
    print(f"   Mode: {image.mode}")
    
    return output_path

if __name__ == "__main__":
    create_test_image()
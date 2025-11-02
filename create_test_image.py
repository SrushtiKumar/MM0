#!/usr/bin/env python3
"""
Create a simple test image for steganography testing
"""

import numpy as np
from PIL import Image

def create_test_image():
    """Create a simple test image"""
    
    # Create a simple 200x200 RGB image
    width, height = 200, 200
    
    # Create a gradient image
    image_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            # Create a gradient pattern
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = int(255 * ((x + y) / (width + height)))
            
            image_array[y, x] = [r, g, b]
    
    # Create PIL image
    img = Image.fromarray(image_array, 'RGB')
    
    # Save as PNG
    img.save('test_image.png')
    print("✅ Created test_image.png for steganography testing")

if __name__ == "__main__":
    try:
        create_test_image()
    except ImportError:
        print("❌ PIL (Pillow) not available, cannot create test image")
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
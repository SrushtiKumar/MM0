#!/usr/bin/env python3

import os
from PIL import Image
import numpy as np

def analyze_image_capacity(image_path):
    """Analyze the capacity of an image for steganography."""
    try:
        print(f"Analyzing: {image_path}")
        
        # Get file size
        file_size = os.path.getsize(image_path)
        print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Load image
        img = Image.open(image_path)
        print(f"Image format: {img.format}")
        print(f"Image mode: {img.mode}")
        print(f"Image size: {img.size}")
        
        # Convert to RGB to ensure 3 channels
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print("Converted to RGB")
        
        # Get dimensions
        width, height = img.size
        channels = 3  # RGB
        
        # Calculate capacity
        total_pixels = width * height
        total_positions = total_pixels * channels
        capacity_bytes = total_positions // 8  # 1 bit per position
        
        print(f"\nCapacity Analysis:")
        print(f"Width: {width:,} pixels")
        print(f"Height: {height:,} pixels") 
        print(f"Total pixels: {total_pixels:,}")
        print(f"Total bit positions: {total_positions:,}")
        print(f"Theoretical capacity: {capacity_bytes:,} bytes ({capacity_bytes/1024:.2f} KB, {capacity_bytes/1024/1024:.2f} MB)")
        
        # Test with 412KB
        test_size = 412 * 1024  # 412KB in bytes
        print(f"\nTest payload (412KB): {test_size:,} bytes")
        print(f"Fits in image: {'YES' if test_size < capacity_bytes else 'NO'}")
        print(f"Usage: {(test_size / capacity_bytes * 100):.2f}%")
        
        return capacity_bytes
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return 0

if __name__ == "__main__":
    # Test with any PNG files in the current directory
    png_files = [f for f in os.listdir('.') if f.lower().endswith('.png')]
    
    if png_files:
        print("Found PNG files:")
        for i, f in enumerate(png_files[:3]):  # Test first 3 files
            print(f"{i+1}. {f}")
            analyze_image_capacity(f)
            print("-" * 50)
    else:
        print("No PNG files found in current directory")
        
        # Create a test image similar to 11MB
        print("Creating test image...")
        # Estimate dimensions for 11MB image
        width, height = 4000, 3000
        img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        test_file = "test_11mb_image.png"
        img.save(test_file)
        
        print(f"Created {test_file}")
        analyze_image_capacity(test_file)
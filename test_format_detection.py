#!/usr/bin/env python3
"""
Test improved format detection in layered containers
"""

import sys
import os
sys.path.append('.')

def test_improved_format_detection():
    """Test that the improved format detection works correctly"""
    print("🧪 TESTING IMPROVED FORMAT DETECTION")
    print("="*60)
    
    try:
        from enhanced_app import (
            create_layered_data_container,
            extract_layered_data_container,
            is_layered_container
        )
        
        print("1. Creating test binary data...")
        
        # Create a simple PNG image
        png_data = bytearray([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D,  # IHDR length
            0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x02,  # Width: 2
            0x00, 0x00, 0x00, 0x02,  # Height: 2
            0x08, 0x02, 0x00, 0x00, 0x00,  # Bit depth, color type, etc.
            0x01, 0x2B, 0x05, 0x5B,  # CRC
            0x00, 0x00, 0x00, 0x16,  # IDAT length
            0x49, 0x44, 0x41, 0x54,  # IDAT
            # Simple 2x2 image data
            0x78, 0x9C, 0x63, 0xF8, 0xCF, 0x80, 0x01, 0x19, 0x00, 0x40, 0x00, 0x03, 
            0x00, 0xC4, 0xFF, 0x7F, 0x26, 0xE5, 0x0B, 0x1C,
            0x6C, 0xBF, 0xC8, 0x30,  # CRC
            0x00, 0x00, 0x00, 0x00,  # IEND length
            0x49, 0x45, 0x4E, 0x44,  # IEND
            0xAE, 0x42, 0x60, 0x82   # CRC
        ])
        
        png_bytes = bytes(png_data)
        print(f"   🖼️  PNG data: {len(png_bytes)} bytes")
        print(f"       Header: {png_bytes[:8].hex()}")
        
        # Create a JPEG header
        jpeg_data = bytearray([
            0xFF, 0xD8, 0xFF, 0xE0,  # JPEG signature
            0x00, 0x10,  # Length
            0x4A, 0x46, 0x49, 0x46,  # "JFIF"
            0x00, 0x01, 0x01, 0x01,  # Version etc.
            0x00, 0x48, 0x00, 0x48,  # Resolution
            0x00, 0x00,  # Thumbnail
            # Minimal JPEG data
            0xFF, 0xD9  # End of image
        ])
        
        jpeg_bytes = bytes(jpeg_data)
        print(f"   📸 JPEG data: {len(jpeg_bytes)} bytes")
        print(f"       Header: {jpeg_bytes[:4].hex()}")
        
        # Text message
        text_message = "This is a text message"
        print(f"   📄 Text: {text_message}")
        
        print(f"\n2. Testing format detection with generic filenames...")
        
        # Test Case 1: No filenames provided - should auto-detect
        layers_no_names = [png_bytes, jpeg_bytes, text_message]
        
        container1 = create_layered_data_container(layers_no_names)
        print(f"   📦 Container created: {len(container1)} chars")
        
        if is_layered_container(container1):
            layers1 = extract_layered_data_container(container1)
            print(f"   📁 Extracted {len(layers1)} layers:")
            
            for i, (content, filename) in enumerate(layers1):
                print(f"     Layer {i+1}: {filename} ({type(content)}, {len(content)} bytes)")
                
                if filename.endswith('.png'):
                    if isinstance(content, bytes) and content.startswith(b'\x89PNG'):
                        print(f"       ✅ PNG detected and preserved correctly")
                    else:
                        print(f"       ❌ PNG detection failed")
                        
                elif filename.endswith('.jpg'):
                    if isinstance(content, bytes) and content.startswith(b'\xff\xd8\xff'):
                        print(f"       ✅ JPEG detected and preserved correctly")
                    else:
                        print(f"       ❌ JPEG detection failed")
                        
                elif filename.endswith('.txt'):
                    if isinstance(content, str) and content == text_message:
                        print(f"       ✅ Text detected and preserved correctly")
                    else:
                        print(f"       ❌ Text detection failed")
        
        print(f"\n3. Testing format detection with generic existing filenames...")
        
        # Test Case 2: Generic filenames that should be improved
        layers_generic = [
            (png_bytes, "existing_data"),
            (jpeg_bytes, "layer_data"), 
            (text_message, "message.txt")
        ]
        
        container2 = create_layered_data_container(layers_generic)
        print(f"   📦 Container created: {len(container2)} chars")
        
        if is_layered_container(container2):
            layers2 = extract_layered_data_container(container2)
            print(f"   📁 Extracted {len(layers2)} layers:")
            
            success = True
            for i, (content, filename) in enumerate(layers2):
                print(f"     Layer {i+1}: {filename} ({type(content)}, {len(content)} bytes)")
                
                # Check if format was properly detected and filename corrected
                if i == 0:  # PNG layer
                    if not filename.endswith('.png'):
                        print(f"       ❌ PNG filename not corrected from generic name")
                        success = False
                    elif not (isinstance(content, bytes) and content.startswith(b'\x89PNG')):
                        print(f"       ❌ PNG content corrupted")
                        success = False
                    else:
                        print(f"       ✅ PNG format correctly detected and preserved")
                        
                elif i == 1:  # JPEG layer
                    if not filename.endswith('.jpg'):
                        print(f"       ❌ JPEG filename not corrected from generic name")
                        success = False
                    elif not (isinstance(content, bytes) and content.startswith(b'\xff\xd8\xff')):
                        print(f"       ❌ JPEG content corrupted")
                        success = False
                    else:
                        print(f"       ✅ JPEG format correctly detected and preserved")
                        
                elif i == 2:  # Text layer
                    if not filename.endswith('.txt'):
                        print(f"       ❌ Text filename issue")
                        success = False
                    elif not (isinstance(content, str) and content == text_message):
                        print(f"       ❌ Text content corrupted")
                        success = False
                    else:
                        print(f"       ✅ Text format correctly preserved")
            
            return success
        else:
            print(f"   ❌ Container not detected as layered")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_improved_format_detection()
    
    print(f"\n" + "="*60)
    print("FORMAT DETECTION TEST RESULT")
    print("="*60)
    
    if success:
        print("✅ SUCCESS: Improved format detection working correctly!")
        print("   • PNG images properly detected and named as .png files")
        print("   • JPEG images properly detected and named as .jpg files") 
        print("   • Text messages preserved as .txt files")
        print("   • Generic filenames automatically corrected")
        print("   • Binary formats preserved without corruption")
    else:
        print("❌ FAILURE: Format detection needs more work")
        print("   Files may still appear as .bin format")
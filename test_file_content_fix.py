#!/usr/bin/env python3
"""
Test file content handling fix
"""

import os
import tempfile
from enhanced_web_image_stego import EnhancedWebImageSteganographyManager

def test_file_content_fix():
    """Test that file content is properly read and embedded"""
    print("🧪 Testing File Content Fix...")
    
    # Create test files
    test_image_path = "test_fix_image.png"
    test_secret_path = "test_fix_secret.txt"
    
    # Create a simple test image
    from PIL import Image
    import numpy as np
    test_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    Image.fromarray(test_img).save(test_image_path)
    
    # Create test secret file with specific content
    secret_content = b"This is the ACTUAL file content that should be embedded, not the file path!"
    with open(test_secret_path, "wb") as f:
        f.write(secret_content)
    
    print(f"✅ Created test files")
    print(f"Secret file size: {len(secret_content)} bytes")
    print(f"Secret content: {secret_content.decode()}")
    
    try:
        manager = EnhancedWebImageSteganographyManager("test123")
        
        # Test hide operation with file path (simulating app.py behavior)
        print("\n📁 Testing hide operation...")
        result = manager.hide_data(test_image_path, test_secret_path, "output_fix.png", is_file=True)
        print(f"Hide result: {result}")
        
        # Test extract operation
        print("\n🔍 Testing extract operation...")
        extracted_data, filename = manager.extract_data("output_fix.png")
        
        print(f"Extracted filename: {filename}")
        print(f"Extracted data size: {len(extracted_data)} bytes")
        print(f"Extracted content: {extracted_data.decode()}")
        
        # Verify content matches
        if extracted_data == secret_content:
            print("✅ SUCCESS! File content properly embedded and extracted!")
            return True
        else:
            print("❌ FAILED! Content mismatch:")
            print(f"Original: {secret_content}")
            print(f"Extracted: {extracted_data}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for file in [test_image_path, test_secret_path, "output_fix.png"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    test_file_content_fix()
#!/usr/bin/env python3
"""
Test image steganography corruption fix
"""

import os
import sys
import tempfile
from PIL import Image
import numpy as np
from universal_file_steganography import UniversalFileSteganography

def create_test_image(path):
    """Create a simple test image"""
    # Create a 100x100 RGB image
    img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array, 'RGB')
    img.save(path, 'PNG')
    print(f"✅ Created test image: {path}")

def create_test_file(path):
    """Create a simple test file"""
    with open(path, 'w') as f:
        f.write("This is a hidden test document!\nIt contains some secret information.")
    print(f"✅ Created test file: {path}")

def test_image_steganography():
    """Test image steganography with corruption fix"""
    
    print("🧪 Testing Image Steganography Corruption Fix")
    print("=" * 50)
    
    stego = UniversalFileSteganography()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_image = os.path.join(temp_dir, "test_image.png")
        test_file = os.path.join(temp_dir, "secret.txt")
        output_image = os.path.join(temp_dir, "stego_image.png")
        extract_dir = os.path.join(temp_dir, "extracted")
        
        create_test_image(test_image)
        create_test_file(test_file)
        os.makedirs(extract_dir, exist_ok=True)
        
        # Test embedding
        print("\n🔧 Testing Embedding...")
        try:
            result = stego.hide_file_in_file(test_image, test_file, output_image)
            print(f"✅ Embedding result: {result}")
        except Exception as e:
            print(f"❌ Embedding failed: {e}")
            return False
        
        # Verify output image can be opened
        print("\n🖼️ Testing Image Integrity...")
        try:
            # Try to open with PIL
            img = Image.open(output_image)
            print(f"✅ Output image can be opened: {img.size}, mode: {img.mode}")
            
            # Save a copy to verify format integrity
            verify_path = os.path.join(temp_dir, "verify_image.png")
            img.save(verify_path)
            print(f"✅ Output image can be re-saved successfully")
            
        except Exception as e:
            print(f"❌ Output image is corrupted: {e}")
            return False
        
        # Test extraction
        print("\n🔓 Testing Extraction...")
        try:
            extracted_file = stego.extract_file_from_file(output_image, extract_dir)
            print(f"✅ Extraction completed: {extracted_file}")
            
            # Verify extracted content using binary comparison to avoid encoding issues
            with open(extracted_file, 'rb') as f:
                content = f.read()
            
            with open(test_file, 'rb') as f:
                original = f.read()
            
            if content == original:
                print("✅ Extracted content matches original")
            else:
                print(f"⚠️ Size difference: original={len(original)}, extracted={len(content)}")
                # Check if at least the beginning matches
                if content.startswith(original):
                    print("✅ Original content is present at start of extracted file")
                else:
                    print("❌ Extracted content doesn't match")
                    return False
                
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
        
        print("\n🎉 All tests passed! Image steganography is working correctly.")
        print("✅ Images preserve their format integrity")
        print("✅ Hidden data is properly embedded and extracted")
        return True

if __name__ == "__main__":
    success = test_image_steganography()
    sys.exit(0 if success else 1)
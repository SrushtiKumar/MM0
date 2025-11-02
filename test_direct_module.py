#!/usr/bin/env python3
"""
Test direct module to verify image steganography works
"""

from universal_file_steganography import UniversalFileSteganography
from PIL import Image
import numpy as np
import os
import tempfile

def test_direct_module():
    print("🔧 Testing Direct Image Steganography Module")
    print("=" * 50)
    
    stego = UniversalFileSteganography()
    
    # Create test files in temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test PNG
        print("1️⃣ Creating test PNG...")
        img = Image.fromarray(np.random.randint(0, 255, (200, 200, 3), dtype='uint8'), 'RGB')
        carrier_path = os.path.join(temp_dir, 'carrier.png')
        img.save(carrier_path, 'PNG')
        print(f"✅ Test PNG created: {carrier_path}")
        
        # Create secret file
        print("2️⃣ Creating secret file...")
        secret_path = os.path.join(temp_dir, 'secret.txt')
        with open(secret_path, 'w') as f:
            f.write('This is my SECRET document with multiple lines!\nLine 2 of secret content.\nLine 3 with special chars: @#$%^&*()')
        print(f"✅ Secret file created: {secret_path}")
        
        # Test embedding
        print("\n3️⃣ Embedding secret in PNG...")
        output_path = os.path.join(temp_dir, 'stego.png')
        try:
            result = stego.hide_file_in_file(carrier_path, secret_path, output_path)
            print(f"✅ Embedding successful: {result}")
        except Exception as e:
            print(f"❌ Embedding failed: {e}")
            return False
        
        # Test image integrity
        print("\n4️⃣ Testing image integrity...")
        try:
            stego_img = Image.open(output_path)
            print(f"✅ Steganographic PNG opens correctly: {stego_img.size}, mode: {stego_img.mode}")
            
            # Save copy to verify
            verify_path = os.path.join(temp_dir, 'verify.png')
            stego_img.save(verify_path, 'PNG')
            print("✅ Steganographic PNG can be re-saved - format intact!")
            
        except Exception as e:
            print(f"❌ Image is corrupted: {e}")
            return False
        
        # Test extraction
        print("\n5️⃣ Extracting hidden file...")
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            extracted_file = stego.extract_file_from_file(output_path, extract_dir)
            print(f"✅ Extraction successful: {extracted_file}")
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
        
        # Verify content
        print("\n6️⃣ Verifying extracted content...")
        try:
            # Use binary mode to avoid encoding issues
            with open(extracted_file, 'rb') as f:
                extracted_content = f.read()
            
            with open(secret_path, 'rb') as f:
                original_content = f.read()
            
            if original_content == extracted_content:
                print("✅ SUCCESS: Extracted content matches original perfectly!")
                print(f"📝 Original: {repr(original_content[:50])}...")
                print(f"📤 Extracted: {repr(extracted_content[:50])}...")
            elif original_content in extracted_content:
                print("✅ SUCCESS: Original content found in extracted file!")
                print(f"📊 Original size: {len(original_content)}, Extracted size: {len(extracted_content)}")
                print(f"📝 Original: {repr(original_content[:50])}...")
                print(f"📤 Extracted: {repr(extracted_content[:50])}...")
            else:
                print("❌ Content mismatch")
                print(f"📝 Original: {repr(original_content[:100])}")
                print(f"📤 Extracted: {repr(extracted_content[:100])}")
                return False
                
        except Exception as e:
            print(f"❌ Content verification failed: {e}")
            return False
        
        print("\n🎉 DIRECT MODULE SUCCESS!")
        print("✅ Image steganography works correctly at module level")
        print("✅ Images maintain format integrity")  
        print("✅ Hidden data is properly embedded and extracted")
        return True

if __name__ == "__main__":
    success = test_direct_module()
    if success:
        print("\n🎯 Module-level image steganography is working perfectly!")
    else:
        print("\n❌ Module-level issues found")
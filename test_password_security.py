#!/usr/bin/env python3
"""
Test password security in steganography
This test should demonstrate that wrong passwords fail to extract data
"""

from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
from PIL import Image
import numpy as np
import os

def create_test_image():
    """Create a simple test image"""
    img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save("test_security_image.png")
    return "test_security_image.png"

def test_password_security():
    """Test that wrong passwords fail to extract data"""
    print("🔐 Testing password security...")
    
    # Create test image
    test_image = create_test_image()
    
    # Test with correct password
    correct_password = "correct_password_123"
    secret_message = "This is a secret message that should only be extractable with the correct password!"
    
    print(f"\n1. Hiding data with password: '{correct_password}'")
    manager_hide = EnhancedWebImageSteganographyManager(correct_password)
    
    try:
        result = manager_hide.hide_data(test_image, secret_message, "stego_image.png", False)
        print(f"✅ Hide operation successful: {result}")
    except Exception as e:
        print(f"❌ Hide operation failed: {e}")
        return
    
    # Test extraction with CORRECT password
    print(f"\n2. Extracting with CORRECT password: '{correct_password}'")
    manager_correct = EnhancedWebImageSteganographyManager(correct_password)
    
    try:
        extracted_data, filename = manager_correct.extract_data("stego_image.png")
        extracted_text = extracted_data.decode('utf-8')
        print(f"✅ Extraction with correct password successful!")
        print(f"   Extracted: {extracted_text}")
        if secret_message in extracted_text:
            print("✅ Correct message extracted!")
        else:
            print("❌ Wrong message extracted!")
    except Exception as e:
        print(f"❌ Extraction with correct password failed: {e}")
    
    # Test extraction with WRONG passwords
    wrong_passwords = ["wrong_password", "123456", "", "different_password", "hacker_attempt"]
    
    for wrong_password in wrong_passwords:
        print(f"\n3. Testing extraction with WRONG password: '{wrong_password}'")
        manager_wrong = EnhancedWebImageSteganographyManager(wrong_password)
        
        try:
            extracted_data, filename = manager_wrong.extract_data("stego_image.png")
            extracted_text = extracted_data.decode('utf-8')
            print(f"❌ SECURITY ISSUE: Wrong password '{wrong_password}' successfully extracted data!")
            print(f"   This should NOT happen! Extracted: {extracted_text[:50]}...")
        except Exception as e:
            print(f"✅ Correct behavior: Wrong password '{wrong_password}' failed to extract: {e}")
    
    # Cleanup
    for file in ["test_security_image.png", "stego_image.png"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    test_password_security()
#!/usr/bin/env python3
"""
Direct test of video steganography with encryption
"""

import os
from final_video_steganography import FinalVideoSteganographyManager

def test_video_encryption():
    print("=== Testing Video Steganography with Encryption ===\n")
    
    # Test parameters
    video_path = "comprehensive_test_video.mp4"  # Use existing video
    password = "test123"
    secret_message = "X"  # Simple test message
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    print(f"Using video: {video_path}")
    print(f"Password: '{password}'")
    print(f"Message: '{secret_message}'")
    
    # Create manager with password
    manager = FinalVideoSteganographyManager(password=password)
    print(f"✅ Created manager with password")
    
    # Test embedding
    print(f"\n1. Embedding message...")
    result = manager.hide_data(
        video_path=video_path,
        payload=secret_message,
        output_path="test_video_encrypted.avi",
        is_file=False
    )
    
    if not result.get('success'):
        print(f"❌ Embedding failed: {result.get('error')}")
        return False
    
    output_path = result['output_path']
    print(f"✅ File embedded successfully in: {output_path}")
    
    # Test extraction with correct password
    print(f"\n2. Extracting with correct password...")
    extracted_result = manager.extract_data(output_path)
    
    if extracted_result is None:
        print(f"❌ ERROR: Extraction returned None")
        return False
    
    extracted_data, filename = extracted_result
    if extracted_data is None:
        print(f"❌ ERROR: No data extracted")
        return False
    
    try:
        extracted_message = extracted_data.decode('utf-8')
        print(f"✅ Extracted message: '{extracted_message}'")
        
        if extracted_message == secret_message:
            print(f"✅ SUCCESS: Messages match!")
            return True
        else:
            print(f"❌ ERROR: Messages don't match")
            print(f"   Expected: '{secret_message}'")
            print(f"   Got:      '{extracted_message}'")
            return False
    except Exception as e:
        print(f"❌ ERROR: Could not decode extracted data: {e}")
        print(f"   Raw data: {extracted_data}")
        return False
    
    # Encrypt
    encrypted = video_stego._encrypt_data(test_data)
    print(f"Encrypted data: {encrypted}")
    
    # Decrypt
    decrypted = video_stego._decrypt_data(encrypted)
    print(f"Decrypted data: {decrypted}")
    
    # Check if they match
    if test_data == decrypted:
        print("✅ Encryption/decryption works correctly")
        return True
    else:
        print(f"❌ Encryption/decryption failed!")
        print(f"   Expected: {test_data}")
        print(f"   Got:      {decrypted}")
        return False

def test_wrong_password():
    """Test decryption with wrong password"""
    print("\nTesting decryption with wrong password...")
    
    password1 = "correct123"
    password2 = "wrong456"
    
    stego1 = EnhancedWebVideoSteganography(password1)
    stego2 = EnhancedWebVideoSteganography(password2)
    
    test_data = b'{"type": "text", "content": "Secret message"}'
    print(f"Original data: {test_data}")
    
    # Encrypt with password1
    encrypted = stego1._encrypt_data(test_data)
    print(f"Encrypted with password1: {encrypted}")
    
    # Try to decrypt with password2 (wrong password)
    decrypted = stego2._decrypt_data(encrypted)
    print(f"Decrypted with password2: {decrypted}")
    
    # Try to parse as JSON
    try:
        import json
        parsed = json.loads(decrypted.decode('utf-8'))
        print(f"❌ PROBLEM: Wrong password decrypted valid JSON: {parsed}")
        return False
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"✅ Good: Wrong password failed JSON parsing: {e}")
        return True

if __name__ == "__main__":
    test1 = test_encryption_decryption()
    test2 = test_wrong_password()
    
    if test1 and test2:
        print("\n✅ All encryption tests passed!")
    else:
        print("\n❌ Some encryption tests failed!")
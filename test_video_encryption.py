#!/usr/bin/env python3
"""Debug video steganography encryption/decryption"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_web_video_stego import EnhancedWebVideoSteganography

def test_encryption_decryption():
    """Test if our encryption/decryption methods work correctly"""
    print("Testing video steganography encryption/decryption...")
    
    password = "testpass123"
    video_stego = EnhancedWebVideoSteganography(password)
    
    # Test data
    test_data = b'{"type": "text", "content": "Hello World"}'
    print(f"Original data: {test_data}")
    
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
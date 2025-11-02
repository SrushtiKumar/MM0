#!/usr/bin/env python3
"""
Direct test of audio steganography with encryption
"""

import tempfile
import os
from universal_file_audio import UniversalFileAudio

def test_audio_encryption():
    """Test audio steganography encryption directly"""
    print("=== Direct Audio Steganography Test ===")
    
    # Create test files
    audio_path = "C:\\Users\\Administrator\\Documents\\Git\\vF\\enhanced_audio_test.wav"
    secret_text = "Hello Audio World"
    password = "test123"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as secret_file:
        secret_file.write(secret_text.encode('utf-8'))
        secret_file_path = secret_file.name
    
    output_path = "direct_audio_stego.wav"
    
    try:
        # Test direct audio steganography with password
        stego = UniversalFileAudio(password=password)
        
        print(f"1. Hiding text '{secret_text}' in {audio_path}")
        print(f"   Password: {password}")
        
        result = stego.embed_file(audio_path, secret_file_path, output_path)
        print(f"✅ Hide result: {result}")
        
        print(f"2. Extracting from {output_path}")
        extracted_path = stego.extract_file(output_path)
        
        with open(extracted_path, 'rb') as f:
            extracted_content = f.read()
        
        # Check if it needs decryption
        print(f"Raw extracted content (first 50 bytes): {extracted_content[:50]}")
        
        # Try to decrypt if it looks encrypted
        try:
            if password and len(extracted_content) > 28:  # Minimum for encrypted data
                decrypted_content = stego._decrypt_data(extracted_content)
                final_text = decrypted_content.decode('utf-8')
                print(f"✅ Decrypted text: '{final_text}'")
            else:
                final_text = extracted_content.decode('utf-8')
                print(f"✅ Direct text: '{final_text}'")
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            try:
                final_text = extracted_content.decode('utf-8')
                print(f"✅ Fallback text: '{final_text}'")
            except:
                print(f"❌ Cannot decode as text")
                return
        
        if final_text == secret_text:
            print("✅ SUCCESS: Direct audio steganography works!")
        else:
            print(f"❌ MISMATCH: Expected '{secret_text}', got '{final_text}'")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            os.unlink(secret_file_path)
            os.unlink(output_path)
            if 'extracted_path' in locals():
                os.unlink(extracted_path)
        except:
            pass

if __name__ == "__main__":
    test_audio_encryption()
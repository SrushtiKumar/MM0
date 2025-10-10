#!/usr/bin/env python3
"""
Direct Test for Enhanced Audio Steganography
Tests the functionality without requiring web server
"""

import os
import tempfile
from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager

def test_enhanced_audio_direct():
    """Test enhanced audio steganography directly"""
    print("🎵 Testing Enhanced Audio Steganography (Direct)")
    
    # Use existing test audio file
    test_audio = "enhanced_audio_test.wav"
    
    if not os.path.exists(test_audio):
        print(f"❌ Test audio file not found: {test_audio}")
        return
    
    manager = EnhancedWebAudioSteganographyManager()
    
    # Test 1: Text message (compatibility test)
    print(f"\n{'='*50}")
    print("Test 1: Text Message")
    print(f"{'='*50}")
    
    test_text = "Hello Enhanced Audio Steganography!"
    result = manager.hide_data(test_audio, test_text, 'direct_text_output.wav', is_file=False)
    
    if result.get('success'):
        print("✅ Text hiding successful")
        
        extracted_bytes, filename = manager.extract_data('direct_text_output.wav')
        if extracted_bytes:
            extracted_text = extracted_bytes.decode('utf-8')
            print(f"✅ Text extraction successful: '{extracted_text}'")
            
            if extracted_text == test_text:
                print("🎉 Text test PASSED!")
            else:
                print("❌ Text test FAILED!")
        else:
            print("❌ Text extraction failed")
    else:
        print(f"❌ Text hiding failed: {result.get('error')}")
    
    # Test 2: File content
    print(f"\n{'='*50}")
    print("Test 2: File Content")
    print(f"{'='*50}")
    
    # Create a test file
    test_file = 'test_audio_file.txt'
    test_file_content = "This is a test file content that should be embedded in the audio file!"
    
    with open(test_file, 'w') as f:
        f.write(test_file_content)
    
    result = manager.hide_data(test_audio, test_file, 'direct_file_output.wav', is_file=True)
    
    if result.get('success'):
        print("✅ File hiding successful")
        
        extracted_bytes, filename = manager.extract_data('direct_file_output.wav')
        if extracted_bytes:
            extracted_content = extracted_bytes.decode('utf-8')
            print(f"✅ File extraction successful")
            print(f"   Filename: {filename}")
            print(f"   Content: '{extracted_content}'")
            
            if extracted_content == test_file_content:
                print("🎉 File test PASSED!")
            else:
                print("❌ File test FAILED!")
                print(f"Expected: '{test_file_content}'")
                print(f"Got: '{extracted_content}'")
        else:
            print("❌ File extraction failed")
    else:
        print(f"❌ File hiding failed: {result.get('error')}")
    
    # Test 3: Binary file content (image-like)
    print(f"\n{'='*50}")
    print("Test 3: Binary File Content")
    print(f"{'='*50}")
    
    # Create a test binary file
    test_binary_file = 'test_binary.dat'
    test_binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'  # Fake PNG header
    
    with open(test_binary_file, 'wb') as f:
        f.write(test_binary_content)
    
    result = manager.hide_data(test_audio, test_binary_file, 'direct_binary_output.wav', is_file=True)
    
    if result.get('success'):
        print("✅ Binary file hiding successful")
        
        extracted_bytes, filename = manager.extract_data('direct_binary_output.wav')
        if extracted_bytes:
            print(f"✅ Binary file extraction successful")
            print(f"   Filename: {filename}")
            print(f"   Content size: {len(extracted_bytes)} bytes")
            
            if extracted_bytes == test_binary_content:
                print("🎉 Binary file test PASSED!")
            else:
                print("❌ Binary file test FAILED!")
                print(f"Expected {len(test_binary_content)} bytes, got {len(extracted_bytes)} bytes")
        else:
            print("❌ Binary file extraction failed")
    else:
        print(f"❌ Binary file hiding failed: {result.get('error')}")
    
    # Cleanup
    for file in [test_file, test_binary_file, 'direct_text_output.wav', 'direct_file_output.wav', 'direct_binary_output.wav']:
        if os.path.exists(file):
            os.remove(file)
    
    print(f"\n🎉 Enhanced audio steganography direct testing complete!")

if __name__ == "__main__":
    test_enhanced_audio_direct()
#!/usr/bin/env python3
"""
Simple test to verify steganography module behavior
"""

import os
import tempfile
from enhanced_web_audio_stego import EnhancedWebAudioSteganography

def test_audio_steganography():
    """Test the audio steganography module directly"""
    
    # Look for an existing audio file
    audio_files = ["demo_audio.wav", "debug_test_audio.wav", "enhanced_audio_test.wav"]
    audio_file = None
    
    for af in audio_files:
        if os.path.exists(af):
            audio_file = af
            break
    
    if not audio_file:
        print("❌ No audio file found for testing")
        return
    
    print(f"🎵 Testing with {audio_file}")
    
    # Create test content
    test_message = "This is a test secret message!"
    password = "test123"
    
    # Initialize steganography
    stego = EnhancedWebAudioSteganography(password=password)
    
    # Hide data
    output_file = "test_stego_output.wav"
    print(f"📝 Hiding message: '{test_message}'")
    
    result = stego.hide_data(audio_file, test_message, output_file, is_file=False)
    print(f"Hide result: {result}")
    
    if result.get('success'):
        # Extract data
        print("🔍 Extracting data...")
        extracted_data, filename = stego.extract_data(output_file)
        
        print(f"Extracted data type: {type(extracted_data)}")
        print(f"Extracted filename: {filename}")
        print(f"Extracted content: {extracted_data}")
        
        if extracted_data == test_message:
            print("✅ Audio steganography test PASSED!")
        else:
            print(f"❌ Content mismatch: expected '{test_message}', got '{extracted_data}'")
    else:
        print(f"❌ Hide operation failed: {result}")

if __name__ == "__main__":
    test_audio_steganography()
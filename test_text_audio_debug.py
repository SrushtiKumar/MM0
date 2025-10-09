#!/usr/bin/env python3

import os
import tempfile
from universal_text_audio_stego import UniversalTextAudioSteganographyManager

def test_text_audio_steganography():
    print("🧪 Testing Text Audio Steganography with Debug")
    
    # Create test audio file path (you need to have an audio file)
    test_files = ['demo_audio.wav', 'ff-16b-2c-44100hz.wav', 'test_audio.wav']
    audio_file = None
    
    for test_file in test_files:
        if os.path.exists(test_file):
            audio_file = test_file
            break
    
    if not audio_file:
        print("❌ No test audio file found")
        return
    
    print(f"📄 Using audio file: {audio_file}")
    
    # Test message
    test_message = "Hello World! This is a test message for debugging."
    print(f"📝 Test message: '{test_message}'")
    
    # Create steganography manager
    stego_manager = UniversalTextAudioSteganographyManager()
    
    # Create output directory
    os.makedirs('debug_outputs', exist_ok=True)
    output_path = os.path.join('debug_outputs', 'test_output.wav')
    
    try:
        print("\n🔒 HIDING TEXT MESSAGE...")
        result = stego_manager.hide_data(audio_file, test_message, output_path)
        
        if result['success']:
            print(f"✅ Successfully hidden message in: {result['output_path']}")
            
            print("\n🔓 EXTRACTING TEXT MESSAGE...")
            extracted_bytes, filename = stego_manager.extract_data(result['output_path'])
            
            if extracted_bytes:
                # Convert bytes back to text for comparison
                extracted_message = extracted_bytes.decode('utf-8')
                print(f"✅ Successfully extracted: '{extracted_message}'")
                
                if extracted_message == test_message:
                    print("🎉 PERFECT MATCH! Text steganography working correctly.")
                else:
                    print("⚠️ Message extracted but doesn't match exactly")
                    print(f"Original: '{test_message}'")
                    print(f"Extracted: '{extracted_message}'")
            else:
                print(f"❌ Extraction failed: No message returned")
        else:
            print(f"❌ Hiding failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_text_audio_steganography()
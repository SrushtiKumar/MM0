#!/usr/bin/env python3
"""
Test MP3 text steganography specifically
"""

import os
from universal_text_audio_stego import UniversalTextAudioSteganographyManager

def test_mp3_steganography():
    print("🧪 Testing MP3 Text Audio Steganography")
    
    # Check if we have an MP3 file
    mp3_files = ['test.mp3', 'demo.mp3', 'sample.mp3']
    input_file = None
    
    for mp3_file in mp3_files:
        if os.path.exists(mp3_file):
            input_file = mp3_file
            break
    
    if not input_file:
        print("❌ No MP3 file found. Let's create one from demo_audio.wav")
        
        # Convert demo audio to MP3
        if os.path.exists('demo_audio.wav'):
            from pydub import AudioSegment
            audio = AudioSegment.from_wav('demo_audio.wav')
            audio.export('test_demo.mp3', format='mp3', bitrate='192k')
            input_file = 'test_demo.mp3'
            print(f"✅ Created MP3 file: {input_file}")
        else:
            print("❌ No audio files available for testing")
            return
    
    print(f"📄 Using MP3 file: {input_file}")
    
    # Test message
    test_message = "Hello MP3 World! This is a test message."
    print(f"📝 Test message: '{test_message}'")
    
    # Create steganography manager
    stego_manager = UniversalTextAudioSteganographyManager()
    
    # Create output directory
    os.makedirs('debug_outputs', exist_ok=True)
    output_path = os.path.join('debug_outputs', 'test_mp3_output.mp3')
    
    try:
        print("\n🔒 HIDING TEXT MESSAGE IN MP3...")
        result = stego_manager.hide_data(input_file, test_message, output_path)
        
        if result['success']:
            print(f"✅ Successfully hidden message in: {result['output_path']}")
            
            print("\n🔓 EXTRACTING TEXT MESSAGE FROM MP3...")
            extracted_bytes, filename = stego_manager.extract_data(result['output_path'])
            
            if extracted_bytes:
                # Convert bytes back to text for comparison
                extracted_message = extracted_bytes.decode('utf-8')
                print(f"✅ Successfully extracted: '{extracted_message}'")
                
                if extracted_message == test_message:
                    print("🎉 PERFECT MATCH! MP3 text steganography working correctly.")
                else:
                    print("⚠️ Message extracted but doesn't match exactly")
                    print(f"Original: '{test_message}'")
                    print(f"Extracted: '{extracted_message}'")
                    
                    # Check if it's just truncated or has minor differences
                    if test_message.startswith(extracted_message) or extracted_message.startswith(test_message):
                        print("💡 Looks like partial match - MP3 compression may have affected some bits")
            else:
                print(f"❌ Extraction failed: No message returned")
        else:
            print(f"❌ Hiding failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mp3_steganography()
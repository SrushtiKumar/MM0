#!/usr/bin/env python3
"""
Test MP3 format preservation - input MP3 should output MP3
"""

import os
from final_audio_stego import FinalAudioSteganographyManager

def test_mp3_format_preservation():
    """Test that MP3 input produces MP3 output."""
    print("=== Testing MP3 Format Preservation ===")
    
    # Check for existing MP3 files
    mp3_files = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    
    if not mp3_files:
        print("❌ No MP3 files found for testing")
        return False
    
    test_mp3 = mp3_files[0]
    print(f"✅ Using MP3 file for testing: {test_mp3}")
    
    # Test with audio steganography
    manager = FinalAudioSteganographyManager("test123")
    
    # Test message
    test_message = "Testing MP3 format preservation! 🎵→🎵"
    
    # Output should be MP3 (same as input)
    output_file = "test_mp3_preserve_format.mp3"
    
    try:
        print(f"\n--- Testing format preservation ---")
        print(f"Input format: MP3 ({test_mp3})")
        print(f"Expected output format: MP3 ({output_file})")
        
        # Embed
        result = manager.hide_data(test_mp3, test_message, output_file)
        print(f"Embed result: {result}")
        
        # Check actual output file
        actual_output = result.get('output_path', output_file)
        actual_ext = os.path.splitext(actual_output)[1].lower()
        
        print(f"Actual output file: {actual_output}")
        print(f"Actual output extension: {actual_ext}")
        
        # Verify format
        format_preserved = actual_ext == '.mp3'
        print(f"Format preserved: {'✅ YES' if format_preserved else '❌ NO'}")
        
        # Test extraction
        if os.path.exists(actual_output):
            extracted_data, filename = manager.extract_data(actual_output)
            extracted_text = extracted_data.decode('utf-8')
            
            print(f"Extracted text: '{extracted_text}'")
            content_match = extracted_text == test_message
            print(f"Content match: {'✅ YES' if content_match else '❌ NO'}")
            
            # Cleanup
            os.unlink(actual_output)
            
            return format_preserved and content_match
        else:
            print(f"❌ Output file not found: {actual_output}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wav_format_preservation():
    """Test that WAV input produces WAV output."""
    print("\n=== Testing WAV Format Preservation ===")
    
    # Use existing WAV file
    wav_file = "demo_audio.wav"
    if not os.path.exists(wav_file):
        print(f"❌ WAV file not found: {wav_file}")
        return False
    
    manager = FinalAudioSteganographyManager("test123")
    test_message = "Testing WAV format preservation! 🎵→🎵"
    output_file = "test_wav_preserve_format.wav"
    
    try:
        print(f"Input format: WAV ({wav_file})")
        print(f"Expected output format: WAV ({output_file})")
        
        # Embed
        result = manager.hide_data(wav_file, test_message, output_file)
        
        # Check actual output
        actual_output = result.get('output_path', output_file)
        actual_ext = os.path.splitext(actual_output)[1].lower()
        
        print(f"Actual output file: {actual_output}")
        print(f"Actual output extension: {actual_ext}")
        
        format_preserved = actual_ext == '.wav'
        print(f"Format preserved: {'✅ YES' if format_preserved else '❌ NO'}")
        
        # Cleanup
        if os.path.exists(actual_output):
            os.unlink(actual_output)
        
        return format_preserved
        
    except Exception as e:
        print(f"❌ WAV test failed: {e}")
        return False

if __name__ == "__main__":
    mp3_success = test_mp3_format_preservation()
    wav_success = test_wav_format_preservation()
    
    print(f"\n=== Results ===")
    print(f"MP3 format preservation: {'✅ PASSED' if mp3_success else '❌ FAILED'}")
    print(f"WAV format preservation: {'✅ PASSED' if wav_success else '❌ FAILED'}")
    
    overall_success = mp3_success and wav_success
    print(f"\n🎉 Overall test {'PASSED' if overall_success else 'FAILED'}!")
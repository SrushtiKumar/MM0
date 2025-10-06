#!/usr/bin/env python3
"""
Quick test for working audio steganography
"""

from working_audio_stego import WorkingAudioSteganographyManager

def quick_test():
    """Quick test with MP3 file"""
    
    try:
        manager = WorkingAudioSteganographyManager()
        
        # Test with simple text
        test_text = "Hello Audio!"
        print(f"Testing with text: '{test_text}'")
        
        # Hide in MP3
        result = manager.hide_data("test_audio.mp3", test_text, "test_working_output.wav", is_file=False)
        print(f"Hide result: {result}")
        
        # Extract
        extracted_data, filename = manager.extract_data("test_working_output.wav")
        extracted_text = extracted_data.decode('utf-8')
        
        print(f"Extracted: '{extracted_text}'")
        print(f"Filename: {filename}")
        print(f"Success: {extracted_text == test_text}")
        
        return extracted_text == test_text
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
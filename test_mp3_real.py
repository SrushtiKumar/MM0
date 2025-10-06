#!/usr/bin/env python3
"""
Test audio steganography with real MP3 file
"""

from simple_audio_stego import SimpleAudioSteganographyManager

def test_with_mp3():
    """Test with a real MP3 file"""
    
    try:
        # Use the existing MP3 file
        mp3_file = "test_audio.mp3"
        
        manager = SimpleAudioSteganographyManager()
        
        # Test message
        test_message = "Hello from MP3!"
        print(f"Test message: {test_message}")
        
        # Hide data in MP3
        result = manager.hide_data(mp3_file, test_message, "test_mp3_stego.wav", is_file=False)
        print(f"Hide result: {result}")
        
        # Extract data
        extracted_data, filename = manager.extract_data("test_mp3_stego.wav")
        extracted_text = extracted_data.decode('utf-8')
        
        print(f"Extracted text: {extracted_text}")
        print(f"Original filename: {filename}")
        print(f"Match: {'✅ YES' if extracted_text == test_message else '❌ NO'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_with_mp3()
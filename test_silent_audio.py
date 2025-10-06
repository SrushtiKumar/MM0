#!/usr/bin/env python3
"""
Test simple audio steganography with silent audio
"""

import numpy as np
import soundfile as sf
from simple_audio_stego import SimpleAudioSteganographyManager

def test_with_silent_audio():
    """Test with silent audio to isolate the bit manipulation issue"""
    
    # Create silent audio
    duration = 1.0  # 1 second
    sample_rate = 44100
    samples = int(duration * sample_rate)
    
    # Create completely silent audio (all zeros)
    silent_audio = np.zeros(samples, dtype=np.float32)
    
    # Save as WAV
    sf.write("test_silent.wav", silent_audio, sample_rate)
    print(f"Created silent audio: {samples} samples at {sample_rate} Hz")
    
    # Test steganography
    test_message = "Hello World!"
    manager = SimpleAudioSteganographyManager()
    
    try:
        print("\nEmbedding test message...")
        result = manager.hide_data("test_silent.wav", test_message, "test_silent_stego.wav", is_file=False)
        print(f"Embed result: {result}")
        
        print("\nExtracting message...")
        extracted_data, filename = manager.extract_data("test_silent_stego.wav")
        extracted_text = extracted_data.decode('utf-8')
        
        print(f"Original: {test_message}")
        print(f"Extracted: {extracted_text}")
        print(f"Success: {test_message == extracted_text}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_silent_audio()
#!/usr/bin/env python3
"""
Test the reliable audio steganography directly
"""

import numpy as np
import soundfile as sf
from reliable_audio_stego import ReliableAudioSteganography

def test_direct():
    print("=== Direct Test of Reliable Audio Steganography ===")
    
    # Create a simple test audio file
    sample_rate = 44100
    duration = 2  # 2 seconds
    t = np.linspace(0, duration, sample_rate * duration)
    # Create a simple sine wave
    audio = 0.1 * np.sin(2 * np.pi * 440 * t)
    
    input_file = "test_input.wav"
    output_file = "test_output.wav"
    
    # Save test audio
    sf.write(input_file, audio, sample_rate)
    print(f"Created test audio: {input_file}")
    
    # Test steganography
    stego = ReliableAudioSteganography()
    test_message = "Hello World"
    
    print(f"\nTesting with message: '{test_message}'")
    
    # Hide message
    print("\n--- HIDING ---")
    success, result = stego.hide_message(input_file, test_message, output_file)
    print(f"Hide result: {success}")
    if not success:
        print(f"Hide failed: {result}")
        return
    
    # Extract message
    print("\n--- EXTRACTING ---")
    success2, extracted = stego.extract_message(output_file)
    print(f"Extract result: {success2}")
    
    if success2:
        print(f"SUCCESS!")
        print(f"Original: '{test_message}'")
        print(f"Extracted: '{extracted}'")
        print(f"Match: {extracted == test_message}")
    else:
        print(f"FAILED: {extracted}")
        
        # Let's debug the first few bits
        print("\n--- DEBUGGING ---")
        audio_data, sr = sf.read(output_file)
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]
        
        audio_int = (audio_data * 32767).astype(np.int16)
        first_bits = []
        for i in range(min(100, len(audio_int))):
            first_bits.append(str(audio_int[i] & 1))
        
        first_bit_string = ''.join(first_bits)
        print(f"First 100 bits: {first_bit_string}")
        
        # Convert expected header to binary
        header_binary = stego.text_to_binary("HIDE:")
        print(f"Expected header binary: {header_binary}")
        print(f"Header length: {len(header_binary)}")
        
        # Check if header is at the beginning
        actual_header = first_bit_string[:len(header_binary)]
        print(f"Actual first bits:      {actual_header}")
        print(f"Match: {actual_header == header_binary}")

if __name__ == "__main__":
    test_direct()
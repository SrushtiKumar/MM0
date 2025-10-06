#!/usr/bin/env python3
"""
Create a test audio file for demonstrating the working audio steganography
"""

import numpy as np
import wave

def create_test_audio():
    """Create a test audio file for demonstration."""
    sample_rate = 44100
    duration = 5.0  # 5 seconds
    num_samples = int(sample_rate * duration)
    
    # Create a pleasant test tone (A chord: A, C#, E)
    t = np.linspace(0, duration, num_samples, False)
    
    # Frequencies for A chord
    freq_a = 440    # A note
    freq_cs = 554.37  # C# note
    freq_e = 659.25   # E note
    
    # Create the chord
    audio_data = (0.3 * np.sin(2 * np.pi * freq_a * t) +     # A
                 0.2 * np.sin(2 * np.pi * freq_cs * t) +    # C#
                 0.2 * np.sin(2 * np.pi * freq_e * t))      # E
    
    # Add some gentle modulation to make it more interesting
    modulation = 0.1 * np.sin(2 * np.pi * 2 * t)  # 2 Hz modulation
    audio_data = audio_data * (1 + modulation)
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767 * 0.8).astype(np.int16)  # 0.8 for headroom
    
    # Save using wave module
    output_file = "demo_audio.wav"
    with wave.open(output_file, 'wb') as wav_file:
        wav_file.setnchannels(1)        # Mono
        wav_file.setsampwidth(2)        # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"✅ Created test audio file: {output_file}")
    print(f"   Duration: {duration}s")
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Samples: {num_samples}")
    print(f"   Format: 16-bit mono WAV")
    print(f"   Content: A major chord (A, C#, E) with gentle modulation")
    
    return output_file

if __name__ == "__main__":
    create_test_audio()
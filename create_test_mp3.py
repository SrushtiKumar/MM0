#!/usr/bin/env python3
"""
Create a test MP3 file for testing
"""

import numpy as np
import os

def create_test_mp3():
    """Create a test MP3 file using pydub."""
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Create a 5-second test tone (440 Hz A note)
        duration = 5000  # 5 seconds in milliseconds
        tone = Sine(440).to_audio_segment(duration=duration)
        
        # Add a second tone to make it more interesting
        tone2 = Sine(880).to_audio_segment(duration=duration)  # A octave higher
        mixed = tone.overlay(tone2 - 6)  # Mix with second tone 6dB lower
        
        # Export as MP3
        output_file = "demo_audio.mp3"
        mixed.export(output_file, format="mp3", bitrate="128k")
        
        print(f"✅ Created test MP3 file: {output_file}")
        print(f"   Duration: {duration/1000}s")
        print(f"   Content: Mixed 440Hz + 880Hz tones")
        print(f"   Format: MP3 (128k bitrate)")
        
        return output_file
        
    except ImportError:
        print("❌ pydub not available, creating WAV file instead...")
        
        # Fallback: create WAV and manually rename to MP3 for testing
        import wave
        
        sample_rate = 44100
        duration = 5.0
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        audio_data = (0.3 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        
        # Save as WAV first
        wav_file = "temp_demo.wav"
        with wave.open(wav_file, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2) 
            wav.setframerate(sample_rate)
            wav.writeframes(audio_data.tobytes())
        
        # Just rename for testing (not real MP3 but will test the logic)
        mp3_file = "demo_audio_fake.mp3"
        os.rename(wav_file, mp3_file)
        
        print(f"⚠️  Created fake MP3 file (actually WAV): {mp3_file}")
        print(f"   This is just for testing the filename logic")
        
        return mp3_file

if __name__ == "__main__":
    create_test_mp3()
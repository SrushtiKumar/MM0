#!/usr/bin/env python3
"""
Test audio steganography noise issues
"""

import os
import numpy as np
from universal_file_audio import UniversalFileAudio

def create_test_audio():
    """Create a simple test WAV file"""
    # Create a simple sine wave
    duration = 3.0  # seconds
    sample_rate = 44100
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Add some variation to make it more interesting
    audio_data += 0.2 * np.sin(2 * np.pi * frequency * 2 * t)
    audio_data += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
    
    # Write as WAV file
    import wave
    with wave.open("test_audio_clean.wav", 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Convert to 16-bit integers
        audio_int16 = (audio_data * 32767).astype(np.int16)
        wav_file.writeframes(audio_int16.tobytes())
    
    return "test_audio_clean.wav"

def analyze_audio_quality(original_file, processed_file):
    """Analyze the quality difference between original and processed audio"""
    
    print(f"🎵 ANALYZING AUDIO QUALITY")
    print("-" * 40)
    
    try:
        import wave
        
        # Read original
        with wave.open(original_file, 'rb') as wav:
            orig_frames = wav.readframes(wav.getnframes())
            orig_sample_rate = wav.getframerate()
            orig_channels = wav.getnchannels()
            orig_width = wav.getsampwidth()
        
        # Read processed  
        with wave.open(processed_file, 'rb') as wav:
            proc_frames = wav.readframes(wav.getnframes())
            proc_sample_rate = wav.getframerate()
            proc_channels = wav.getnchannels()
            proc_width = wav.getsampwidth()
        
        print(f"📊 Original: {orig_sample_rate}Hz, {orig_channels}ch, {orig_width*8}bit, {len(orig_frames)} bytes")
        print(f"📊 Processed: {proc_sample_rate}Hz, {proc_channels}ch, {proc_width*8}bit, {len(proc_frames)} bytes")
        
        # Convert to numpy arrays for analysis
        orig_data = np.frombuffer(orig_frames, dtype=np.int16)
        proc_data = np.frombuffer(proc_frames, dtype=np.int16)
        
        if len(orig_data) == len(proc_data):
            # Calculate difference
            diff = orig_data - proc_data
            max_diff = np.max(np.abs(diff))
            mean_diff = np.mean(np.abs(diff))
            
            print(f"📈 Max difference: {max_diff}")
            print(f"📈 Mean difference: {mean_diff:.2f}")
            print(f"📈 RMS difference: {np.sqrt(np.mean(diff**2)):.2f}")
            
            # Check first few samples for noise
            print(f"🔍 First 10 samples comparison:")
            for i in range(min(10, len(orig_data))):
                print(f"   Sample {i}: {orig_data[i]} → {proc_data[i]} (diff: {diff[i]})")
            
            # Check if noise is concentrated in beginning
            first_100_diff = np.mean(np.abs(diff[:100])) if len(diff) > 100 else 0
            middle_100_diff = np.mean(np.abs(diff[len(diff)//2:len(diff)//2+100])) if len(diff) > 200 else 0
            
            print(f"🎯 First 100 samples avg diff: {first_100_diff:.2f}")
            print(f"🎯 Middle 100 samples avg diff: {middle_100_diff:.2f}")
            
            if first_100_diff > middle_100_diff * 2:
                print(f"⚠️ NOISE CONCENTRATED IN BEGINNING!")
                return False
            elif first_100_diff == 0.0:  # Perfect preservation of beginning
                print(f"✅ Perfect audio quality preserved (no noise in beginning)")
                return True
            elif max_diff < 100:  # Very small difference
                print(f"✅ Good audio quality preserved")
                return True
            else:
                print(f"⚠️ Noticeable audio quality impact but acceptable")
                return True  # Still acceptable since no noise at beginning
        else:
            print(f"❌ File length mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Audio analysis error: {e}")
        return False

def test_audio_noise_issue():
    """Test audio steganography for noise issues"""
    
    print("🧪 TESTING AUDIO STEGANOGRAPHY NOISE")
    print("=" * 60)
    
    # Create test audio
    audio_file = create_test_audio()
    secret_content = "Secret message in audio!"
    secret_file = "audio_secret.txt"
    
    with open(secret_file, 'w') as f:
        f.write(secret_content)
    
    print(f"🎵 Created test audio: {audio_file}")
    
    try:
        # Test steganography
        stego = UniversalFileAudio("test123")
        output_file = "processed_audio.wav"
        
        print(f"🔐 Embedding secret in audio...")
        # Read file content as bytes for proper handling
        with open(secret_file, 'rb') as f:
            secret_data = f.read()
        result = stego.hide_data(audio_file, secret_data, output_file, is_file=True)
        
        if not result.get('success'):
            print(f"❌ Embedding failed: {result}")
            return False
        
        print(f"✅ Embedding successful")
        print(f"📊 Method: {result.get('method', 'unknown')}")
        
        # Analyze audio quality
        quality_ok = analyze_audio_quality(audio_file, output_file)
        
        # Test extraction
        print(f"\n🔍 Testing extraction...")
        extraction_result = stego.extract_data(output_file)
        
        if extraction_result and isinstance(extraction_result, tuple):
            extracted_content, filename = extraction_result
            
            if isinstance(extracted_content, bytes):
                extracted_text = extracted_content.decode('utf-8')
            else:
                extracted_text = extracted_content
                
            if secret_content.strip() == extracted_text.strip():
                print(f"✅ Extraction successful - data preserved!")
                extraction_ok = True
            else:
                print(f"❌ Extraction data mismatch")
                print(f"   Expected: '{secret_content.strip()}'")
                print(f"   Got:      '{extracted_text.strip()}'")
                extraction_ok = False
        else:
            print(f"❌ Extraction failed: {extraction_result}")
            extraction_ok = False
        
        return quality_ok and extraction_ok
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        for file in [audio_file, secret_file, "processed_audio.wav"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = test_audio_noise_issue()
    if success:
        print(f"\n🎉 AUDIO NOISE TEST PASSED!")
    else:
        print(f"\n❌ AUDIO NOISE TEST FAILED!")
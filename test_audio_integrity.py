#!/usr/bin/env python3
"""
Test audio steganography for file corruption issues
"""

import os
import tempfile
import numpy as np
from scipy.io import wavfile
from universal_file_audio import UniversalFileAudio

def create_test_audio(path, duration_seconds=2, sample_rate=44100):
    """Create a test WAV file"""
    # Generate a simple sine wave
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
    frequency = 440  # A4 note
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
    
    wavfile.write(path, sample_rate, audio_data)
    print(f"✅ Created test audio: {path}")

def test_audio_integrity(audio_path):
    """Test if audio file can be opened and played"""
    try:
        # Try to read the audio file
        sample_rate, audio_data = wavfile.read(audio_path)
        print(f"✅ Audio file readable: {sample_rate} Hz, {len(audio_data)} samples")
        
        # Verify it's valid audio data
        if len(audio_data) > 0 and sample_rate > 0:
            print(f"✅ Audio file is valid and playable")
            return True
        else:
            print(f"❌ Audio file has invalid data")
            return False
            
    except Exception as e:
        print(f"❌ Audio file is corrupted: {e}")
        return False

def test_audio_steganography():
    """Test audio steganography for corruption issues"""
    
    print("🎵 Testing Audio Steganography File Integrity")
    print("=" * 50)
    
    stego = UniversalFileAudio()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        carrier_audio = os.path.join(temp_dir, "carrier.wav")
        secret_file = os.path.join(temp_dir, "secret.txt")
        output_audio = os.path.join(temp_dir, "stego_audio.wav")
        extract_dir = os.path.join(temp_dir, "extracted")
        
        # Create test audio
        print("1️⃣ Creating test audio file...")
        create_test_audio(carrier_audio)
        
        # Create secret file
        print("2️⃣ Creating secret document...")
        with open(secret_file, 'w') as f:
            f.write("This is secret audio content!\nMultiple lines of hidden data.")
        print(f"✅ Secret file created: {secret_file}")
        
        # Test original audio integrity
        print("\n3️⃣ Testing original audio integrity...")
        if not test_audio_integrity(carrier_audio):
            print("❌ Original audio is already corrupted")
            return False
        
        # Test embedding
        print("\n4️⃣ Embedding secret in audio...")
        try:
            # Read the secret file content
            with open(secret_file, 'r') as f:
                secret_content = f.read()
            
            result = stego.hide_data(carrier_audio, secret_content, output_audio, is_file=False)
            print(f"✅ Audio embedding successful: {result}")
        except Exception as e:
            print(f"❌ Audio embedding failed: {e}")
            return False
        
        # Test processed audio integrity - THIS IS THE CRITICAL TEST
        print("\n5️⃣ Testing processed audio integrity...")
        if not test_audio_integrity(output_audio):
            print("❌ CORRUPTION DETECTED: Processed audio file is corrupted!")
            return False
        
        print("✅ SUCCESS: Processed audio file remains playable!")
        
        # Test extraction
        print("\n6️⃣ Testing extraction...")
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            extraction_result = stego.extract_data(output_audio, extract_dir)
            print(f"✅ Audio extraction successful: {extraction_result}")
            
            # Handle tuple return (content, filename)
            if isinstance(extraction_result, tuple):
                extracted_content, extracted_filename = extraction_result
            else:
                extracted_content = extraction_result
                
        except Exception as e:
            print(f"❌ Audio extraction failed: {e}")
            return False
        
        # Verify content
        print("\n7️⃣ Verifying extracted content...")
        try:
            with open(secret_file, 'r') as f:
                original_content = f.read()
            
            if original_content == extracted_content:
                print("✅ SUCCESS: Extracted content matches original!")
                print(f"📝 Original: {repr(original_content[:50])}...")
                print(f"📤 Extracted: {repr(extracted_content[:50])}...")
            else:
                print("❌ Content mismatch")
                print(f"📝 Original: {repr(original_content)}")
                print(f"📤 Extracted: {repr(extracted_content)}")
                return False
                
        except Exception as e:
            print(f"❌ Content verification failed: {e}")
            return False
        
        print("\n🎉 AUDIO STEGANOGRAPHY SUCCESS!")
        print("✅ Audio files remain playable after processing")
        print("✅ Hidden data is properly embedded and extracted")
        print("✅ No file corruption detected")
        return True

if __name__ == "__main__":
    success = test_audio_steganography()
    if success:
        print("\n🎯 Audio steganography is working without corruption!")
    else:
        print("\n❌ Audio steganography has corruption issues")
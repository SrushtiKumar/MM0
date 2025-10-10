#!/usr/bin/env python3
"""
Test password security in audio steganography
This test should demonstrate that wrong passwords fail to extract data
"""

from reliable_audio_stego import ReliableAudioSteganography
import numpy as np
import soundfile as sf
import os

def create_test_audio():
    """Create a simple test audio file"""
    # Generate 1 second of random audio
    sample_rate = 44100
    duration = 1.0
    samples = int(sample_rate * duration)
    audio_data = np.random.randint(-1000, 1000, samples, dtype=np.int16)
    
    sf.write("test_security_audio.wav", audio_data, sample_rate)
    return "test_security_audio.wav"

def test_audio_password_security():
    """Test that wrong passwords fail to extract data from audio"""
    print("🔐 Testing audio password security...")
    
    # Create test audio
    test_audio = create_test_audio()
    
    # Test with correct password
    correct_password = "correct_audio_password_123"
    secret_message = "This is a secret message hidden in audio!"
    
    print(f"\n1. Hiding data in audio with password: '{correct_password}'")
    manager_hide = ReliableAudioSteganography(password=correct_password)
    
    try:
        result = manager_hide.hide_message(test_audio, secret_message, "stego_audio.wav")
        if result:
            print(f"✅ Hide operation successful!")
        else:
            print(f"❌ Hide operation failed")
            return
    except Exception as e:
        print(f"❌ Hide operation failed: {e}")
        return
    
    # Test extraction with CORRECT password
    print(f"\n2. Extracting with CORRECT password: '{correct_password}'")
    manager_correct = ReliableAudioSteganography(password=correct_password)
    
    try:
        success, extracted_text = manager_correct.extract_message("stego_audio.wav")
        if success:
            print(f"✅ Extraction with correct password successful!")
            print(f"   Extracted: {extracted_text}")
            if secret_message == extracted_text:
                print("✅ Correct message extracted!")
            else:
                print("❌ Wrong message extracted!")
        else:
            print(f"❌ Extraction with correct password failed: {extracted_text}")
    except Exception as e:
        print(f"❌ Extraction with correct password failed: {e}")
    
    # Test extraction with WRONG passwords
    wrong_passwords = ["wrong_password", "123456", "", "different_password", "hacker_attempt"]
    
    for wrong_password in wrong_passwords:
        print(f"\n3. Testing extraction with WRONG password: '{wrong_password}'")
        manager_wrong = ReliableAudioSteganography(password=wrong_password)
        
        try:
            success, extracted_text = manager_wrong.extract_message("stego_audio.wav")
            if success:
                print(f"❌ SECURITY ISSUE: Wrong password '{wrong_password}' successfully extracted data!")
                print(f"   This should NOT happen! Extracted: {extracted_text[:50]}...")
            else:
                print(f"✅ Correct behavior: Wrong password '{wrong_password}' failed to extract: {extracted_text}")
        except Exception as e:
            print(f"✅ Correct behavior: Wrong password '{wrong_password}' failed to extract: {e}")
    
    # Cleanup
    for file in ["test_security_audio.wav", "stego_audio.wav"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    test_audio_password_security()
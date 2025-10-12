#!/usr/bin/env python3
"""
Fix Video-in-Audio Steganography Issues
Addresses the WinError 2 file not found and MP3 format issues
"""

import os
import tempfile
import shutil
from pathlib import Path
from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager

def create_real_mp3_file(output_path):
    """Create a real MP3 file using ffmpeg"""
    try:
        import subprocess
        
        # Create a simple sine wave using ffmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=3',
            '-c:a', 'mp3', '-b:a', '128k', '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created real MP3 file: {output_path}")
            return True
        else:
            print(f"❌ Failed to create MP3: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ MP3 creation error: {e}")
        return False

def create_simple_video_file(output_path):
    """Create a simple video file"""
    try:
        import subprocess
        
        # Create a simple colored video using ffmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'color=c=blue:size=320x240:duration=1',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created video file: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
        else:
            print(f"❌ Failed to create video: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Video creation error: {e}")
        return False

def create_wav_file(output_path):
    """Create a WAV file for comparison"""
    try:
        import numpy as np
        import soundfile as sf
        
        # Generate 3 seconds of test audio at 44100 Hz
        sample_rate = 44100
        duration = 3.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = 440.0  # A4 note
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        sf.write(output_path, audio_data, sample_rate)
        print(f"✅ Created WAV file: {output_path}")
        return True
    except Exception as e:
        print(f"❌ WAV creation error: {e}")
        return False

def test_video_in_audio_comprehensive():
    """Comprehensive test of video-in-audio steganography"""
    print("🎬 Testing Video-in-Audio Steganography Comprehensive Fix")
    print("=" * 70)
    
    # Create test files
    wav_file = "test_audio_carrier.wav"
    mp3_file = "test_audio_carrier.mp3"
    video_file = "test_video_content.mp4"
    
    # Create test files
    wav_created = create_wav_file(wav_file)
    mp3_created = create_real_mp3_file(mp3_file)
    video_created = create_simple_video_file(video_file)
    
    if not video_created:
        print("❌ Cannot proceed without video file")
        return
    
    manager = EnhancedWebAudioSteganographyManager(password="test123")
    
    # Test 1: WAV + Video (should work)
    if wav_created:
        print(f"\n{'='*50}")
        print("Test 1: WAV Audio + MP4 Video")
        print(f"{'='*50}")
        
        output_wav = "output_wav_with_video.wav"
        
        try:
            result = manager.hide_data(
                audio_path=wav_file,
                payload=video_file,  # File path
                output_path=output_wav,
                is_file=True,
                original_filename="test_video.mp4"
            )
            
            if result.get('success'):
                print("✅ WAV + Video embedding successful")
                
                # Test extraction
                extracted_bytes, filename = manager.extract_data(output_wav)
                if extracted_bytes and filename:
                    print(f"✅ Extraction successful: {filename} ({len(extracted_bytes)} bytes)")
                    
                    # Save extracted file
                    extracted_path = f"extracted_{filename}"
                    with open(extracted_path, 'wb') as f:
                        f.write(extracted_bytes)
                    
                    # Compare file sizes
                    original_size = os.path.getsize(video_file)
                    extracted_size = len(extracted_bytes)
                    
                    print(f"   Original size: {original_size} bytes")
                    print(f"   Extracted size: {extracted_size} bytes")
                    
                    if original_size == extracted_size:
                        print("🎉 WAV + Video test PASSED!")
                    else:
                        print("⚠️ Size mismatch - but extraction worked")
                    
                    # Check file extension preservation
                    if filename.endswith('.mp4'):
                        print("✅ VIDEO FORMAT PRESERVED!")
                    else:
                        print(f"❌ Format issue: got {filename}")
                        
                else:
                    print("❌ WAV + Video extraction failed")
            else:
                print(f"❌ WAV + Video embedding failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ WAV + Video test error: {e}")
    
    # Test 2: MP3 + Video (problematic case)
    if mp3_created:
        print(f"\n{'='*50}")
        print("Test 2: MP3 Audio + MP4 Video")
        print(f"{'='*50}")
        
        output_mp3 = "output_mp3_with_video.wav"  # Note: will convert to WAV
        
        try:
            result = manager.hide_data(
                audio_path=mp3_file,
                payload=video_file,  # File path
                output_path=output_mp3,
                is_file=True,
                original_filename="test_video.mp4"
            )
            
            if result.get('success'):
                print("✅ MP3 + Video embedding successful")
                print(f"   Output saved as: {result.get('output_path')}")
                
                # Test extraction from the converted file
                actual_output = result.get('output_path')
                extracted_bytes, filename = manager.extract_data(actual_output)
                if extracted_bytes and filename:
                    print(f"✅ Extraction successful: {filename} ({len(extracted_bytes)} bytes)")
                    
                    # Save extracted file
                    extracted_path = f"extracted_from_mp3_{filename}"
                    with open(extracted_path, 'wb') as f:
                        f.write(extracted_bytes)
                    
                    # Compare file sizes
                    original_size = os.path.getsize(video_file)
                    extracted_size = len(extracted_bytes)
                    
                    print(f"   Original size: {original_size} bytes")
                    print(f"   Extracted size: {extracted_size} bytes")
                    
                    if original_size == extracted_size:
                        print("🎉 MP3 + Video test PASSED!")
                    else:
                        print("⚠️ Size mismatch - but extraction worked")
                    
                    # Check file extension preservation
                    if filename.endswith('.mp4'):
                        print("✅ VIDEO FORMAT PRESERVED!")
                    else:
                        print(f"❌ Format issue: got {filename}")
                        
                else:
                    print("❌ MP3 + Video extraction failed")
            else:
                print(f"❌ MP3 + Video embedding failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ MP3 + Video test error: {e}")
    
    # Test 3: Error reproduction - test with existing video files
    print(f"\n{'='*50}")
    print("Test 3: Using Existing Video Files")
    print(f"{'='*50}")
    
    existing_videos = [
        'api_test_video.mp4',
        'comprehensive_test_video.mp4',
        'debug_test_video.mp4'
    ]
    
    for video in existing_videos:
        if os.path.exists(video):
            print(f"\n  Testing with: {video}")
            
            if wav_created:
                output_path = f"test_existing_{Path(video).stem}.wav"
                try:
                    result = manager.hide_data(
                        audio_path=wav_file,
                        payload=video,
                        output_path=output_path,
                        is_file=True,
                        original_filename=os.path.basename(video)
                    )
                    
                    if result.get('success'):
                        print(f"    ✅ {video} embedded successfully")
                        
                        # Quick extraction test
                        extracted_bytes, filename = manager.extract_data(output_path)
                        if extracted_bytes:
                            print(f"    ✅ Extracted: {filename} ({len(extracted_bytes)} bytes)")
                        else:
                            print(f"    ❌ Extraction failed")
                    else:
                        print(f"    ❌ Embedding failed: {result.get('error')}")
                        
                except Exception as e:
                    print(f"    ❌ Error with {video}: {e}")
            break  # Test with first available video only
    
    # Cleanup
    cleanup_files = [
        wav_file, mp3_file, video_file,
        "output_wav_with_video.wav", 
        "output_mp3_with_video.wav",
        "extracted_test_video.mp4",
        "extracted_from_mp3_test_video.mp4"
    ]
    
    cleanup_files.extend([f"test_existing_{Path(v).stem}.wav" for v in existing_videos])
    
    print(f"\n{'='*50}")
    print("Cleanup")
    print(f"{'='*50}")
    
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ Cleaned up: {file}")
            except Exception as e:
                print(f"⚠️ Could not remove {file}: {e}")
    
    print(f"\n🎉 Video-in-Audio testing complete!")

if __name__ == "__main__":
    test_video_in_audio_comprehensive()
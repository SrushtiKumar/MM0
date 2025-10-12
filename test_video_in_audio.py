#!/usr/bin/env python3
"""
Test Video File Hidden in Audio File
Reproduces the specific error with video files in audio carriers
"""
import os
import tempfile
from pathlib import Path

def create_test_files():
    """Create test video and audio files"""
    print("📁 Creating test files for video-in-audio test...")
    
    # Create test MP3 audio carrier
    audio_file = "test_audio_carrier.mp3"
    if not os.path.exists(audio_file):
        # Create a basic MP3 file content
        mp3_content = b'\xff\xfb\x90\x00' + b'\x00' * 8000  # Basic MP3 header + data
        with open(audio_file, 'wb') as f:
            f.write(mp3_content)
        print(f"  Created test MP3: {audio_file}")
    
    # Create test WAV audio carrier
    wav_file = "test_audio_carrier.wav"
    if not os.path.exists(wav_file):
        # Create a proper WAV file
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        wav_data = b'\x00\x00' * 4096  # 4KB of silence
        with open(wav_file, 'wb') as f:
            f.write(wav_header + wav_data)
        print(f"  Created test WAV: {wav_file}")
    
    # Create test video file (small MP4)
    video_file = "test_video_content.mp4"
    if not os.path.exists(video_file):
        # Create a minimal MP4 file structure
        mp4_content = (
            b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'  # ftyp box
            b'\x00\x00\x00\x08free'  # free box
            + b'Test video content for audio steganography' + b'\x00' * 100
        )
        with open(video_file, 'wb') as f:
            f.write(mp4_content)
        print(f"  Created test MP4: {video_file}")
    
    return audio_file, wav_file, video_file

def test_video_in_audio_direct():
    """Test hiding video in audio using direct API"""
    print("\n🎵➡️📹 Testing Video File Hidden in Audio File")
    print("=" * 60)
    
    # Create test files
    mp3_file, wav_file, video_file = create_test_files()
    
    try:
        from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager
        
        # Test 1: Hide video in WAV
        print(f"\n📹 Test 1: Hide MP4 video in WAV audio")
        print("-" * 40)
        
        manager = EnhancedWebAudioSteganographyManager(password="test123")
        
        # Read video content as bytes
        with open(video_file, 'rb') as f:
            video_bytes = f.read()
        
        print(f"  Video file size: {len(video_bytes)} bytes")
        print(f"  Hiding {video_file} in {wav_file}")
        
        # Hide video file with original filename
        result1 = manager.hide_data(
            wav_file,
            video_bytes,
            "audio_with_video.wav",
            is_file=True,
            original_filename="test_video_content.mp4"
        )
        
        if result1.get('success'):
            print("✅ Video embedding in WAV successful")
            print(f"  Result: {result1.get('message', '')}")
            print(f"  Output: {result1.get('output_path', 'audio_with_video.wav')}")
            
            # Check if output file exists
            expected_output = result1.get('output_path', 'audio_with_video.wav')
            if os.path.exists(expected_output):
                print(f"  ✅ Output file exists: {expected_output}")
                print(f"  📊 Output file size: {os.path.getsize(expected_output)} bytes")
                
                # Try extraction
                print(f"\n  📤 Extracting video from {expected_output}...")
                extracted_data, extracted_filename = manager.extract_data(expected_output)
                
                if extracted_data and extracted_filename:
                    print(f"  📥 Extracted: {extracted_filename}")
                    print(f"  📊 Extracted size: {len(extracted_data)} bytes")
                    
                    if extracted_filename.endswith('.mp4'):
                        print("  ✅ VIDEO FORMAT PRESERVED!")
                        
                        # Save extracted video
                        with open(f"extracted_{extracted_filename}", 'wb') as f:
                            f.write(extracted_data)
                        print(f"  💾 Saved: extracted_{extracted_filename}")
                    else:
                        print(f"  ❌ VIDEO format not preserved: {extracted_filename}")
                else:
                    print(f"  ❌ Video extraction failed")
            else:
                print(f"  ❌ Output file not found: {expected_output}")
                # List files in current directory to see what was created
                print(f"  📁 Files in current directory:")
                for f in os.listdir('.'):
                    if 'audio' in f.lower() or 'wav' in f.lower():
                        print(f"    - {f}")
        else:
            print(f"❌ Video embedding failed: {result1.get('error', 'Unknown error')}")
        
        # Test 2: Hide video in MP3
        print(f"\n📹 Test 2: Hide MP4 video in MP3 audio")
        print("-" * 40)
        
        print(f"  Hiding {video_file} in {mp3_file}")
        
        # Hide video file in MP3
        result2 = manager.hide_data(
            mp3_file,
            video_bytes,
            "audio_with_video.mp3",
            is_file=True,
            original_filename="test_video_content.mp4"
        )
        
        if result2.get('success'):
            print("✅ Video embedding in MP3 successful")
            print(f"  Result: {result2.get('message', '')}")
            print(f"  Output: {result2.get('output_path', 'audio_with_video.mp3')}")
            
            # Check if output file exists
            expected_output2 = result2.get('output_path', 'audio_with_video.mp3')
            if os.path.exists(expected_output2):
                print(f"  ✅ Output file exists: {expected_output2}")
                print(f"  📊 Output file size: {os.path.getsize(expected_output2)} bytes")
                
                # Note: MP3 steganography converts to WAV, so the output might be WAV
                if expected_output2.endswith('.wav'):
                    print("  ℹ️  MP3 converted to WAV for LSB steganography")
            else:
                print(f"  ❌ Output file not found: {expected_output2}")
                # Check for WAV version (MP3 gets converted to WAV)
                wav_version = expected_output2.replace('.mp3', '.wav')
                if os.path.exists(wav_version):
                    print(f"  ✅ Found WAV version: {wav_version}")
                else:
                    print(f"  ❌ Neither MP3 nor WAV version found")
        else:
            print(f"❌ Video embedding in MP3 failed: {result2.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Audio steganography module not available: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print("🎯 VIDEO-IN-AUDIO TEST COMPLETE")
    print("If any errors occurred, they should be visible above.")
    print("=" * 60)

if __name__ == "__main__":
    test_video_in_audio_direct()
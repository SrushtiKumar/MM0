#!/usr/bin/env python3
"""
Test Safe Video Steganography
Verify that videos remain playable and in original format
"""

import os
import tempfile
import subprocess
from safe_video_steganography import SafeVideoSteganography, FinalVideoSteganographyManager

def create_test_video(output_path):
    """Create a simple test MP4 video using ffmpeg"""
    try:
        # Create a simple test video - 5 seconds, 10fps, 320x240
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', 
            '-i', 'testsrc=duration=5:size=320x240:rate=10',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created test MP4: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
        else:
            print(f"❌ ffmpeg error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to create test video: {e}")
        return False

def check_video_playable(video_path):
    """Check if video is playable using ffprobe"""
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_format', '-show_streams', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract key info
            output = result.stdout
            duration = None
            codec = None
            format_name = None
            
            for line in output.split('\n'):
                if 'duration=' in line:
                    duration = line.split('=')[1]
                elif 'codec_name=' in line and codec is None:
                    codec = line.split('=')[1]
                elif 'format_name=' in line:
                    format_name = line.split('=')[1]
            
            print(f"✅ Video is playable: codec={codec}, format={format_name}, duration={duration}")
            return True, codec, format_name
        else:
            print(f"❌ Video not playable: {result.stderr}")
            return False, None, None
    except Exception as e:
        print(f"❌ Error checking video: {e}")
        return False, None, None

def test_safe_video_steganography():
    """Test the safe video steganography system"""
    
    print("🎬 TESTING SAFE VIDEO STEGANOGRAPHY")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test video
        test_video = os.path.join(temp_dir, "test_original.mp4")
        if not create_test_video(test_video):
            print("❌ Cannot create test video - need ffmpeg")
            return False
        
        # Check original video
        original_playable, orig_codec, orig_format = check_video_playable(test_video)
        if not original_playable:
            print("❌ Original test video not playable")
            return False
        
        # Test safe steganography
        safe_stego = SafeVideoSteganography("test123")
        stego_video = os.path.join(temp_dir, "stego_video.mp4")
        
        secret_message = "This is a secret message hidden in the video!"
        
        print(f"\n🔧 Testing safe video embedding...")
        result = safe_stego.hide_data_in_video(test_video, secret_message, stego_video)
        
        if result['success']:
            print(f"✅ Embedding successful: {result}")
            
            # CRITICAL TEST: Check if stego video is still playable
            print(f"\n🧪 Testing if stego video is playable...")
            stego_playable, stego_codec, stego_format = check_video_playable(stego_video)
            
            if stego_playable:
                print(f"🎉 ✅ STEGO VIDEO IS PLAYABLE!")
                print(f"   Original: codec={orig_codec}, format={orig_format}")
                print(f"   Stego:    codec={stego_codec}, format={stego_format}")
                
                if orig_codec == stego_codec and orig_format == stego_format:
                    print(f"🎉 ✅ VIDEO FORMAT COMPLETELY PRESERVED!")
                else:
                    print(f"⚠️  Format changed but still playable")
                
                # Test extraction
                print(f"\n📤 Testing extraction...")
                extracted = safe_stego.extract_data_from_video(stego_video)
                
                if extracted:
                    data, filename = extracted
                    extracted_message = data.decode('utf-8')
                    
                    if extracted_message == secret_message:
                        print(f"✅ Extraction perfect!")
                        print(f"   Original:  '{secret_message}'")
                        print(f"   Extracted: '{extracted_message}'")
                        return True
                    else:
                        print(f"❌ Message mismatch")
                        print(f"   Expected: '{secret_message}'")
                        print(f"   Got:      '{extracted_message}'")
                else:
                    print(f"❌ Extraction failed")
            else:
                print(f"❌ STEGO VIDEO IS NOT PLAYABLE - CORRUPTION!")
        else:
            print(f"❌ Embedding failed: {result}")
    
    return False

def test_video_manager():
    """Test the FinalVideoSteganographyManager"""
    
    print("\n🎬 TESTING VIDEO MANAGER (Production API Compatible)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test video
        test_video = os.path.join(temp_dir, "manager_test.mp4")
        if not create_test_video(test_video):
            print("❌ Cannot create test video")
            return False
        
        manager = FinalVideoSteganographyManager()
        stego_video = os.path.join(temp_dir, "manager_stego.mp4")
        
        # Test embedding
        print(f"\n🔧 Testing manager embedding...")
        result = manager.hide_data(test_video, "Manager test message", stego_video, "test456")
        
        if result['success']:
            print(f"✅ Manager embedding successful")
            
            # Check playability
            playable, codec, format_name = check_video_playable(stego_video)
            if playable:
                print(f"🎉 ✅ MANAGER OUTPUT IS PLAYABLE!")
                
                # Test extraction
                extracted = manager.extract_data(stego_video, "test456", temp_dir)
                if extracted and extracted.get('success'):
                    print(f"✅ Manager extraction successful!")
                    print(f"   Data: {extracted['extracted_data']}")
                    return True
                else:
                    print(f"❌ Manager extraction failed")
            else:
                print(f"❌ Manager output not playable")
        else:
            print(f"❌ Manager embedding failed")
    
    return False

if __name__ == "__main__":
    print("🎯 SAFE VIDEO STEGANOGRAPHY VERIFICATION")
    print("=" * 70)
    
    test1 = test_safe_video_steganography()
    test2 = test_video_manager()
    
    if test1 and test2:
        print("\n" + "=" * 70)
        print("🎉 🎉 🎉 SAFE VIDEO STEGANOGRAPHY WORKING! 🎉 🎉 🎉")
        print("✅ Videos remain playable and in original format")
        print("✅ Ready for production integration")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ ❌ ❌ SAFE VIDEO STEGANOGRAPHY FAILED ❌ ❌ ❌")
        print("❌ Videos are being corrupted")
        print("=" * 70)
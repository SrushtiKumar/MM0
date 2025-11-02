"""
Direct Module Test - Verify Steganography Modules Work Correctly
"""
from universal_file_audio import UniversalFileAudio
from final_video_steganography import VideoSteganography
import os

def test_direct_modules():
    print("🔧 DIRECT MODULE TESTING")
    print("=" * 40)
    
    # Test 1: Audio steganography filename preservation
    print("\n1. Testing audio module directly...")
    try:
        manager = UniversalFileAudio(password='test123')
        
        # Create test Python file
        with open('module_test.py', 'w') as f:
            f.write('#!/usr/bin/env python3\nprint("Hello from module test!")\n')
        
        # Read files
        with open('test_audio.wav', 'rb') as carrier:
            carrier_data = carrier.read()
        with open('module_test.py', 'rb') as content:
            content_data = content.read()
        
        # Embed using module directly
        result = manager.hide_data(carrier_data, content_data, 'module_test.py')
        
        # Save result
        with open('module_test_output.wav', 'wb') as f:
            f.write(result)
        
        print("✅ Direct embedding successful")
        
        # Extract using module directly
        with open('module_test_output.wav', 'rb') as f:
            stego_data = f.read()
        
        extracted_data, extracted_filename = manager.extract_data(stego_data)
        
        print(f"📄 Extracted filename: {extracted_filename}")
        
        if extracted_filename and extracted_filename.endswith('.py'):
            print("🎯 SUCCESS: Audio module preserves .py extension!")
        elif extracted_filename and extracted_filename.endswith('.txt'):
            print("❌ FAILED: Audio module still converts to .txt")
        else:
            print(f"❓ Unexpected result: {extracted_filename}")
            
    except Exception as e:
        print(f"❌ Audio module test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Video steganography (should already work perfectly)  
    print("\n2. Testing video module directly...")
    try:
        manager = VideoSteganography(password='test123')
        
        # Use existing video file
        video_files = ['test_video.mp4', 'clean_carrier.mp4', 'comprehensive_test_video.mp4']
        video_file = None
        for vf in video_files:
            if os.path.exists(vf):
                video_file = vf
                break
        
        if video_file:
            # Read files
            with open(video_file, 'rb') as carrier:
                carrier_data = carrier.read()
            with open('module_test.py', 'rb') as content:
                content_data = content.read()
            
            # Embed
            result = manager.hide_data(carrier_data, content_data, 'module_test.py')
            
            # Save
            with open('module_video_test.mp4', 'wb') as f:
                f.write(result)
            
            print("✅ Video direct embedding successful")
            
            # Extract
            with open('module_video_test.mp4', 'rb') as f:
                stego_data = f.read()
            
            extracted_data, extracted_filename = manager.extract_data(stego_data)
            
            print(f"📄 Video extracted filename: {extracted_filename}")
            
            if extracted_filename and extracted_filename.endswith('.py'):
                print("🎯 SUCCESS: Video module preserves .py extension!")
            else:
                print(f"❓ Video result: {extracted_filename}")
        else:
            print("❌ No video file available for testing")
            
    except Exception as e:
        print(f"❌ Video module test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("🏁 DIRECT MODULE TEST COMPLETE")
    print("=" * 40)

if __name__ == "__main__":
    test_direct_modules()
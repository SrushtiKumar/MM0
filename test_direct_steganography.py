#!/usr/bin/env python3
"""
Direct test of steganography modules without web server
"""

import os
import sys

def test_video_steganography():
    """Test video steganography directly"""
    print("🎬 Testing Video Steganography Core Functionality")
    print("=" * 50)
    
    try:
        from final_video_steganography import FinalVideoSteganographyManager
        
        if not os.path.exists('clean_carrier.mp4'):
            print("❌ clean_carrier.mp4 not found")
            return False
            
        # Create manager
        manager = FinalVideoSteganographyManager(password="test123")
        print("✅ Video manager created successfully")
        
        # Test embedding
        print("📥 Testing video embedding...")
        message = "Hello, this is a test message for video steganography!"
        
        try:
            output_filename = "test_video_output.mp4"
            result = manager.hide_data(
                video_path="clean_carrier.mp4",
                payload=message,
                output_path=output_filename
            )
            print(f"✅ Video embedding completed: {output_filename}")
            
            # Test extraction
            if os.path.exists(output_filename):
                print("📤 Testing video extraction...")
                extracted = manager.extract_data(output_filename)
                
                if extracted == message:
                    print("✅ Video extraction successful - messages match!")
                    return True
                else:
                    print(f"❌ Message mismatch. Expected: '{message}', Got: '{extracted}'")
                    return False
            else:
                print("❌ Output video file not created")
                return False
                
        except Exception as e:
            print(f"❌ Video steganography failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Cannot import video steganography: {e}")
        return False

def test_audio_steganography():
    """Test audio steganography directly"""
    print("\n🔊 Testing Audio Steganography Core Functionality")
    print("=" * 50)
    
    try:
        from universal_file_audio import UniversalFileAudio
        
        # Find an audio file
        audio_file = None
        for filename in ['audio_with_hidden_doc.wav', 'direct_test_audio.wav']:
            if os.path.exists(filename):
                audio_file = filename
                break
        
        if not audio_file:
            print("❌ No audio file found for testing")
            return False
            
        print(f"📁 Using audio file: {audio_file}")
        
        # Create manager
        manager = UniversalFileAudio()
        print("✅ Audio manager created successfully")
        
        # Test embedding - audio manager might work with files differently
        print("📥 Testing audio file embedding...")
        
        # Create a test text file to hide
        test_file = "test_message.txt"
        with open(test_file, "w") as f:
            f.write("Hello from audio steganography test!")
        
        try:
            output_filename = "test_audio_output.wav"
            manager.embed_file(
                audio_path=audio_file,
                file_path=test_file,
                output_path=output_filename
            )
            print(f"✅ Audio embedding completed: {output_filename}")
            
            # Test extraction
            if os.path.exists(output_filename):
                print("📤 Testing audio extraction...")
                extracted_file = manager.extract_file(output_filename, "extracted_from_audio")
                
                if extracted_file and os.path.exists(extracted_file):
                    print(f"✅ Audio extraction successful: {extracted_file}")
                    return True
                else:
                    print("❌ Audio extraction failed - no file extracted")
                    return False
            else:
                print("❌ Output audio file not created")
                return False
                
        except Exception as e:
            print(f"❌ Audio steganography failed: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
            
    except ImportError as e:
        print(f"❌ Cannot import audio steganography: {e}")
        return False

def test_image_steganography():
    """Test image steganography directly"""
    print("\n🖼️ Testing Image Steganography Core Functionality")
    print("=" * 50)
    
    try:
        from universal_file_steganography import UniversalFileSteganography
        
        # Look for image files
        image_file = None
        for ext in ['png', 'jpg', 'jpeg', 'bmp']:
            for filename in os.listdir('.'):
                if filename.lower().endswith(f'.{ext}'):
                    image_file = filename
                    break
            if image_file:
                break
        
        if not image_file:
            print("❌ No image file found for testing")
            return False
            
        print(f"📁 Using image file: {image_file}")
        
        # Create manager
        manager = UniversalFileSteganography(password="test123")
        print("✅ Image manager created successfully")
        
        # Test embedding
        print("📥 Testing image embedding...")
        
        # Create a test file to hide
        test_file = "test_image_message.txt"
        with open(test_file, "w") as f:
            f.write("Hello from image steganography test!")
        
        try:
            output_filename = "test_image_output.png"
            result = manager.hide_file_in_file(
                container_path=image_file,
                secret_file_path=test_file,
                output_path=output_filename
            )
            print(f"✅ Image embedding completed: {output_filename}")
            
            # Test extraction
            if os.path.exists(output_filename):
                print("📤 Testing image extraction...")
                extracted_file = manager.extract_file_from_file(
                    stego_file_path=output_filename,
                    output_dir="."
                )
                
                if extracted_file and os.path.exists(extracted_file):
                    print(f"✅ Image extraction successful: {extracted_file}")
                    return True
                else:
                    print("❌ Image extraction failed - no file extracted")
                    return False
            else:
                print("❌ Output image file not created")
                return False
                
        except Exception as e:
            print(f"❌ Image steganography failed: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
            
    except ImportError as e:
        print(f"❌ Cannot import image steganography: {e}")
        return False

def main():
    """Test all steganography modules directly"""
    print("🧪 Direct Steganography Module Testing")
    print("=" * 60)
    print("Testing core functionality without web server...")
    print()
    
    results = []
    results.append(("Video", test_video_steganography()))
    results.append(("Audio", test_audio_steganography()))
    results.append(("Image", test_image_steganography()))
    
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall Result: {passed}/{total} core tests passed")
    
    if passed == total:
        print("🎉 All steganography modules are working correctly!")
        print("The issue is likely in the web server configuration, not the core functionality.")
    elif passed > 0:
        print("⚠️ Some steganography modules are working. Check the failing ones.")
    else:
        print("❌ No steganography modules are working. Check implementations.")

if __name__ == "__main__":
    main()
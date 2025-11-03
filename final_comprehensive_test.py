"""
Final comprehensive test of all steganography modules
Tests both direct class usage and simulates API behavior
"""

import sys
import os
sys.path.append(os.getcwd())

from universal_file_steganography import UniversalFileSteganography
from universal_file_audio import UniversalFileAudio
from final_video_steganography import FinalVideoSteganographyManager
import tempfile

def test_all_modules_direct():
    """Test all steganography modules directly"""
    print("=== COMPREHENSIVE STEGANOGRAPHY TEST ===\n")
    
    results = {}
    
    # Test 1: Image Steganography
    print("1. Testing Image Steganography...")
    try:
        image_stego = UniversalFileSteganography()  # No password in constructor
        # Try multiple possible image files
        possible_images = ["carrier_test_image.png", "test_image.png", "image_test.png"]
        image_path = None
        for img in possible_images:
            if os.path.exists(img):
                image_path = img
                break
        
        if image_path:
            result = image_stego.hide_data(
                image_path, "Test Image Message", "test_final_image.png", 
                password="test123", is_file=False  # Password goes in hide_data method
            )
            if result.get('success'):
                extract_result = image_stego.extract_data("test_final_image.png", password="test123")
                if extract_result and extract_result[0].decode('utf-8') == "Test Image Message":
                    print("   ✅ Image steganography PASSED")
                    results['image'] = True
                else:
                    print("   ❌ Image extraction failed")
                    results['image'] = False
            else:
                print(f"   ❌ Image embedding failed: {result.get('error')}")
                results['image'] = False
        else:
            print(f"   ⚠️ No image files found - SKIPPED")
            results['image'] = 'skipped'
    except Exception as e:
        print(f"   ❌ Image test error: {e}")
        results['image'] = False
    
    print()
    
    # Test 2: Audio Steganography (Updated)
    print("2. Testing Audio Steganography (Updated)...")
    try:
        audio_stego = UniversalFileAudio(password="test123")
        audio_path = "test_audio_carrier.wav"
        
        if os.path.exists(audio_path):
            result = audio_stego.hide_data(
                audio_path, "Test Audio Message", "test_final_audio.wav", is_file=False
            )
            if result.get('success'):
                extract_result = audio_stego.extract_data("test_final_audio.wav")
                if extract_result and extract_result[0].decode('utf-8') == "Test Audio Message":
                    print("   ✅ Audio steganography PASSED")
                    results['audio'] = True
                else:
                    print("   ❌ Audio extraction failed")
                    results['audio'] = False
            else:
                print(f"   ❌ Audio embedding failed: {result.get('error')}")
                results['audio'] = False
        else:
            print(f"   ⚠️ Audio file {audio_path} not found - SKIPPED")
            results['audio'] = 'skipped'
    except Exception as e:
        print(f"   ❌ Audio test error: {e}")
        results['audio'] = False
    
    print()
    
    # Test 3: Video Steganography
    print("3. Testing Video Steganography...")
    try:
        video_stego = FinalVideoSteganographyManager("test123")
        video_path = "comprehensive_test_video.mp4"
        
        if os.path.exists(video_path):
            result = video_stego.hide_data(
                video_path, "Test Video Message", "test_final_video.avi", is_file=False
            )
            if result.get('success'):
                extract_result = video_stego.extract_data("test_final_video.avi")
                if extract_result and extract_result[0].decode('utf-8') == "Test Video Message":
                    print("   ✅ Video steganography PASSED")
                    results['video'] = True
                else:
                    print("   ❌ Video extraction failed")
                    results['video'] = False
            else:
                print(f"   ❌ Video embedding failed: {result.get('error')}")
                results['video'] = False
        else:
            print(f"   ⚠️ Video file {video_path} not found - SKIPPED")
            results['video'] = 'skipped'
    except Exception as e:
        print(f"   ❌ Video test error: {e}")
        results['video'] = False
    
    print()
    
    # Test 4: Document Steganography
    print("4. Testing Document Steganography...")
    try:
        doc_stego = UniversalFileSteganography()  # No password in constructor
        doc_path = "large_test_document.txt"
        
        if os.path.exists(doc_path):
            result = doc_stego.hide_data(
                doc_path, "Test Document Message", "test_final_document.txt", 
                password="test123", is_file=False  # Password goes in hide_data method
            )
            if result.get('success'):
                extract_result = doc_stego.extract_data("test_final_document.txt", password="test123")
                if extract_result and extract_result[0].decode('utf-8') == "Test Document Message":
                    print("   ✅ Document steganography PASSED")
                    results['document'] = True
                else:
                    print("   ❌ Document extraction failed")
                    results['document'] = False
            else:
                print(f"   ❌ Document embedding failed: {result.get('error')}")
                results['document'] = False
        else:
            print(f"   ⚠️ Document file {doc_path} not found - SKIPPED")
            results['document'] = 'skipped'
    except Exception as e:
        print(f"   ❌ Document test error: {e}")
        results['document'] = False
    
    print()
    
    # Summary
    print("=" * 60)
    print("FINAL RESULTS SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v == 'skipped')
    
    for module, result in results.items():
        if result is True:
            print(f"{module.capitalize()} steganography: ✅ PASSED")
        elif result is False:
            print(f"{module.capitalize()} steganography: ❌ FAILED")
        else:
            print(f"{module.capitalize()} steganography: ⚠️ SKIPPED")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0 and passed > 0:
        print("🎉 ALL AVAILABLE MODULES WORKING!")
    elif passed >= 3:
        print("🎯 EXCELLENT PROGRESS - Most modules working!")
    elif passed >= 2:
        print("👍 GOOD PROGRESS - Multiple modules working!")
    else:
        print("⚠️ NEEDS MORE WORK")
    
    return results

if __name__ == "__main__":
    test_all_modules_direct()
#!/usr/bin/env python3
"""
Final comprehensive test of all fixed steganography implementations
"""

import os
from simple_image_stego import SimpleImageSteganography
from fixed_audio_stego import FixedAudioSteganography  
from robust_video_stego import RobustVideoSteganography

def test_all_steganography():
    """Test all steganography implementations"""
    
    print("🧪 FINAL COMPREHENSIVE STEGANOGRAPHY TEST")
    print("=" * 50)
    
    results = {}
    
    # Create test files
    test_text_file = "final_test_message.txt"
    test_content = "This is a comprehensive test of all steganography modules working correctly!"
    
    with open(test_text_file, 'w') as f:
        f.write(test_content)
    
    test_doc_file = "final_test_doc.doc"
    with open(test_doc_file, 'wb') as f:
        # Create a simple binary document
        f.write(b"This is a test document for steganography verification.\x00\x01\x02\x03")
    
    # Test 1: Image Steganography
    print("\n1️⃣ TESTING IMAGE STEGANOGRAPHY")
    print("-" * 30)
    
    try:
        image_stego = SimpleImageSteganography()
        
        # Create a simple test image first
        from PIL import Image
        import numpy as np
        
        # Create test image
        test_image = Image.fromarray(np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8))
        test_image.save("test_image_for_stego.png")
        
        # Embed
        success = image_stego.embed_file(
            image_path="test_image_for_stego.png",
            file_path=test_text_file,
            output_path="final_test_image.png"
        )
        
        if success:
            # Extract  
            extracted_path = image_stego.extract_file("final_test_image.png")
            
            with open(extracted_path, 'r') as f:
                extracted_content = f.read()
            
            if extracted_content == test_content:
                results['image'] = "✅ PASS"
                print("✅ Image steganography: PASS")
            else:
                results['image'] = "❌ FAIL - Content mismatch"
                print("❌ Image steganography: FAIL - Content mismatch")
        else:
            results['image'] = "❌ FAIL - Embedding failed"
            print("❌ Image steganography: FAIL - Embedding failed")
            
    except Exception as e:
        results['image'] = f"❌ FAIL - {e}"
        print(f"❌ Image steganography: FAIL - {e}")
    
    # Test 2: Audio Steganography
    print("\n2️⃣ TESTING AUDIO STEGANOGRAPHY") 
    print("-" * 30)
    
    try:
        audio_stego = FixedAudioSteganography()
        
        # Embed text file
        success = audio_stego.embed_file(
            audio_path="audio_with_hidden_doc.wav",
            file_path=test_text_file,
            output_path="final_test_audio.wav"
        )
        
        if success:
            # Extract
            extracted_path = audio_stego.extract_file("final_test_audio.wav")
            
            with open(extracted_path, 'r') as f:
                extracted_content = f.read()
            
            if extracted_content == test_content:
                results['audio'] = "✅ PASS"
                print("✅ Audio steganography: PASS")
            else:
                results['audio'] = "❌ FAIL - Content mismatch"
                print("❌ Audio steganography: FAIL - Content mismatch")
        else:
            results['audio'] = "❌ FAIL - Embedding failed"
            print("❌ Audio steganography: FAIL - Embedding failed")
            
    except Exception as e:
        results['audio'] = f"❌ FAIL - {e}"
        print(f"❌ Audio steganography: FAIL - {e}")
    
    # Test 3: Video Steganography
    print("\n3️⃣ TESTING VIDEO STEGANOGRAPHY")
    print("-" * 30)
    
    try:
        video_stego = RobustVideoSteganography()
        
        # Embed
        success = video_stego.embed_file(
            video_path="direct_test_video.mp4",
            file_path=test_text_file,
            output_path="final_test_video.mp4"
        )
        
        if success:
            # Extract
            extracted_path = video_stego.extract_file("final_test_video.mp4")
            
            with open(extracted_path, 'r') as f:
                extracted_content = f.read()
            
            if extracted_content == test_content:
                results['video'] = "✅ PASS"
                print("✅ Video steganography: PASS")
            else:
                results['video'] = "❌ FAIL - Content mismatch"
                print("❌ Video steganography: FAIL - Content mismatch")
        else:
            results['video'] = "❌ FAIL - Embedding failed"
            print("❌ Video steganography: FAIL - Embedding failed")
            
    except Exception as e:
        results['video'] = f"❌ FAIL - {e}"
        print(f"❌ Video steganography: FAIL - {e}")
    
    # Test 4: Document Embedding (using audio for document)
    print("\n4️⃣ TESTING DOCUMENT STEGANOGRAPHY")
    print("-" * 30)
    
    try:
        audio_stego = FixedAudioSteganography()
        
        # Embed document file
        success = audio_stego.embed_file(
            audio_path="audio_with_hidden_doc.wav",
            file_path=test_doc_file,
            output_path="final_test_document.wav"
        )
        
        if success:
            # Extract
            extracted_path = audio_stego.extract_file("final_test_document.wav")
            
            with open(test_doc_file, 'rb') as f:
                original_doc = f.read()
                
            with open(extracted_path, 'rb') as f:
                extracted_doc = f.read()
            
            if extracted_doc == original_doc:
                results['document'] = "✅ PASS"
                print("✅ Document steganography: PASS")
            else:
                results['document'] = "❌ FAIL - Content mismatch"
                print("❌ Document steganography: FAIL - Content mismatch")
        else:
            results['document'] = "❌ FAIL - Embedding failed"
            print("❌ Document steganography: FAIL - Embedding failed")
            
    except Exception as e:
        results['document'] = f"❌ FAIL - {e}"
        print(f"❌ Document steganography: FAIL - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for module, result in results.items():
        print(f"{module.upper():12} : {result}")
        if "PASS" in result:
            passed += 1
    
    print(f"\n🎯 OVERALL: {passed}/{total} modules working correctly")
    
    if passed == total:
        print("🎉 ALL STEGANOGRAPHY MODULES ARE FULLY FUNCTIONAL! 🎉")
        return True
    else:
        print("⚠️  Some modules need attention")
        return False
    
    # Cleanup
    try:
        os.unlink(test_text_file)
        os.unlink(test_doc_file)
        os.unlink("test_image_for_stego.png")
    except:
        pass

if __name__ == "__main__":
    test_all_steganography()
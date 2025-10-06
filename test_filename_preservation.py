#!/usr/bin/env python3
"""
Test file extension preservation in audio steganography
"""

import os
from final_audio_stego import FinalAudioSteganographyManager

def test_filename_preservation():
    """Test that file extensions are preserved correctly."""
    print("=== Testing Filename Preservation ===")
    
    # Create test files
    test_files = {
        "test.pdf": b"PDF content here",
        "test.docx": b"DOCX content here", 
        "test.jpg": b"JPG content here",
        "test.txt": b"TXT content here"
    }
    
    # Create test files
    for filename, content in test_files.items():
        with open(filename, 'wb') as f:
            f.write(content)
        print(f"Created test file: {filename}")
    
    # Use existing audio file
    audio_file = "demo_audio.wav"
    if not os.path.exists(audio_file):
        print(f"❌ Audio file {audio_file} not found")
        return False
    
    # Test embedding and extraction
    manager = FinalAudioSteganographyManager("test123")
    
    success_count = 0
    total_tests = len(test_files)
    
    for filename, original_content in test_files.items():
        try:
            print(f"\n--- Testing {filename} ---")
            
            # Embed
            output_audio = f"stego_{filename}.wav"
            result = manager.hide_data(audio_file, filename, output_audio, is_file=True)
            print(f"Embed result: {result}")
            
            # Extract
            extracted_data, extracted_filename = manager.extract_data(output_audio)
            
            print(f"Original filename: {filename}")
            print(f"Extracted filename: {extracted_filename}")
            print(f"Content match: {'✅' if extracted_data == original_content else '❌'}")
            print(f"Filename match: {'✅' if extracted_filename == filename else '❌'}")
            
            if extracted_data == original_content and extracted_filename == filename:
                success_count += 1
                print(f"✅ {filename} test PASSED")
            else:
                print(f"❌ {filename} test FAILED")
            
            # Cleanup
            if os.path.exists(output_audio):
                os.unlink(output_audio)
                
        except Exception as e:
            print(f"❌ {filename} test FAILED with error: {e}")
    
    # Cleanup test files
    for filename in test_files.keys():
        if os.path.exists(filename):
            os.unlink(filename)
    
    print(f"\n=== Results ===")
    print(f"Passed: {success_count}/{total_tests}")
    print(f"Success rate: {success_count/total_tests*100:.1f}%")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = test_filename_preservation()
    print(f"\n🎉 Overall test {'PASSED' if success else 'FAILED'}!")
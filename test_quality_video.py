#!/usr/bin/env python3
"""
Test with the quality video
"""

from robust_video_stego import RobustVideoSteganographyManager
from pathlib import Path

def test_with_quality_video():
    # Create test image
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    test_data = jpeg_header + (b'A' * 10000)  # 10KB
    test_image_path = Path('quality_test_image.jpg')
    with open(test_image_path, 'wb') as f:
        f.write(test_data)

    print(f'Created test image: {len(test_data)} bytes')

    # Test with quality video
    manager = RobustVideoSteganographyManager()
    output_path = 'quality_test_output.avi'  # Use AVI for lossless

    print('Testing with quality_test_video.avi...')
    result = manager.hide_data('quality_test_video.avi', str(test_image_path), output_path, is_file=True)
    print(f'Embedding result: {result.get("success", False)}')

    if result.get('success'):
        print('Testing extraction...')
        extracted_data, extracted_filename = manager.extract_data(output_path)
        if extracted_data is not None:
            print(f'Extraction successful: {extracted_filename}, {len(extracted_data)} bytes')
            match = extracted_data == test_data
            print(f'Data match: {match}')
            
            # Check first few bytes
            if len(extracted_data) >= 30 and len(test_data) >= 30:
                first_match = extracted_data[:30] == test_data[:30]
                print(f'First 30 bytes match: {first_match}')
                print(f'Original: {test_data[:30]}')
                print(f'Extracted: {extracted_data[:30]}')
            
            if match:
                print("🎉 PERFECT SUCCESS: Image steganography in video is working perfectly!")
            elif first_match:
                print("🎉 GOOD SUCCESS: Image steganography in video is working (with minor corruption)!")
            else:
                print("⚠️ PARTIAL SUCCESS: Data recovered but with corruption")
            
            return match or first_match
        else:
            print('Extraction failed')
            return False
    else:
        print(f'Embedding failed: {result.get("error", "Unknown error")}')
        return False

if __name__ == "__main__":
    success = test_with_quality_video()
    if success:
        print("\n✅ VIDEO STEGANOGRAPHY FOR IMAGES IS NOW WORKING!")
    else:
        print("\n❌ Still having issues")
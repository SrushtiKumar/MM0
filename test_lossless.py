#!/usr/bin/env python3
"""
Test with lossless codec
"""

from robust_video_stego import RobustVideoSteganographyManager
from pathlib import Path

def test_with_lossless_codec():
    # Create test image
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    test_data = jpeg_header + (b'A' * 5000)  # Smaller image for testing
    test_image_path = Path('lossless_test_image.jpg')
    with open(test_image_path, 'wb') as f:
        f.write(test_data)

    print(f'Created test image: {len(test_data)} bytes')

    # Test with AVI output (which should try lossless codecs)
    manager = RobustVideoSteganographyManager()
    output_path = 'lossless_test_output.avi'  # Use AVI for lossless

    print('Testing with demo_video.mp4 -> AVI output (lossless)...')
    result = manager.hide_data('demo_video.mp4', str(test_image_path), output_path, is_file=True)
    print(f'Embedding result: {result.get("success", False)}')

    if result.get('success'):
        print('Testing extraction...')
        extracted_data, extracted_filename = manager.extract_data(output_path)
        if extracted_data is not None:
            print(f'Extraction successful: {extracted_filename}, {len(extracted_data)} bytes')
            print(f'Data match: {extracted_data == test_data}')
            
            # Check first few bytes
            if len(extracted_data) >= 20 and len(test_data) >= 20:
                print(f'First 20 bytes match: {extracted_data[:20] == test_data[:20]}')
                print(f'Original: {test_data[:20]}')
                print(f'Extracted: {extracted_data[:20]}')
            
            return extracted_data == test_data
        else:
            print('Extraction failed')
            return False
    else:
        print(f'Embedding failed: {result.get("error", "Unknown error")}')
        return False

if __name__ == "__main__":
    success = test_with_lossless_codec()
    if success:
        print("🎉 SUCCESS: Lossless codec approach works!")
    else:
        print("❌ Still having issues")
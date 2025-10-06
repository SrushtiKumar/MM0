#!/usr/bin/env python3
"""
Test image hiding with a larger video
"""

from robust_video_stego import RobustVideoSteganographyManager
from pathlib import Path

def test_image_with_large_video():
    # Create test image
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    test_data = jpeg_header + (b'A' * 15000)  # 15KB
    test_image_path = Path('large_test_image.jpg')
    with open(test_image_path, 'wb') as f:
        f.write(test_data)

    print(f'Created test image: {len(test_data)} bytes')

    # Test with larger video
    manager = RobustVideoSteganographyManager()
    output_path = 'test_output_large.mp4'

    print('Testing with demo_video.mp4 (90 frames, 640x480)...')
    result = manager.hide_data('demo_video.mp4', str(test_image_path), output_path, is_file=True)
    print(f'Embedding result: {result.get("success", False)}')

    if result.get('success'):
        print('Testing extraction...')
        extracted_data, extracted_filename = manager.extract_data(output_path)
        if extracted_data is not None:
            print(f'Extraction successful: {extracted_filename}, {len(extracted_data)} bytes')
            print(f'Data match: {extracted_data == test_data}')
            return True
        else:
            print('Extraction failed')
            return False
    else:
        print(f'Embedding failed: {result.get("error", "Unknown error")}')
        return False

if __name__ == "__main__":
    test_image_with_large_video()
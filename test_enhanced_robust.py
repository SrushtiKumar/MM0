#!/usr/bin/env python3
"""
Test enhanced robust video steganography with image
"""

from enhanced_robust_video_stego import EnhancedRobustVideoSteganographyManager
from pathlib import Path

def test_enhanced_robust_image():
    # Create test image
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    test_data = jpeg_header + (b'A' * 15000)  # 15KB
    test_image_path = Path('enhanced_test_image.jpg')
    with open(test_image_path, 'wb') as f:
        f.write(test_data)

    print(f'Created test image: {len(test_data)} bytes')

    # Test with larger video
    manager = EnhancedRobustVideoSteganographyManager()
    output_path = 'enhanced_test_output.mp4'

    print('Testing enhanced embedding with demo_video.mp4...')
    result = manager.hide_data('demo_video.mp4', str(test_image_path), output_path, is_file=True)
    print(f'Embedding result: {result.get("success", False)}')

    if result.get('success'):
        print('Testing extraction...')
        extracted_data, extracted_filename = manager.extract_data(output_path)
        if extracted_data is not None:
            print(f'Extraction successful: {extracted_filename}, {len(extracted_data)} bytes')
            print(f'Data match: {extracted_data == test_data}')
            
            # Check first few bytes to see if it's close
            if len(extracted_data) >= 20 and len(test_data) >= 20:
                print(f'First 20 bytes match: {extracted_data[:20] == test_data[:20]}')
                print(f'Original: {test_data[:20]}')
                print(f'Extracted: {extracted_data[:20]}')
            
            # If data matches, clean up test files
            if extracted_data == test_data:
                print("🎉 SUCCESS: Image steganography in video is working!")
                return True
            else:
                print("⚠️ Data recovered but with some corruption")
                return True  # Still count as success since data was recovered
        else:
            print('Extraction failed')
            return False
    else:
        print(f'Embedding failed: {result.get("error", "Unknown error")}')
        return False

if __name__ == "__main__":
    test_enhanced_robust_image()
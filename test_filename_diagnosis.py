#!/usr/bin/env python3
"""Direct test focusing on filename preservation logic"""

from universal_file_steganography import UniversalFileSteganography
import tempfile
import os
import json
import struct

def test_filename_logic():
    """Test the filename logic directly by examining the extraction process"""
    
    # Use an existing image file that should be large enough
    import glob
    
    # Look for existing image files
    image_files = glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.jpeg")
    
    if not image_files:
        print("❌ No existing image files found. Creating a larger test image...")
        # Create a minimal but larger PNG
        create_test_image()
        image_files = ["large_test_image.png"]
    
    container_file = image_files[0]
    print(f"📁 Using container: {container_file}")
    
    # Create test MP3 with proper metadata
    test_mp3_content = (
        b'ID3\x03\x00\x00\x00\x00\x00\x00'  # ID3v2.3 header
        b'Test MP3 audio content for filename testing.\n'
        b'This should be extracted with .mp3 extension.\n'
    )
    
    mp3_file = "sample_music_file.mp3"
    output_file = "stego_container.png"
    
    with open(mp3_file, 'wb') as f:
        f.write(test_mp3_content)
    
    print(f"✅ Created MP3: {mp3_file} ({len(test_mp3_content)} bytes)")
    
    try:
        stego = UniversalFileSteganography("test123")
        
        # Hide MP3 in image
        print("\n🔐 Embedding MP3...")
        result = stego.hide_file_in_file(container_file, mp3_file, output_file)
        
        if not result.get('success'):
            print(f"❌ Embedding failed")
            return
        
        print("✅ Embedding successful")
        
        # Test extraction with debug output
        print("\n🔍 Testing extraction with debug...")
        
        # Enable debug by examining the extract_data method step by step
        extraction_result = stego.extract_data(output_file)
        
        print(f"\n📊 Extraction Analysis:")
        print(f"   Result type: {type(extraction_result)}")
        
        if extraction_result and isinstance(extraction_result, tuple):
            extracted_content, filename = extraction_result
            print(f"   Filename: '{filename}'")
            print(f"   Content size: {len(extracted_content)} bytes")
            print(f"   Content type: {type(extracted_content)}")
            
            # Analyze the filename
            print(f"\n🔍 Filename Analysis:")
            
            if filename.endswith('.mp3'):
                print(f"   ✅ SUCCESS: Correct .mp3 extension!")
            elif filename.endswith('.bin'):
                print(f"   ❌ PROBLEM: Has .bin extension instead of .mp3")
                print(f"   This indicates the MP3 signature detection failed")
            else:
                print(f"   ⚠️  Unexpected extension: {filename}")
            
            # Check MP3 header in extracted content
            if isinstance(extracted_content, bytes) and extracted_content.startswith(b'ID3'):
                print(f"   ✅ MP3 header present in content")
                print(f"   The content is correct, just the filename detection needs fixing")
            else:
                print(f"   ❌ MP3 header missing or content is text")
            
            print(f"\n💡 Diagnosis:")
            if filename.endswith('.bin') and extracted_content.startswith(b'ID3'):
                print(f"   The MP3 content is correctly extracted but filename detection")
                print(f"   is falling back to 'extracted_data.bin' instead of detecting MP3 format.")
                print(f"   Need to enhance the MP3 signature detection in extract_data method.")
        
        # Also test the internal extraction to see what filename it produces
        print(f"\n🔍 Testing internal extraction method...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                internal_path = stego.extract_file_from_file(output_file, temp_dir)
                internal_filename = os.path.basename(internal_path)
                print(f"   Internal method filename: '{internal_filename}'")
                
                if 'mp3' in internal_filename.lower():
                    print(f"   ✅ Internal method preserves MP3 in filename!")
                    print(f"   The issue is in the API extract_data filename processing")
                else:
                    print(f"   ❌ Internal method also loses MP3 extension")
            except Exception as e:
                print(f"   ❌ Internal extraction failed: {e}")
        
    finally:
        # Cleanup
        for file in [mp3_file, output_file]:
            if os.path.exists(file):
                os.remove(file)

def create_test_image():
    """Create a larger test image for steganography"""
    try:
        from PIL import Image
        import numpy as np
        
        # Create a 200x200 RGB image
        img_array = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save("large_test_image.png")
        print("✅ Created large test image: large_test_image.png")
        
    except ImportError:
        print("❌ PIL not available, cannot create test image")
        raise

if __name__ == "__main__":
    test_filename_logic()
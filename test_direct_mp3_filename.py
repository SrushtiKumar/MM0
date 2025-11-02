#!/usr/bin/env python3
"""Direct test of MP3 extraction to check filename preservation"""

from universal_file_steganography import UniversalFileSteganography
import tempfile
import os

def test_direct_mp3_extraction():
    """Test MP3 filename preservation in direct steganography"""
    
    # Create test MP3 file with proper header
    test_mp3_content = (
        b'ID3\x03\x00\x00\x00\x00\x00\x00'  # ID3v2.3 header
        b'Test MP3 content for steganography testing\n'
        b'This should preserve the .mp3 extension.\n'
    )
    
    # Create test files
    mp3_file = "test_audio_sample.mp3"
    png_file = "test_container_image.png"
    output_file = "processed_stego_image.png"
    
    # Create simple test PNG file (minimal valid PNG)
    png_content = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\rIHDR'  # IHDR chunk
        b'\x00\x00\x00\x10\x00\x00\x00\x10'  # 16x16 image
        b'\x08\x02\x00\x00\x00\x90\x91h6'  # IHDR data + CRC
        b'\x00\x00\x00\x0bIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01'  # Minimal IDAT
        b'\x00\x18\xdd\x8d\xb4'  # IDAT CRC
        b'\x00\x00\x00\x00IEND\xae\x42`\x82'  # IEND chunk
    )
    
    # Write test files
    with open(mp3_file, 'wb') as f:
        f.write(test_mp3_content)
    
    with open(png_file, 'wb') as f:
        f.write(png_content)
    
    print(f"✅ Created test files:")
    print(f"   MP3: {mp3_file} ({len(test_mp3_content)} bytes)")
    print(f"   PNG: {png_file} ({len(png_content)} bytes)")
    
    try:
        # Initialize steganography with password
        stego = UniversalFileSteganography("test123")
        
        # Step 1: Hide MP3 in PNG
        print(f"\n🔐 Hiding MP3 in PNG...")
        result = stego.hide_file_in_file(png_file, mp3_file, output_file)
        
        if not result.get('success'):
            print(f"❌ Embedding failed: {result}")
            return
        
        print(f"✅ Embedding successful!")
        print(f"   Output: {output_file}")
        print(f"   Method: {result['method']}")
        
        # Step 2: Extract MP3 from PNG using extract_data (API method)
        print(f"\n🔍 Extracting using extract_data method (API-compatible)...")
        
        extraction_result = stego.extract_data(output_file)
        
        if extraction_result is None:
            print("❌ Extraction failed - returned None")
            return
        
        if isinstance(extraction_result, tuple):
            extracted_content, extracted_filename = extraction_result
            print(f"✅ Extraction successful!")
            print(f"   Content: {len(extracted_content)} bytes")
            print(f"   Filename: '{extracted_filename}'")
            
            # Check if filename has correct extension
            if extracted_filename.endswith('.mp3'):
                print("✅ SUCCESS: Filename has .mp3 extension!")
            elif extracted_filename.endswith('.bin'):
                print("❌ ISSUE: Filename has .bin extension instead of .mp3")
                print("   This is the problem we need to fix!")
            else:
                print(f"⚠️  Unexpected filename: {extracted_filename}")
            
            # Verify content integrity
            if isinstance(extracted_content, bytes):
                content_to_compare = extracted_content
            else:
                content_to_compare = extracted_content.encode('utf-8')
            
            if content_to_compare == test_mp3_content:
                print("✅ Content integrity: Perfect match!")
            else:
                print("❌ Content integrity: Mismatch")
                print(f"   Original: {test_mp3_content[:30]}")
                print(f"   Extracted: {content_to_compare[:30]}")
            
            # Check MP3 header
            if content_to_compare.startswith(b'ID3'):
                print("✅ MP3 header: ID3 tag preserved correctly")
            else:
                print(f"❌ MP3 header: Missing - starts with {content_to_compare[:10]}")
        else:
            print(f"❌ Unexpected return format: {type(extraction_result)}")
        
        # Step 3: Also test the regular extraction method 
        print(f"\n🔍 Extracting using extract_file_from_file method...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            extracted_path = stego.extract_file_from_file(output_file, temp_dir)
            extracted_filename_alt = os.path.basename(extracted_path)
            
            with open(extracted_path, 'rb') as f:
                extracted_content_alt = f.read()
            
            print(f"✅ Alternative extraction successful!")
            print(f"   Filename: '{extracted_filename_alt}'")
            print(f"   Content: {len(extracted_content_alt)} bytes")
            
            if extracted_filename_alt.endswith('.mp3') or 'mp3' in extracted_filename_alt:
                print("✅ Alternative method preserves MP3 extension!")
            else:
                print(f"⚠️  Alternative method filename: {extracted_filename_alt}")
        
    finally:
        # Cleanup
        for file in [mp3_file, png_file, output_file]:
            if os.path.exists(file):
                os.remove(file)
        print("\n🧹 Cleaned up test files")

if __name__ == "__main__":
    test_direct_mp3_extraction()
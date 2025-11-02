#!/usr/bin/env python3
"""
Direct test of the steganography system to understand the filename issue
"""

import os
import tempfile
from PIL import Image
from universal_file_steganography import UniversalFileSteganography

def test_direct_steganography():
    """Test steganography directly to see what filenames are used"""
    print("🔍 DIRECT STEGANOGRAPHY FILENAME TEST")
    print("=" * 50)
    
    try:
        # Create test files
        carrier_img = Image.new('RGB', (100, 100), color='blue')
        carrier_path = "direct_carrier.png"
        carrier_img.save(carrier_path, 'PNG')
        
        secret_img = Image.new('RGB', (50, 50), color='red')
        secret_path = "my_secret_image.jpg"
        secret_img.save(secret_path, 'JPEG')
        
        print(f"✅ Created test files:")
        print(f"   Carrier: {carrier_path}")
        print(f"   Secret: {secret_path}")
        
        # Initialize steganography
        stego = UniversalFileSteganography()
        
        # Test 1: Direct steganography with original filenames
        print(f"\n📤 Test 1: Direct embedding...")
        result = stego.hide_file_in_file(carrier_path, secret_path, "direct_stego.png")
        print(f"Embed result: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"\n🔓 Test 1: Direct extraction...")
            extraction_result = stego.extract_data("direct_stego.png")
            
            if isinstance(extraction_result, tuple):
                data, filename = extraction_result
                print(f"✅ Direct extraction successful:")
                print(f"   Data type: {type(data)}")
                print(f"   Data size: {len(data)} bytes")
                print(f"   Returned filename: {filename}")
                print(f"   First 10 bytes: {data[:10].hex() if isinstance(data, bytes) else 'N/A'}")
                
                # Verify it's a valid JPEG
                if isinstance(data, bytes):
                    is_jpeg = data.startswith(b'\xff\xd8\xff\xe0') and b'JFIF' in data[:20]
                    print(f"   Is valid JPEG: {is_jpeg}")
        
        # Test 2: Steganography with API-style temp filenames
        print(f"\n📤 Test 2: Embedding with temp filenames (simulating API)...")
        
        # Simulate how the API saves files with temp names
        import shutil
        temp_carrier = "tmp_carrier_123abc.png"
        temp_secret = "tmp_secret_456def.bin"  # Note: .bin extension like API uses
        
        shutil.copy(carrier_path, temp_carrier)
        shutil.copy(secret_path, temp_secret)
        
        result2 = stego.hide_file_in_file(temp_carrier, temp_secret, "temp_stego.png")
        print(f"Embed result: {result2.get('success', False)}")
        
        if result2.get('success'):
            print(f"\n🔓 Test 2: Extraction from temp-named files...")
            extraction_result2 = stego.extract_data("temp_stego.png")
            
            if isinstance(extraction_result2, tuple):
                data2, filename2 = extraction_result2
                print(f"✅ Temp extraction successful:")
                print(f"   Data type: {type(data2)}")
                print(f"   Data size: {len(data2)} bytes")
                print(f"   Returned filename: {filename2}")
                print(f"   First 10 bytes: {data2[:10].hex() if isinstance(data2, bytes) else 'N/A'}")
                
                # This should show us what happens when the original file has a .bin extension
                if isinstance(data2, bytes):
                    is_jpeg = data2.startswith(b'\xff\xd8\xff\xe0') and b'JFIF' in data2[:20]
                    print(f"   Is valid JPEG: {is_jpeg}")
        
        # Cleanup
        for f in [carrier_path, secret_path, "direct_stego.png", "temp_stego.png", temp_carrier, temp_secret]:
            if os.path.exists(f):
                os.remove(f)
        
        print(f"\n🎯 SUMMARY:")
        print(f"   This test shows what filenames the steganography system")
        print(f"   actually stores and returns, helping us understand why")
        print(f"   the API returns temp filenames instead of original ones.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_steganography()
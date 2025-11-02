#!/usr/bin/env python3
"""
Simple test to check what extract_data returns
"""

import tempfile
import os
from PIL import Image
import io

# Import our steganography class
from universal_file_steganography import UniversalFileSteganography

def create_test_files():
    """Create test files for embedding/extraction"""
    # Create a simple PNG carrier
    img = Image.new('RGB', (100, 100), color='blue')
    carrier_path = "test_carrier.png"
    img.save(carrier_path, 'PNG')
    
    # Create a JPG secret file
    secret_img = Image.new('RGB', (50, 50), color='red')
    secret_path = "test_secret.jpg"
    secret_img.save(secret_path, 'JPEG')
    
    return carrier_path, secret_path

def test_extract_data_directly():
    """Test the extract_data method directly"""
    print("🧪 Testing extract_data method directly")
    print("=" * 50)
    
    try:
        # Create test files
        carrier_path, secret_path = create_test_files()
        
        # Initialize steganography
        stego = UniversalFileSteganography()
        
        # Embed the secret file (container_file, secret_file, output_file)
        print("📥 Embedding secret JPG in PNG carrier...")
        result = stego.hide_file_in_file(carrier_path, secret_path, "stego_test.png")
        print(f"Embed result: {result}")
        
        if result['success']:
            stego_file = "stego_test.png"  # We know the output filename
            print(f"Stego file created: {stego_file}")
            
            # Extract using the extract_data method (what the API uses)
            print("\n🔓 Extracting using extract_data method...")
            extraction_result = stego.extract_data(stego_file)
            
            print(f"Extraction result type: {type(extraction_result)}")
            
            if isinstance(extraction_result, tuple):
                data, filename = extraction_result
                print(f"Data type: {type(data)}")
                print(f"Filename: {filename}")
                print(f"Data size: {len(data) if hasattr(data, '__len__') else 'N/A'}")
                
                if isinstance(data, bytes):
                    print(f"First 20 bytes (hex): {data[:20].hex()}")
                    print(f"First 20 bytes (repr): {repr(data[:20])}")
                    
                    # Try to verify it's a valid JPG
                    try:
                        img = Image.open(io.BytesIO(data))
                        print(f"✅ Valid image: {img.size} {img.mode}")
                    except Exception as e:
                        print(f"❌ Invalid image data: {e}")
                        
                elif isinstance(data, str):
                    print(f"String data preview: {repr(data[:100])}")
                    
            else:
                print(f"Non-tuple result: {type(extraction_result)}")
                print(f"Value: {repr(extraction_result)}")
                
        # Cleanup
        for f in [carrier_path, secret_path, "stego_test.png"]:
            if os.path.exists(f):
                os.remove(f)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extract_data_directly()
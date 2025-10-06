"""
Quick test script to verify the steganography fix
"""

import os
import tempfile
from PIL import Image
import numpy as np
from stego_cli import HybridImageSteganography

def test_simple_steganography():
    """Test basic hide/extract functionality"""
    print("Testing steganography fix...")
    
    # Create a simple test image
    test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    test_image_path = "test_image.png"
    output_path = "test_output.png"
    
    try:
        # Save test image
        Image.fromarray(test_image).save(test_image_path)
        
        # Create steganography instance
        stego = HybridImageSteganography()
        
        # Test message
        test_message = "Hello, this is a test message!"
        test_data = test_message.encode('utf-8')
        
        print(f"Original message: {test_message}")
        print(f"Data size: {len(test_data)} bytes")
        
        # Hide data
        print("\n1. Hiding data...")
        result = stego.embed_data(test_image_path, test_data, output_path)
        print(f"Hide result: {result}")
        
        # Extract data
        print("\n2. Extracting data...")
        extracted_data = stego.extract_data(output_path)
        extracted_message = extracted_data.decode('utf-8')
        
        print(f"Extracted message: {extracted_message}")
        
        # Verify
        if test_message == extracted_message:
            print("\n✅ SUCCESS: Message extracted correctly!")
            return True
        else:
            print(f"\n❌ FAILED: Messages don't match!")
            print(f"Expected: {test_message}")
            print(f"Got: {extracted_message}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for file_path in [test_image_path, output_path]:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    success = test_simple_steganography()
    if success:
        print("\n🎉 Steganography fix verified successfully!")
    else:
        print("\n💥 Test failed - more fixes needed")
#!/usr/bin/env python3
"""
Simple direct test of FinalVideoSteganographyManager
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from final_video_steganography import FinalVideoSteganographyManager

def test_simple_message():
    """Test with a very simple message"""
    
    print("🔧 Direct Manager Test")
    print("=" * 30)
    
    if not os.path.exists('clean_carrier.mp4'):
        print("❌ clean_carrier.mp4 not found")
        return False
    
    # Very simple test
    simple_message = "test"
    password = "123"
    output_file = "simple_test_output.avi"
    
    print(f"Message: '{simple_message}'")
    print(f"Password: '{password}'")
    
    # Create manager
    manager = FinalVideoSteganographyManager(password)
    
    try:
        print("\n1. Embedding...")
        result = manager.hide_data('clean_carrier.mp4', simple_message, output_file)
        
        if not result.get('success'):
            print(f"❌ Embed failed: {result.get('error')}")
            return False
        
        actual_output = result.get('output_path', output_file)
        print(f"✅ Embedded successfully: {actual_output}")
        
        if not os.path.exists(actual_output):
            print(f"❌ Output file not created: {actual_output}")
            return False
        
        print(f"File size: {os.path.getsize(actual_output)} bytes")
        
        print("\n2. Extracting...")
        extracted_data, filename = manager.extract_data(actual_output)
        
        if extracted_data is None:
            print("❌ Extraction failed: No data returned")
            return False
        
        # Convert to string if needed
        if isinstance(extracted_data, bytes):
            extracted_text = extracted_data.decode('utf-8')
        else:
            extracted_text = str(extracted_data)
        
        print(f"✅ Extracted: '{extracted_text}'")
        print(f"Original:  '{simple_message}'")
        
        # Check if they match
        success = extracted_text.strip() == simple_message.strip()
        
        if success:
            print("\n🎉 SUCCESS: Messages match!")
        else:
            print(f"\n❌ MISMATCH:")
            print(f"  Expected: '{simple_message}' (len={len(simple_message)})")
            print(f"  Got:      '{extracted_text}' (len={len(extracted_text)})")
        
        # Cleanup
        try:
            os.remove(actual_output)
            print("🧹 Cleaned up test file")
        except:
            pass
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_message()
    print(f"\n{'='*30}")
    if success:
        print("🎉 Direct test PASSED!")
    else:
        print("❌ Direct test FAILED!")
    
    sys.exit(0 if success else 1)
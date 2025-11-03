"""
Direct verification of the password fix - test steganography manager directly
"""

import json
import tempfile
import os
import sys

# Add current directory to path to import steganography modules
sys.path.append('.')

from universal_file_steganography import UniversalFileSteganography

def test_password_extraction_fix():
    """Direct test of password-based steganography"""
    
    print("🧪 Testing Universal File Steganography with Password")
    print("=" * 60)
    
    # Create test files
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as carrier_file:
        # Simple 1x1 PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x14\xa3\x00\x00\x00\x00IEND\xaeB`\x82'
        carrier_file.write(png_data)
        carrier_path = carrier_file.name
    
    # Create test JSON (like forensic evidence)
    test_evidence = {
        "type": "forensic_evidence",
        "metadata": {
            "case_id": "TEST-001",
            "investigator": "Test Agent",
            "location": "Test Lab"
        },
        "file_data": "VGVzdCBldmlkZW5jZSBkYXRh",  # base64 encoded "Test evidence data"
        "original_filename": "evidence.txt",
        "timestamp": "2024-01-01T12:00:00"
    }
    
    # Convert to JSON string (like forensic embedding does)
    forensic_json = json.dumps(test_evidence, indent=2)
    password = "test123"
    
    try:
        # Initialize steganography manager
        manager = UniversalFileSteganography()
        
        # Step 1: Hide data WITH password (like forensic embed does)
        print("📤 Step 1: Hiding forensic JSON with password...")
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as stego_file:
            stego_path = stego_file.name
        
        hide_result = manager.hide_data(
            carrier_path,
            forensic_json,  # The JSON string
            stego_path,
            password,
            is_file=False,  # Text mode
            original_filename="forensic_evidence.json"
        )
        
        if not hide_result.get("success"):
            print(f"❌ Hide failed: {hide_result}")
            return False
        
        print(f"✅ Hide successful: {hide_result}")
        print(f"   Original JSON size: {len(forensic_json)} chars")
        
        # Step 2a: Extract WITHOUT password (OLD BUG - should fail)
        print("\n📥 Step 2a: Extracting WITHOUT password (simulating old bug)...")
        
        try:
            extract_result_no_pass = manager.extract_data(stego_path)  # No password
            if extract_result_no_pass:
                extracted_data, filename = extract_result_no_pass
                print(f"❌ UNEXPECTED: Extraction without password succeeded!")
                print(f"   Data type: {type(extracted_data)}")
                print(f"   Data size: {len(extracted_data) if extracted_data else 0}")
                if isinstance(extracted_data, bytes):
                    print(f"   First 100 bytes: {extracted_data[:100]}")
            else:
                print("✅ EXPECTED: Extraction without password failed (returns None)")
        except Exception as e:
            print(f"✅ EXPECTED: Extraction without password threw exception: {e}")
        
        # Step 2b: Extract WITH password (NEW FIX - should work)
        print("\n📥 Step 2b: Extracting WITH password (testing our fix)...")
        
        extract_result = manager.extract_data(stego_path, password=password)  # WITH password
        
        if not extract_result:
            print("❌ Extract with password failed!")
            return False
        
        extracted_data, extracted_filename = extract_result
        print(f"✅ Extract with password successful!")
        print(f"   Data type: {type(extracted_data)}")
        print(f"   Data size: {len(extracted_data) if extracted_data else 0}")
        print(f"   Filename: {extracted_filename}")
        
        # Step 3: Verify extracted data is valid JSON
        print("\n🔍 Step 3: Verifying extracted data...")
        
        if isinstance(extracted_data, bytes):
            try:
                decoded_data = extracted_data.decode('utf-8')
                print(f"✅ Successfully decoded bytes to UTF-8")
                print(f"   Decoded size: {len(decoded_data)} chars")
            except Exception as e:
                print(f"❌ Failed to decode bytes: {e}")
                return False
        else:
            decoded_data = extracted_data
            print(f"✅ Data already text: {len(decoded_data)} chars")
        
        # Try to parse as JSON
        try:
            parsed_json = json.loads(decoded_data)
            print(f"✅ Successfully parsed JSON!")
            print(f"   Type: {parsed_json.get('type')}")
            print(f"   Case ID: {parsed_json.get('metadata', {}).get('case_id')}")
            print(f"   Original filename: {parsed_json.get('original_filename')}")
            
            # Verify it matches original
            if parsed_json == test_evidence:
                print("✅ Extracted JSON matches original perfectly!")
                return True
            else:
                print("⚠️  Extracted JSON differs from original")
                print(f"   Original keys: {list(test_evidence.keys())}")
                print(f"   Extracted keys: {list(parsed_json.keys())}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse as JSON: {e}")
            print(f"   First 200 chars: {repr(decoded_data[:200])}")
            return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for path in [carrier_path, stego_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    success = test_password_extraction_fix()
    
    if success:
        print("\n🎉 PASSWORD FIX VERIFIED!")
        print("✅ Steganography manager correctly handles password-protected extraction")
        print("✅ Forensic JSON is preserved perfectly with password")
        print("✅ Our fix (adding password=password to extract_data call) is correct!")
    else:
        print("\n❌ Password fix verification failed")
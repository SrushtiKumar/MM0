#!/usr/bin/env python3
"""
Direct Module Test - Verify core steganography modules work correctly
"""

from universal_file_steganography import UniversalFileSteganography
import os

def test_direct_modules():
    """Test steganography modules directly to verify content preservation"""
    
    print("=== DIRECT MODULE TEST ===\n")
    
    # Test with the same content and password as API test
    test_message = "This is a test message to verify content preservation through the API workflow!"
    password = "workflow123"
    
    print("1. Testing direct image steganography...")
    
    try:
        # Initialize steganography
        stego = UniversalFileSteganography()
        
        carrier_path = "debug_embedded.png"
        output_path = "direct_test_output.png"
        
        if not os.path.exists(carrier_path):
            print(f"   ERROR: Carrier {carrier_path} not found")
            return
        
        # Hide message
        print(f"   Hiding message: '{test_message}'")
        hide_result = stego.hide_data(carrier_path, test_message, output_path, password=password)
        print(f"   Hide result: {hide_result}")
        
        if hide_result and os.path.exists(output_path):
            # Extract message
            print(f"   Extracting from: {output_path}")
            extract_result = stego.extract_data(output_path, password=password)
            print(f"   Extract result type: {type(extract_result)}")
            print(f"   Extract result: {repr(extract_result)}")
            
            # Handle tuple return (data, filename)
            if isinstance(extract_result, tuple):
                extracted_data, original_filename = extract_result
                print(f"   Extracted data: {repr(extracted_data)}")
                print(f"   Original filename: {original_filename}")
                
                # Check content preservation - handle bytes vs string
                if isinstance(extracted_data, bytes):
                    try:
                        decoded_data = extracted_data.decode('utf-8')
                        if decoded_data == test_message:
                            print("   ✅ DIRECT MODULE TEST: SUCCESS")
                            print("   Content perfectly preserved (bytes decoded to string)")
                        else:
                            print("   ❌ DIRECT MODULE TEST: FAILED (decoded)")
                            print(f"      Expected: {repr(test_message)}")
                            print(f"      Got:      {repr(decoded_data)}")
                    except UnicodeDecodeError:
                        print("   ❌ DIRECT MODULE TEST: FAILED (not UTF-8)")
                        print(f"      Got binary: {repr(extracted_data[:50])}")
                elif extracted_data == test_message:
                    print("   ✅ DIRECT MODULE TEST: SUCCESS")
                    print("   Content perfectly preserved in direct module test")
                else:
                    print("   ❌ DIRECT MODULE TEST: FAILED")
                    print(f"      Expected: {repr(test_message)}")
                    print(f"      Got:      {repr(extracted_data)}")
            elif extract_result == test_message:
                print("   ✅ DIRECT MODULE TEST: SUCCESS")
            else:
                print(f"   ❌ DIRECT MODULE TEST: FAILED")
                print(f"      Expected: {repr(test_message)}")
                print(f"      Got:      {repr(extract_result)}")
                
            # Cleanup
            try:
                os.remove(output_path)
            except:
                pass
                
        else:
            print("   ❌ Hide operation failed")
            
    except Exception as e:
        print(f"   ❌ Direct test error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== DIRECT MODULE TEST COMPLETE ===")

if __name__ == "__main__":
    test_direct_modules()
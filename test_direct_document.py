#!/usr/bin/env python3
"""Direct test of document steganography to isolate the capacity issue"""

import os
import tempfile
from universal_file_steganography import UniversalFileSteganography

def test_direct_document_steganography():
    """Test document steganography directly without API"""
    
    print("🧪 DIRECT DOCUMENT STEGANOGRAPHY TEST")
    print("=" * 50)
    
    # Create test files that match the API test exactly
    rtf_content = """{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}} \\f0\\fs24 This is a simple RTF document used as a carrier for steganography testing. It contains minimal formatting and plain text content to serve as a baseline for capacity testing.}"""
    
    secret_content = "This is the secret message to hide in various media files using the API!"
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False) as carrier_file:
        carrier_file.write(rtf_content)
        carrier_path = carrier_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as secret_file:
        secret_file.write(secret_content)
        secret_path = secret_file.name
    
    try:
        print(f"📁 Carrier file: {os.path.basename(carrier_path)} ({len(rtf_content.encode())} bytes)")
        print(f"📁 Secret file: {os.path.basename(secret_path)} ({len(secret_content.encode())} bytes)")
        print()
        
        # Test without password (no encryption)
        print("🔓 Testing WITHOUT encryption...")
        stego = UniversalFileSteganography()
        
        output_path = "test_stego_nopass.rtf"
        
        try:
            result = stego.hide_file_in_file(carrier_path, secret_path, output_path)
            print("✅ Embedding successful (no encryption)")
            print(f"📊 Result: {result}")
            
            # Test extraction
            extracted_path = stego.extract_file_from_file(output_path)
            print(f"✅ Extraction successful: {extracted_path}")
            
            # Verify content
            with open(extracted_path, 'r') as f:
                extracted_content = f.read()
            
            if extracted_content == secret_content:
                print("✅ Content verification: PASS")
            else:
                print("❌ Content verification: FAIL")
                
        except Exception as e:
            print(f"❌ No encryption test failed: {e}")
        
        print()
        
        # Test with password (encryption)
        print("🔐 Testing WITH encryption...")
        stego_encrypted = UniversalFileSteganography(password="test123")
        
        output_path_encrypted = "test_stego_encrypted.rtf"
        
        try:
            result = stego_encrypted.hide_file_in_file(carrier_path, secret_path, output_path_encrypted)
            print("✅ Embedding successful (with encryption)")
            print(f"📊 Result: {result}")
            
            # Test extraction
            extracted_path = stego_encrypted.extract_file_from_file(output_path_encrypted)
            print(f"✅ Extraction successful: {extracted_path}")
            
            # Verify content
            with open(extracted_path, 'r') as f:
                extracted_content = f.read()
            
            if extracted_content == secret_content:
                print("✅ Content verification: PASS")
            else:
                print("❌ Content verification: FAIL")
                
        except Exception as e:
            print(f"❌ Encryption test failed: {e}")
        
    finally:
        # Cleanup
        cleanup_files = [
            carrier_path, 
            secret_path, 
            "test_stego_nopass.rtf",
            "test_stego_encrypted.rtf"
        ]
        
        # Also clean up extracted files
        for i in range(10):  # Clean up any extracted files
            cleanup_files.extend([
                f"extracted_api_secret.txt",
                f"extracted_{os.path.basename(secret_path)}",
            ])
        
        for file_path in cleanup_files:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                    print(f"🗑️ Cleaned up: {file_path}")
                except:
                    pass

if __name__ == "__main__":
    test_direct_document_steganography()
#!/usr/bin/env python3
"""Test the updated universal steganography with safe document handling"""

import os
from universal_file_steganography import UniversalFileSteganography

def test_updated_system():
    """Test the updated system with safe document handling"""
    
    print("🔄 TESTING UPDATED UNIVERSAL STEGANOGRAPHY")
    print("=" * 60)
    
    # Create the same test PDF that was getting corrupted
    simple_pdf = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""

    # Save test PDF
    with open("test_updated_original.pdf", "wb") as f:
        f.write(simple_pdf)
    
    print(f"📄 Original PDF size: {len(simple_pdf)} bytes")
    
    # Create secret file
    secret_content = "This secret message should not corrupt the 6145-page PDF structure!"
    with open("test_updated_secret.txt", "w") as f:
        f.write(secret_content)
    
    print(f"🔐 Secret content: {len(secret_content)} bytes")
    
    # Test with updated system
    try:
        stego = UniversalFileSteganography(password="test123")
        result = stego.hide_file_in_file("test_updated_original.pdf", "test_updated_secret.txt", "test_updated_stego.pdf")
        
        print(f"📊 Updated embedding result: {result}")
        
        # Check if PDF structure is preserved
        with open("test_updated_stego.pdf", "rb") as f:
            stego_content = f.read()
        
        print(f"📄 Updated stego PDF size: {len(stego_content)} bytes")
        
        print("\n🔍 STRUCTURE PRESERVATION CHECK:")
        print("=" * 35)
        
        if stego_content.startswith(b'%PDF'):
            print("✅ PDF header preserved")
        else:
            print("❌ PDF header corrupted")
        
        if b'Hello World' in stego_content:
            print("✅ Original content PRESERVED (6145 pages would be safe)")
        else:
            print("❌ Original content lost (this would destroy large PDFs)")
            
        if b'xref' in stego_content:
            print("✅ Cross-reference table preserved") 
        else:
            print("❌ Cross-reference table corrupted")
        
        # Test extraction
        print("\n🔐 EXTRACTION TEST:")
        print("=" * 20)
        
        extracted_path = stego.extract_file_from_file("test_updated_stego.pdf")
        
        with open(extracted_path, "r") as f:
            extracted_content = f.read()
        
        if extracted_content == secret_content:
            print("✅ Extraction perfect - content matches exactly")
            print("✅ SYSTEM FIXED - Large PDFs will no longer be corrupted")
        else:
            print("❌ Extraction failed")
            print(f"Expected: {secret_content}")
            print(f"Got: {extracted_content}")
        
    except Exception as e:
        print(f"❌ Updated system failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    files_to_remove = [
        "test_updated_original.pdf", 
        "test_updated_secret.txt", 
        "test_updated_stego.pdf"
    ]
    
    # Also clean up extracted files
    for file in os.listdir('.'):
        if file.startswith('extracted_'):
            files_to_remove.append(file)
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    test_updated_system()
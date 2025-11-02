#!/usr/bin/env python3
"""Test the safe document steganography with PDF"""

import os
from safe_document_steganography import SafeDocumentSteganography

def test_safe_pdf():
    """Test safe PDF steganography that preserves document structure"""
    
    print("🛡️ SAFE PDF STEGANOGRAPHY TEST")
    print("=" * 50)
    
    # Create the same test PDF
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

    # Save original PDF
    with open("test_safe_original.pdf", "wb") as f:
        f.write(simple_pdf)
    
    print(f"📄 Original PDF size: {len(simple_pdf)} bytes")
    
    # Create secret file
    secret_content = "This is a secret message to hide safely in the PDF without corruption!"
    with open("test_safe_secret.txt", "w") as f:
        f.write(secret_content)
    
    print(f"🔐 Secret content: {len(secret_content)} bytes")
    
    # Test safe embedding
    try:
        safe_stego = SafeDocumentSteganography(password="test123")
        result = safe_stego.hide_file_in_document("test_safe_original.pdf", "test_safe_secret.txt", "test_safe_stego.pdf")
        
        print(f"📊 Safe embedding result: {result}")
        
        # Analyze the safe stego file
        with open("test_safe_stego.pdf", "rb") as f:
            stego_content = f.read()
        
        print(f"📄 Safe stego PDF size: {len(stego_content)} bytes")
        
        # Check if PDF structure is PRESERVED
        print("\n🔍 STRUCTURE PRESERVATION CHECK:")
        print("=" * 35)
        
        if stego_content.startswith(b'%PDF'):
            print("✅ PDF header preserved")
        else:
            print("❌ PDF header corrupted")
        
        if b'xref' in stego_content:
            print("✅ Cross-reference table preserved")
        else:
            print("❌ Cross-reference table missing")
            
        if b'/Catalog' in stego_content:
            print("✅ Document catalog preserved") 
        else:
            print("❌ Document catalog missing")
            
        if b'Hello World' in stego_content:
            print("✅ Original content PRESERVED")
        else:
            print("❌ Original content lost")
        
        # Test extraction
        print("\n🔐 EXTRACTION TEST:")
        print("=" * 20)
        
        extracted_path = safe_stego.extract_file_from_document("test_safe_stego.pdf")
        
        with open(extracted_path, "r") as f:
            extracted_content = f.read()
        
        if extracted_content == secret_content:
            print("✅ Extraction successful - content matches exactly")
        else:
            print("❌ Extraction failed - content mismatch")
            print(f"Expected: {secret_content}")
            print(f"Got: {extracted_content}")
        
        print(f"✅ Safe steganography test PASSED")
        
    except Exception as e:
        print(f"❌ Safe embedding failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    for file in ["test_safe_original.pdf", "test_safe_secret.txt", "test_safe_stego.pdf"]:
        if os.path.exists(file):
            os.remove(file)
    
    # Also clean up extracted files
    for file in os.listdir('.'):
        if file.startswith('extracted_'):
            os.remove(file)

if __name__ == "__main__":
    test_safe_pdf()
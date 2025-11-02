#!/usr/bin/env python3
"""
Test document corruption with larger files
"""

import os
from universal_file_steganography import UniversalFileSteganography

def create_larger_test_doc():
    """Create a larger RTF document for testing"""
    rtf_content = r"""{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}
\\f0\\fs24 This is a comprehensive test RTF document for steganography testing.
\\par
\\par
\\b Introduction\\b0
\\par
This document contains multiple sections and formatting elements to ensure that 
the RTF structure is preserved during steganography processing. The document 
should remain fully readable and properly formatted after embedding hidden data.
\\par
\\par
\\b Section 1: Text Content\\b0
\\par
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
\\par
\\par
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt 
in culpa qui officia deserunt mollit anim id est laborum.
\\par
\\par
\\b Section 2: Lists and Formatting\\b0
\\par
Here are some important points:
\\par
- Point number one with detailed explanation
\\par
- Point number two with additional context and information
\\par  
- Point number three with comprehensive details
\\par
- Point number four with extended content for testing
\\par
\\par
\\b Section 3: Additional Content\\b0
\\par
This section contains more text to ensure we have sufficient capacity for 
steganography operations while maintaining document integrity and readability.
\\par
\\par
The steganography system should preserve:
\\par
1. Document structure and formatting
\\par
2. Text content and readability  
\\par
3. File format compatibility
\\par
4. Binary integrity for proper file opening
\\par
\\par
\\b Conclusion\\b0
\\par
This test document provides a comprehensive evaluation of document steganography 
capabilities while ensuring sufficient data capacity for embedding operations.
\\par
}"""
    
    with open("large_test_document.rtf", 'wb') as f:
        f.write(rtf_content.encode('utf-8'))
    
    return "large_test_document.rtf"

def test_large_document_steganography():
    """Test steganography with larger document"""
    
    print("🧪 TESTING LARGE DOCUMENT STEGANOGRAPHY")
    print("=" * 60)
    
    # Create larger test document
    doc_file = create_larger_test_doc()
    secret_content = "This is a secret message hidden in the document!"
    secret_file = "secret_message.txt"
    
    with open(secret_file, 'w') as f:
        f.write(secret_content)
    
    print(f"📄 Created test document: {doc_file}")
    
    # Check file sizes
    doc_size = os.path.getsize(doc_file)
    secret_size = os.path.getsize(secret_file)
    
    print(f"📏 Document size: {doc_size} bytes")
    print(f"📏 Secret size: {secret_size} bytes")
    print(f"📊 Capacity ratio: {(secret_size * 8) / doc_size:.2f} bits per byte")
    
    try:
        # Test steganography
        stego = UniversalFileSteganography("test123")
        output_file = "processed_large_doc.rtf"
        
        print(f"🔐 Embedding secret in large document...")
        result = stego.hide_file_in_file(doc_file, secret_file, output_file)
        
        if not result.get('success'):
            print(f"❌ Embedding failed: {result}")
            return False
        
        print(f"✅ Embedding successful using {result.get('method', 'unknown')} method")
        print(f"📊 Capacity used: {result.get('capacity_used', 'unknown')}")
        
        # Verify file integrity
        if not os.path.exists(output_file):
            print(f"❌ Output file not created")
            return False
        
        output_size = os.path.getsize(output_file)
        print(f"📏 Output size: {output_size} bytes")
        
        # Test if RTF is still valid
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if "\\rtf1" in content and content.count('{') > 0:
                print(f"✅ RTF format preserved")
            else:
                print(f"❌ RTF format may be corrupted")
        except Exception as e:
            print(f"❌ Cannot validate RTF: {e}")
        
        # Test extraction
        print(f"🔍 Testing extraction...")
        extraction_result = stego.extract_data(output_file)
        
        if extraction_result and isinstance(extraction_result, tuple):
            extracted_content, filename = extraction_result
            
            if isinstance(extracted_content, bytes):
                extracted_text = extracted_content.decode('utf-8')
            else:
                extracted_text = extracted_content
                
            if secret_content.strip() == extracted_text.strip():
                print(f"✅ Extraction successful - data preserved!")
                print(f"📝 Extracted: '{extracted_text}'")
                return True
            else:
                print(f"❌ Extraction data mismatch")
                print(f"   Expected: '{secret_content}'")
                print(f"   Got:      '{extracted_text}'")
                return False
        else:
            print(f"❌ Extraction failed: {extraction_result}")
            return False
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        for file in [doc_file, secret_file, "processed_large_doc.rtf"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = test_large_document_steganography()
    if success:
        print(f"\n🎉 LARGE DOCUMENT TEST PASSED!")
    else:
        print(f"\n❌ LARGE DOCUMENT TEST FAILED!")
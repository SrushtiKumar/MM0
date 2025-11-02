#!/usr/bin/env python3
"""
Test binary document corruption (DOC, PDF, etc.)
"""

import os
from universal_file_steganography import UniversalFileSteganography

def create_test_binary_doc():
    """Create a simple binary document file for testing"""
    # Create a minimal RTF document (Rich Text Format)
    rtf_content = r"""{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}
\\f0\\fs24 This is a test RTF document.
\\par
\\par
It contains some text and should remain readable after steganography processing.
\\par
\\par
- Bullet point 1
\\par
- Bullet point 2  
\\par
- Bullet point 3
\\par
}"""
    
    with open("test_document.rtf", 'wb') as f:
        f.write(rtf_content.encode('utf-8'))
    
    return "test_document.rtf"

def test_binary_document_corruption():
    """Test binary document steganography corruption"""
    
    print("🧪 TESTING BINARY DOCUMENT CORRUPTION")
    print("=" * 60)
    
    # Create test binary document
    doc_file = create_test_binary_doc()
    secret_content = "Hidden message in binary document!"
    secret_file = "secret_binary.txt"
    
    with open(secret_file, 'w') as f:
        f.write(secret_content)
    
    print(f"📄 Created test document: {doc_file}")
    
    # Check original file size and type
    original_size = os.path.getsize(doc_file)
    print(f"📏 Original size: {original_size} bytes")
    
    # Read original binary content
    with open(doc_file, 'rb') as f:
        original_data = f.read()
    
    print(f"🔍 Original binary signature: {original_data[:20].hex()}")
    
    try:
        # Test steganography
        stego = UniversalFileSteganography("test123")
        output_file = "processed_binary_doc.rtf"
        
        print(f"🔐 Embedding secret in binary document...")
        result = stego.hide_file_in_file(doc_file, secret_file, output_file)
        
        if not result.get('success'):
            print(f"❌ Embedding failed: {result}")
            return False
        
        print(f"✅ Embedding successful using {result.get('method', 'unknown')} method")
        
        # Check processed file
        if not os.path.exists(output_file):
            print(f"❌ Output file not created")
            return False
        
        processed_size = os.path.getsize(output_file)
        print(f"📏 Processed size: {processed_size} bytes")
        
        # Read processed binary content  
        with open(output_file, 'rb') as f:
            processed_data = f.read()
        
        print(f"🔍 Processed binary signature: {processed_data[:20].hex()}")
        
        # Compare binary signatures
        if original_data[:20] == processed_data[:20]:
            print(f"✅ Binary signature preserved")
        else:
            print(f"⚠️ Binary signature changed")
            print(f"   Original:  {original_data[:20].hex()}")  
            print(f"   Processed: {processed_data[:20].hex()}")
        
        # Test if file is still valid RTF by trying to read it
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if "\\rtf1" in content:
                print(f"✅ RTF format preserved")
            else:
                print(f"❌ RTF format corrupted")
        except Exception as e:
            print(f"❌ Cannot read as text: {e}")
        
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
        for file in [doc_file, secret_file, "processed_binary_doc.rtf"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = test_binary_document_corruption()
    if success:
        print(f"\n🎉 BINARY DOCUMENT TEST PASSED!")
    else:
        print(f"\n❌ BINARY DOCUMENT TEST FAILED!")
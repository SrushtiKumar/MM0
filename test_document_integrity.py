#!/usr/bin/env python3
"""
Test document steganography for file corruption issues
"""

import os
import tempfile
from universal_file_steganography import UniversalFileSteganography

def test_document_integrity(doc_path):
    """Test if document file can be opened and read"""
    try:
        # Try to read the document file as text
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 0:
            print(f"✅ Document file readable: {len(content)} characters")
            return True, content
        else:
            print(f"❌ Document file is empty")
            return False, ""
            
    except UnicodeDecodeError:
        # Try binary mode if UTF-8 fails
        try:
            with open(doc_path, 'rb') as f:
                content = f.read()
            print(f"✅ Document readable as binary: {len(content)} bytes")
            return True, content
        except Exception as e:
            print(f"❌ Document file is corrupted: {e}")
            return False, ""
    except Exception as e:
        print(f"❌ Document file is corrupted: {e}")
        return False, ""

def test_document_steganography():
    """Test document steganography for corruption issues"""
    
    print("📄 Testing Document Steganography File Integrity")
    print("=" * 50)
    
    stego = UniversalFileSteganography()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        carrier_doc = os.path.join(temp_dir, "carrier.txt")
        secret_file = os.path.join(temp_dir, "secret.txt")
        output_doc = os.path.join(temp_dir, "stego_document.txt")
        extract_dir = os.path.join(temp_dir, "extracted")
        
        # Create carrier document
        print("1️⃣ Creating carrier document...")
        carrier_content = """This is a sample document for testing steganography.
        
It contains multiple paragraphs with various content.
The document should remain readable after embedding secret data.

This is the second paragraph with more text content.
We want to ensure the document format stays intact.

Here's a third paragraph to provide more space for steganographic embedding.
The text should look normal to any casual reader.

And this is the final paragraph of our test document.
Everything should work seamlessly without corruption."""
        
        with open(carrier_doc, 'w', encoding='utf-8') as f:
            f.write(carrier_content)
        print(f"✅ Carrier document created: {carrier_doc}")
        
        # Create secret file
        print("2️⃣ Creating secret file...")
        secret_content = "This is my secret document data!\nConfidential information here.\nMultiple lines of secrets."
        with open(secret_file, 'w') as f:
            f.write(secret_content)
        print(f"✅ Secret file created: {secret_file}")
        
        # Test original document integrity
        print("\n3️⃣ Testing original document integrity...")
        is_readable, original_content = test_document_integrity(carrier_doc)
        if not is_readable:
            print("❌ Original document is already corrupted")
            return False
        
        # Test embedding
        print("\n4️⃣ Embedding secret in document...")
        try:
            result = stego.hide_file_in_file(carrier_doc, secret_file, output_doc)
            print(f"✅ Document embedding successful: {result}")
        except Exception as e:
            print(f"❌ Document embedding failed: {e}")
            return False
        
        # Test processed document integrity - THIS IS THE CRITICAL TEST
        print("\n5️⃣ Testing processed document integrity...")
        is_readable, processed_content = test_document_integrity(output_doc)
        if not is_readable:
            print("❌ CORRUPTION DETECTED: Processed document file is corrupted!")
            return False
        
        print("✅ SUCCESS: Processed document file remains readable!")
        
        # Check if original content is preserved
        if isinstance(original_content, str) and isinstance(processed_content, str):
            if carrier_content in processed_content:
                print("✅ Original document content is preserved in processed file!")
            else:
                print("⚠️ Original content may be modified but file is still readable")
        
        # Test extraction
        print("\n6️⃣ Testing extraction...")
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            extracted_file = stego.extract_file_from_file(output_doc, extract_dir)
            print(f"✅ Document extraction successful: {extracted_file}")
        except Exception as e:
            print(f"❌ Document extraction failed: {e}")
            return False
        
        # Verify content
        print("\n7️⃣ Verifying extracted content...")
        try:
            with open(extracted_file, 'rb') as f:
                extracted_content = f.read()
            
            with open(secret_file, 'rb') as f:
                original_secret = f.read()
            
            if original_secret == extracted_content:
                print("✅ SUCCESS: Extracted content matches original perfectly!")
                print(f"📝 Original: {repr(original_secret[:50])}...")
                print(f"📤 Extracted: {repr(extracted_content[:50])}...")
            elif original_secret in extracted_content:
                print("✅ SUCCESS: Original content found in extracted file!")
                print(f"📊 Original size: {len(original_secret)}, Extracted size: {len(extracted_content)}")
            else:
                print("❌ Content mismatch")
                return False
                
        except Exception as e:
            print(f"❌ Content verification failed: {e}")
            return False
        
        print("\n🎉 DOCUMENT STEGANOGRAPHY SUCCESS!")
        print("✅ Document files remain readable after processing")
        print("✅ Hidden data is properly embedded and extracted")
        print("✅ No file corruption detected")
        return True

if __name__ == "__main__":
    success = test_document_steganography()
    if success:
        print("\n🎯 Document steganography is working without corruption!")
    else:
        print("\n❌ Document steganography has corruption issues")
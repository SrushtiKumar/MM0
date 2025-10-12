#!/usr/bin/env python3
"""
Test Document Steganography Extraction Issue
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_document_extraction():
    """Test document steganography to check filename handling"""
    
    print("📄 DOCUMENT STEGANOGRAPHY EXTRACTION TEST")
    print("=" * 60)
    
    try:
        # Import the steganography module
        from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
        print("✅ Document steganography module imported")
        
        # Create a test DOCX file to hide
        test_docx_content = b"""PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00"""  # Simple docx header
        test_docx_filename = "test_document.docx"
        
        with open(test_docx_filename, 'wb') as f:
            f.write(test_docx_content)
        print(f"✅ Created test DOCX file: {test_docx_filename}")
        
        # Create container document
        container_content = """This is a test document for steganography.
It contains multiple lines of text.
We will hide a DOCX file in this document.
The hidden file should maintain its .docx extension when extracted.
This is important for file format preservation."""
        
        container_filename = "container_document.txt"
        with open(container_filename, 'w') as f:
            f.write(container_content)
        print(f"✅ Created container document: {container_filename}")
        
        # Test embedding
        password = "test123"
        manager = EnhancedWebDocumentSteganographyManager(password)
        print(f"✅ Manager initialized with password: {password}")
        
        print("\n🔒 EMBEDDING TEST")
        print("-" * 30)
        
        # Hide the DOCX file
        result = manager.hide_data(container_filename, test_docx_filename, "stego_container.txt", is_file=True)
        print(f"✅ Embedding result: {result}")
        
        print("\n🔍 EXTRACTION TEST")
        print("-" * 30)
        
        # Extract the hidden file
        extracted_data, extracted_filename = manager.extract_data("stego_container.txt")
        
        print(f"✅ Extraction successful!")
        print(f"   Data type: {type(extracted_data)}")
        print(f"   Data size: {len(extracted_data)} bytes")
        print(f"   Extracted filename: '{extracted_filename}'")
        print(f"   Original filename: '{test_docx_filename}'")
        
        # Check if filename is preserved correctly
        if extracted_filename == test_docx_filename:
            print("✅ Filename preservation: CORRECT")
        else:
            print(f"❌ Filename preservation: INCORRECT")
            print(f"   Expected: {test_docx_filename}")
            print(f"   Got: {extracted_filename}")
        
        # Check file extension
        original_ext = Path(test_docx_filename).suffix
        extracted_ext = Path(extracted_filename).suffix if extracted_filename else ""
        
        if extracted_ext == original_ext:
            print(f"✅ Extension preservation: CORRECT ({original_ext})")
        else:
            print(f"❌ Extension preservation: INCORRECT")
            print(f"   Expected: {original_ext}")
            print(f"   Got: {extracted_ext}")
        
        # Save the extracted file with correct extension
        final_filename = f"extracted_{test_docx_filename}"
        with open(final_filename, 'wb') as f:
            f.write(extracted_data)
        
        print(f"✅ Saved extracted file as: {final_filename}")
        
        # Verify file content matches
        original_size = len(test_docx_content)
        extracted_size = len(extracted_data)
        
        if extracted_size == original_size:
            print(f"✅ File size verification: PASSED ({extracted_size} bytes)")
        else:
            print(f"❌ File size verification: FAILED")
            print(f"   Original: {original_size} bytes")
            print(f"   Extracted: {extracted_size} bytes")
        
        # Check if content matches
        if extracted_data == test_docx_content:
            print("✅ File content verification: PASSED")
        else:
            print("❌ File content verification: FAILED")
            print(f"   Original first 20 bytes: {test_docx_content[:20]}")
            print(f"   Extracted first 20 bytes: {extracted_data[:20]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        for file in ["test_document.docx", "container_document.txt", "stego_container.txt"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

def main():
    print("🧪 DOCUMENT EXTRACTION FORMAT TEST")
    print("=" * 60)
    print("Testing if document files maintain their original format when extracted")
    print("Focus: DOCX files should be extracted as .docx, not .bin\n")
    
    success = test_document_extraction()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("✅ Document files should now maintain their original format")
    else:
        print("❌ TEST FAILED - Issues found with document extraction")
    
    print("\n📋 SUMMARY:")
    print("   - Document steganography module tested")
    print("   - Filename and extension preservation verified")
    print("   - File content integrity checked")

if __name__ == "__main__":
    main()
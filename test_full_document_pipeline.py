#!/usr/bin/env python3
"""
Test Full Document Steganography Pipeline
Simulates the complete backend process for document files
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def create_test_docx():
    """Create a realistic test DOCX file"""
    # More realistic DOCX content
    docx_content = b"""PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\xb7\x81\xb6\\\x1a\x01\x00\x00L\x04\x00\x00\x10\x00\x08\x02[Content_Types].xml \xa2\x04\x02(\xa0\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""
    
    filename = "important_document.docx"
    with open(filename, 'wb') as f:
        f.write(docx_content)
    
    return filename, docx_content

def simulate_backend_embedding(carrier_file, content_file, password):
    """Simulate the backend embedding process"""
    
    print("🔄 SIMULATING BACKEND EMBEDDING PROCESS")
    print("-" * 50)
    
    try:
        from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
        
        # Step 1: Initialize manager with password (like backend does)
        manager = EnhancedWebDocumentSteganographyManager(password)
        print(f"✅ Manager initialized with password: {password}")
        
        # Step 2: Read content file as bytes (like backend does for content_type="file")
        with open(content_file, "rb") as f:
            content_to_hide = f.read()
        print(f"✅ Read content file: {len(content_to_hide)} bytes")
        
        # Step 3: Determine content type and prepare parameters
        content_type = "file"  # Since we're hiding a file
        is_file = (content_type == "file")
        original_filename = Path(content_file).name
        
        print(f"✅ Content type: {content_type}")
        print(f"✅ Is file: {is_file}")
        print(f"✅ Original filename: {original_filename}")
        
        # Step 4: Generate output path
        output_path = f"stego_{Path(carrier_file).name}"
        
        # Step 5: Call hide_data like backend does
        # For document steganography: hide_data(container_path, data, output_path, is_file, original_filename)
        # Test the new original_filename parameter
        result = manager.hide_data(
            carrier_file,        # container_path
            content_to_hide,     # data (bytes for file content)
            output_path,         # output_path
            is_file,             # is_file flag
            original_filename    # original_filename parameter
        )
        
        print(f"✅ Embedding completed: {result}")
        
        return output_path, original_filename
        
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def simulate_backend_extraction(stego_file, password, original_filename):
    """Simulate the backend extraction process"""
    
    print("\n🔍 SIMULATING BACKEND EXTRACTION PROCESS")
    print("-" * 50)
    
    try:
        from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
        
        # Step 1: Initialize manager with password
        manager = EnhancedWebDocumentSteganographyManager(password)
        print(f"✅ Manager initialized with password: {password}")
        
        # Step 2: Extract data (like backend does)
        extraction_result = manager.extract_data(stego_file)
        
        if extraction_result is None or (isinstance(extraction_result, tuple) and extraction_result[0] is None):
            print("❌ Extraction failed - wrong password or no hidden data")
            return False
        
        # Step 3: Handle tuple return (data, filename) like backend does
        if isinstance(extraction_result, tuple):
            extracted_data, extracted_filename = extraction_result
        else:
            extracted_data = extraction_result
            extracted_filename = None
        
        print(f"✅ Extraction successful!")
        print(f"   Data type: {type(extracted_data)}")
        print(f"   Data size: {len(extracted_data)} bytes")
        print(f"   Extracted filename: '{extracted_filename}'")
        print(f"   Original filename: '{original_filename}'")
        
        # Step 4: Check if filename is correctly preserved (like backend logic)
        is_text_message = (
            extracted_filename == "extracted_message.txt" or
            extracted_filename == "embedded_text.txt"
        )
        
        print(f"✅ Is text message: {is_text_message}")
        
        # Step 5: Determine output filename (like backend does)
        if extracted_filename and extracted_filename.strip():
            output_filename = extracted_filename
            # Basic sanitization like backend
            import re
            output_filename = re.sub(r'[<>:"/\\|?*]', '_', output_filename)
            
            if not output_filename or output_filename.startswith('.') or len(output_filename.strip()) == 0:
                original_ext = Path(original_filename).suffix if original_filename else ".bin"
                output_filename = f"extracted_file_{int(time.time())}{original_ext}"
        else:
            if isinstance(extracted_data, str):
                output_filename = f"extracted_text_{int(time.time())}.txt"
            else:
                output_filename = f"extracted_file_{int(time.time())}.bin"
        
        print(f"✅ Final output filename: '{output_filename}'")
        
        # Step 6: Save file (like backend does)
        if isinstance(extracted_data, str):
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(extracted_data)
        elif isinstance(extracted_data, bytes):
            if is_text_message:
                try:
                    decoded_text = extracted_data.decode('utf-8')
                    with open(output_filename, "w", encoding="utf-8") as f:
                        f.write(decoded_text)
                except UnicodeDecodeError:
                    with open(output_filename, "wb") as f:
                        f.write(extracted_data)
            else:
                with open(output_filename, "wb") as f:
                    f.write(extracted_data)
        
        print(f"✅ File saved as: {output_filename}")
        
        # Step 7: Verify the results
        saved_size = os.path.getsize(output_filename)
        expected_ext = Path(original_filename).suffix
        actual_ext = Path(output_filename).suffix
        
        print(f"\n📊 VERIFICATION:")
        print(f"   Expected extension: {expected_ext}")
        print(f"   Actual extension: {actual_ext}")
        print(f"   File size: {saved_size} bytes")
        
        if actual_ext == expected_ext:
            print("✅ Extension preservation: CORRECT")
        else:
            print("❌ Extension preservation: INCORRECT")
            
        return output_filename
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    
    print("🧪 FULL DOCUMENT STEGANOGRAPHY PIPELINE TEST")
    print("=" * 70)
    print("This test simulates the complete backend process for document files")
    print("to identify where .docx files are being saved as .bin files\n")
    
    # Create test files
    print("📁 CREATING TEST FILES")
    print("-" * 30)
    
    # Create a DOCX file to hide
    docx_file, docx_content = create_test_docx()
    print(f"✅ Created DOCX file: {docx_file} ({len(docx_content)} bytes)")
    
    # Create container document
    container_content = """This is a professional document that will serve as a container.
It contains multiple paragraphs of text to provide adequate space for steganography.
The hidden document should maintain its original format when extracted.
Document steganography is an important technique for secure communication.
This container provides sufficient whitespace for embedding our secret document."""
    
    container_file = "container.txt"
    with open(container_file, 'w') as f:
        f.write(container_content)
    print(f"✅ Created container: {container_file}")
    
    # Test the full pipeline
    password = "secure123"
    
    # Embedding
    stego_file, original_filename = simulate_backend_embedding(container_file, docx_file, password)
    
    if stego_file and os.path.exists(stego_file):
        print(f"✅ Stego file created: {stego_file}")
        
        # Extraction
        extracted_file = simulate_backend_extraction(stego_file, password, original_filename)
        
        if extracted_file:
            print(f"\n🎯 FINAL RESULT:")
            print(f"   Original file: {docx_file}")
            print(f"   Extracted file: {extracted_file}")
            
            # Check if the issue is resolved
            original_ext = Path(docx_file).suffix
            extracted_ext = Path(extracted_file).suffix
            
            if extracted_ext == original_ext:
                print(f"🎉 SUCCESS: File format preserved ({original_ext})")
            else:
                print(f"❌ ISSUE: File format changed from {original_ext} to {extracted_ext}")
        else:
            print("❌ Extraction failed")
    else:
        print("❌ Embedding failed")
    
    # Cleanup
    print(f"\n🧹 CLEANING UP...")
    for file in [docx_file, container_file, stego_file]:
        if file and os.path.exists(file):
            try:
                os.remove(file)
                print(f"   Removed: {file}")
            except:
                pass

if __name__ == "__main__":
    main()
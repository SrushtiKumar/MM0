#!/usr/bin/env python3
"""
Comprehensive File Format Preservation Test
Test all steganography types to ensure file formats are preserved correctly
"""

import sys
import os
from pathlib import Path
from PIL import Image

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def create_test_files():
    """Create test files for all steganography types"""
    
    files = {}
    
    # 1. Create DOC file
    doc_content = b"Microsoft Word document content for testing format preservation."
    files['doc'] = "report.doc"
    with open(files['doc'], 'wb') as f:
        f.write(doc_content)
    
    # 2. Create PDF file
    pdf_content = b"%PDF-1.4\nTest PDF content for format preservation testing."
    files['pdf'] = "manual.pdf"
    with open(files['pdf'], 'wb') as f:
        f.write(pdf_content)
    
    # 3. Create DOCX file
    docx_content = b"PK\x03\x04DOCX content simulation for testing."
    files['docx'] = "presentation.docx"
    with open(files['docx'], 'wb') as f:
        f.write(docx_content)
    
    # 4. Create carrier files
    # PNG image
    img = Image.new('RGB', (200, 200), color='red')
    files['png'] = "carrier.png"
    img.save(files['png'])
    
    # Text document
    text_content = """This is a text document that will serve as a carrier.
It contains multiple lines of text to provide space for steganography.
The hidden files should maintain their original format when extracted.
This is important for usability and file integrity."""
    files['txt'] = "container.txt"
    with open(files['txt'], 'w') as f:
        f.write(text_content)
    
    return files

def test_image_steganography(files):
    """Test image steganography format preservation"""
    
    print("🖼️ IMAGE STEGANOGRAPHY TEST")
    print("-" * 40)
    
    try:
        from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
        
        results = {}
        password = "test123"
        manager = EnhancedWebImageSteganographyManager(password)
        
        # Test different file types
        test_files = ['doc', 'pdf', 'docx']
        
        for file_type in test_files:
            print(f"Testing {file_type.upper()} file in PNG image...")
            
            with open(files[file_type], 'rb') as f:
                file_content = f.read()
            
            output_file = f"image_stego_{file_type}.png"
            
            # Hide file
            result = manager.hide_data(
                files['png'],
                file_content,
                output_file,
                is_file=True,
                original_filename=files[file_type]
            )
            
            if result['success']:
                # Extract and check format
                extracted_data, extracted_filename = manager.extract_data(output_file)
                
                original_ext = Path(files[file_type]).suffix
                extracted_ext = Path(extracted_filename).suffix
                
                format_preserved = (extracted_ext == original_ext)
                results[file_type] = format_preserved
                
                print(f"   Original: {files[file_type]} → Extracted: {extracted_filename}")
                print(f"   Format preserved: {'✅' if format_preserved else '❌'}")
                
                # Clean up
                if os.path.exists(output_file):
                    os.remove(output_file)
            else:
                results[file_type] = False
                print(f"   ❌ Embedding failed for {file_type}")
        
        return results
        
    except Exception as e:
        print(f"❌ Image steganography test failed: {e}")
        return {}

def test_document_steganography(files):
    """Test document steganography format preservation"""
    
    print(f"\n📄 DOCUMENT STEGANOGRAPHY TEST")
    print("-" * 40)
    
    try:
        from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
        
        results = {}
        password = "test123"
        manager = EnhancedWebDocumentSteganographyManager(password)
        
        # Test different file types
        test_files = ['doc', 'pdf', 'docx']
        
        for file_type in test_files:
            print(f"Testing {file_type.upper()} file in TXT document...")
            
            with open(files[file_type], 'rb') as f:
                file_content = f.read()
            
            output_file = f"doc_stego_{file_type}.txt"
            
            # Hide file
            result = manager.hide_data(
                files['txt'],
                file_content,
                output_file,
                is_file=True,
                original_filename=files[file_type]
            )
            
            if result['success']:
                # Extract and check format
                extracted_data, extracted_filename = manager.extract_data(output_file)
                
                original_ext = Path(files[file_type]).suffix
                extracted_ext = Path(extracted_filename).suffix
                
                format_preserved = (extracted_ext == original_ext)
                results[file_type] = format_preserved
                
                print(f"   Original: {files[file_type]} → Extracted: {extracted_filename}")
                print(f"   Format preserved: {'✅' if format_preserved else '❌'}")
                
                # Clean up
                if os.path.exists(output_file):
                    os.remove(output_file)
            else:
                results[file_type] = False
                print(f"   ❌ Embedding failed for {file_type}")
        
        return results
        
    except Exception as e:
        print(f"❌ Document steganography test failed: {e}")
        return {}

def main():
    """Main test function"""
    
    print("🧪 COMPREHENSIVE FILE FORMAT PRESERVATION TEST")
    print("=" * 70)
    print("Testing all steganography types to ensure file formats are preserved")
    print("Goal: DOC files should extract as .doc, PDF as .pdf, DOCX as .docx\n")
    
    # Create test files
    files = create_test_files()
    print("✅ Created test files:")
    for key, filename in files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   {key.upper()}: {filename} ({size} bytes)")
    
    # Test all steganography types
    image_results = test_image_steganography(files)
    document_results = test_document_steganography(files)
    
    # Summary
    print(f"\n📊 COMPREHENSIVE RESULTS")
    print("=" * 50)
    
    all_formats = ['doc', 'pdf', 'docx']
    
    print("Image Steganography:")
    for fmt in all_formats:
        status = "✅ PASS" if image_results.get(fmt, False) else "❌ FAIL"
        print(f"   {fmt.upper()} format: {status}")
    
    print("\nDocument Steganography:")
    for fmt in all_formats:
        status = "✅ PASS" if document_results.get(fmt, False) else "❌ FAIL"
        print(f"   {fmt.upper()} format: {status}")
    
    # Overall assessment
    image_success = all(image_results.get(fmt, False) for fmt in all_formats)
    doc_success = all(document_results.get(fmt, False) for fmt in all_formats)
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    print(f"   Image Steganography: {'✅ ALL FORMATS PRESERVED' if image_success else '❌ SOME ISSUES'}")
    print(f"   Document Steganography: {'✅ ALL FORMATS PRESERVED' if doc_success else '❌ SOME ISSUES'}")
    
    if image_success and doc_success:
        print(f"\n🎉 SUCCESS: ALL FILE FORMATS ARE NOW PRESERVED CORRECTLY!")
        print("✅ DOC files extract as .doc")
        print("✅ PDF files extract as .pdf") 
        print("✅ DOCX files extract as .docx")
        print("✅ The .bin format issue has been resolved!")
    else:
        print(f"\n⚠️ Some format preservation issues remain")
    
    # Cleanup
    for filename in files.values():
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

if __name__ == "__main__":
    main()
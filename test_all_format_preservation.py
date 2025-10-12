#!/usr/bin/env python3
"""
Comprehensive File Format Preservation Test
Tests all steganography modules to ensure original file formats are preserved
"""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def create_test_doc_file():
    """Create a test .doc file"""
    # Simple DOC file content (basic DOC format header)
    doc_content = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00>\x00\x03\x00\xfe\xff\t\x00' + b'This is a test DOC file content for steganography testing. ' * 10
    
    filename = "test_document.doc"
    with open(filename, 'wb') as f:
        f.write(doc_content)
    
    return filename, doc_content

def create_test_container_files():
    """Create container files for different steganography types"""
    containers = {}
    
    # PNG for image steganography
    png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91h6\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x12IDATx\xdab\xf8\x00\x02\x00\x00\x05\x00\x01\r\n-\xb5\x00\x00\x00\x00IEND\xaeB`\x82'
    containers['image'] = 'test_container.png'
    with open(containers['image'], 'wb') as f:
        f.write(png_content)
    
    # TXT for document steganography  
    txt_content = """Professional Document Container for Steganography Testing
========================================================

This document serves as a comprehensive container for hiding sensitive information.
The document contains multiple paragraphs and sections to provide adequate space.
Advanced steganographic techniques are employed to ensure data security and integrity.
Corporate policies require secure communication channels for confidential information.
Technical specifications and implementation details are documented in subsequent sections.

Executive Summary
================

Our quarterly analysis demonstrates significant growth across all operational metrics.
Strategic initiatives have yielded positive outcomes in market penetration and revenue.
Investment in technology infrastructure has improved efficiency and customer satisfaction.
Partnership development has created new opportunities for sustainable business expansion.
Risk management protocols have been enhanced to address emerging security challenges."""
    
    containers['document'] = 'test_container.txt'
    with open(containers['document'], 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    return containers

def test_image_steganography(doc_file, doc_content, container_file):
    """Test image steganography with DOC file"""
    print("🖼️  TESTING IMAGE STEGANOGRAPHY")
    print("-" * 40)
    
    try:
        from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
        
        password = "TestPassword123"
        manager = EnhancedWebImageSteganographyManager(password)
        
        # Test embedding with original filename
        print(f"📤 Embedding {doc_file} in {container_file}")
        
        result = manager.hide_data(
            container_file,     # container_path
            doc_content,        # data (bytes)
            "stego_image.png",  # output_path
            is_file=True,       # is_file
            original_filename=doc_file  # original_filename
        )
        
        if not result.get('success', False):
            print(f"❌ Embedding failed: {result}")
            return False
        
        print(f"✅ Embedding successful: {result['output_path']}")
        
        # Test extraction
        print(f"📥 Extracting from {result['output_path']}")
        
        extracted_data, extracted_filename = manager.extract_data(result['output_path'])
        
        print(f"📊 Extraction Results:")
        print(f"   Original filename: {doc_file}")
        print(f"   Extracted filename: {extracted_filename}")
        print(f"   Data size: {len(extracted_data)} bytes")
        
        # Check format preservation
        original_ext = Path(doc_file).suffix
        extracted_ext = Path(extracted_filename).suffix if extracted_filename else ""
        
        print(f"   Original extension: {original_ext}")
        print(f"   Extracted extension: {extracted_ext}")
        
        if extracted_ext == original_ext:
            print(f"✅ Format preserved: {original_ext}")
            return True
        else:
            print(f"❌ Format NOT preserved: {original_ext} → {extracted_ext}")
            return False
            
    except Exception as e:
        print(f"❌ Image steganography test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_steganography(doc_file, doc_content, container_file):
    """Test document steganography with DOC file"""
    print("\n📄 TESTING DOCUMENT STEGANOGRAPHY")
    print("-" * 42)
    
    try:
        from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
        
        password = "TestPassword123"
        manager = EnhancedWebDocumentSteganographyManager(password)
        
        # Test embedding with original filename
        print(f"📤 Embedding {doc_file} in {container_file}")
        
        result = manager.hide_data(
            container_file,     # container_path
            doc_content,        # data (bytes)
            "stego_document.txt",  # output_path
            is_file=True,       # is_file
            original_filename=doc_file  # original_filename
        )
        
        if not result.get('success', False):
            print(f"❌ Embedding failed: {result}")
            return False
        
        print(f"✅ Embedding successful: {result['output_path']}")
        
        # Test extraction
        print(f"📥 Extracting from {result['output_path']}")
        
        extracted_data, extracted_filename = manager.extract_data(result['output_path'])
        
        print(f"📊 Extraction Results:")
        print(f"   Original filename: {doc_file}")
        print(f"   Extracted filename: {extracted_filename}")
        print(f"   Data size: {len(extracted_data)} bytes")
        
        # Check format preservation
        original_ext = Path(doc_file).suffix
        extracted_ext = Path(extracted_filename).suffix if extracted_filename else ""
        
        print(f"   Original extension: {original_ext}")
        print(f"   Extracted extension: {extracted_ext}")
        
        if extracted_ext == original_ext:
            print(f"✅ Format preserved: {original_ext}")
            return True
        else:
            print(f"❌ Format NOT preserved: {original_ext} → {extracted_ext}")
            return False
            
    except Exception as e:
        print(f"❌ Document steganography test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("🧪 COMPREHENSIVE FILE FORMAT PRESERVATION TEST")
    print("=" * 70)
    print("Testing DOC file hiding in PNG image and TXT document")
    print("Goal: Extracted file should be .doc, not .bin\n")
    
    # Create test files
    print("📁 CREATING TEST FILES")
    print("-" * 30)
    
    doc_file, doc_content = create_test_doc_file()
    containers = create_test_container_files()
    
    print(f"✅ Created DOC file: {doc_file} ({len(doc_content)} bytes)")
    print(f"✅ Created PNG container: {containers['image']}")
    print(f"✅ Created TXT container: {containers['document']}")
    
    # Test image steganography
    image_success = test_image_steganography(doc_file, doc_content, containers['image'])
    
    # Test document steganography
    document_success = test_document_steganography(doc_file, doc_content, containers['document'])
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 TEST SUMMARY")
    print("-" * 20)
    print(f"Image Steganography: {'✅ PASSED' if image_success else '❌ FAILED'}")
    print(f"Document Steganography: {'✅ PASSED' if document_success else '❌ FAILED'}")
    
    if image_success and document_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ DOC files now extract as .doc (not .bin)")
        print("✅ File format preservation is working correctly")
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print("File format preservation needs additional fixes")
    
    # Cleanup
    print(f"\n🧹 CLEANING UP...")
    cleanup_files = [doc_file, containers['image'], containers['document'], 
                    'stego_image.png', 'stego_document.txt']
    
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"   Removed: {file}")
            except:
                pass

if __name__ == "__main__":
    main()
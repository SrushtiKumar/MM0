#!/usr/bin/env python3

import sys
import os
from simple_stego import SimpleImageSteganography

def test_pdf_hiding():
    """Test hiding a PDF file in an image."""
    
    # Create a test PDF content (simulate 412KB)
    test_pdf_content = b"PDF test content " * 24000  # Approximately 400KB
    print(f"Test PDF size: {len(test_pdf_content):,} bytes ({len(test_pdf_content)/1024:.1f} KB)")
    
    # Use the test image we created
    image_path = "test_11mb_image.png"
    output_path = "test_output_with_pdf.png" 
    
    try:
        # Test the simple steganography
        stego = SimpleImageSteganography()
        
        print("Starting embedding process...")
        result = stego.embed_data(
            image_path=image_path,
            data=test_pdf_content,
            output_path=output_path,
            filename="test_document.pdf"
        )
        
        print("Embedding result:", result)
        
        if result['success']:
            print("✅ PDF embedding successful!")
            
            # Test extraction
            print("Testing extraction...")
            extracted_data, filename, file_extension = stego.extract_data(output_path)
            
            print(f"Extracted data size: {len(extracted_data):,} bytes")
            print(f"Original filename: {filename}")
            print(f"File extension: {file_extension}")
            print(f"Data matches: {'✅ YES' if extracted_data == test_pdf_content else '❌ NO'}")
            
        else:
            print("❌ PDF embedding failed!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_hiding()
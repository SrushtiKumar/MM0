#!/usr/bin/env python3
"""
Test with Real PNG File for DOC Format Preservation
"""

import sys
import os
from pathlib import Path
from PIL import Image

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def create_real_test_files():
    """Create valid test files"""
    
    # Create a DOC file
    doc_content = b"""This is a test document file.
It should maintain its .doc extension when extracted from image steganography.
The file format preservation is critical for usability."""
    
    doc_filename = "important_document.doc"
    with open(doc_filename, 'wb') as f:
        f.write(doc_content)
    
    # Create a valid PNG image using PIL
    png_filename = "test_image.png"
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(png_filename)
    
    return doc_filename, png_filename

def test_format_preservation():
    """Test format preservation with real files"""
    
    print("🧪 REAL FILE FORMAT PRESERVATION TEST")
    print("=" * 50)
    
    try:
        from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
        
        doc_file, png_file = create_real_test_files()
        print(f"✅ Created files:")
        print(f"   DOC: {doc_file} ({os.path.getsize(doc_file)} bytes)")
        print(f"   PNG: {png_file} ({os.path.getsize(png_file)} bytes)")
        
        password = "test123"
        manager = EnhancedWebImageSteganographyManager(password)
        
        # Test backend-style embedding (content + filename)
        print(f"\n🔒 Testing backend-style embedding...")
        
        with open(doc_file, 'rb') as f:
            file_content = f.read()
        
        result = manager.hide_data(
            png_file,
            file_content,
            "stego_output.png",
            is_file=True,
            original_filename=doc_file
        )
        
        print(f"   Embedding result: {result['success']}")
        
        if result['success']:
            # Test extraction
            print(f"\n🔍 Testing extraction...")
            extracted_data, extracted_filename = manager.extract_data("stego_output.png")
            
            print(f"   Extracted filename: '{extracted_filename}'")
            print(f"   Expected filename: '{doc_file}'")
            
            # Check extensions
            original_ext = Path(doc_file).suffix
            extracted_ext = Path(extracted_filename).suffix
            
            print(f"   Original extension: {original_ext}")
            print(f"   Extracted extension: {extracted_ext}")
            
            if extracted_ext == original_ext:
                print(f"   ✅ SUCCESS: Extension preserved!")
                
                # Save extracted file to verify
                with open(f"extracted_{extracted_filename}", 'wb') as f:
                    f.write(extracted_data)
                
                print(f"   ✅ Extracted file saved as: extracted_{extracted_filename}")
                return True
            else:
                print(f"   ❌ ISSUE: Extension changed from {original_ext} to {extracted_ext}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        for file in ["important_document.doc", "test_image.png", "stego_output.png"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

def main():
    print("🔧 TESTING DOC FILE FORMAT PRESERVATION IN PNG")
    print("=" * 60)
    print("Verifying that .doc files maintain .doc extension when extracted\n")
    
    success = test_format_preservation()
    
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Format preservation test")
    
    if success:
        print("🎉 DOC files now extract with correct .doc extension!")
    else:
        print("❌ Format preservation needs more investigation")

if __name__ == "__main__":
    main()
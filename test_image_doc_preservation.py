#!/usr/bin/env python3
"""
Test Image Steganography DOC File Format Preservation
Test hiding a DOC file inside a PNG and verify extraction format
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def create_test_files():
    """Create test files for image steganography"""
    
    # Create a simple DOC file (actually just text content for testing)
    doc_content = b"""DOC file header simulation
This is a test document that simulates a DOC file.
In a real scenario, this would be actual Microsoft Word binary data.
The important thing is that the file extension should be preserved as .doc
and not changed to .bin when extracted from the PNG carrier image."""
    
    doc_filename = "test_document.doc"
    with open(doc_filename, 'wb') as f:
        f.write(doc_content)
    
    # Create a simple PNG image (minimal PNG header)
    png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91h6'
    png_data = png_header + b'\x00' * 1000  # Add some data to make it larger
    
    png_filename = "carrier_image.png"
    with open(png_filename, 'wb') as f:
        f.write(png_data)
    
    return doc_filename, png_filename

def test_image_steganography():
    """Test image steganography with DOC file preservation"""
    
    print("🖼️ IMAGE STEGANOGRAPHY DOC FILE TEST")
    print("=" * 50)
    
    try:
        from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
        
        # Create test files
        doc_filename, png_filename = create_test_files()
        print(f"✅ Created test files:")
        print(f"   DOC file: {doc_filename} ({os.path.getsize(doc_filename)} bytes)")
        print(f"   PNG carrier: {png_filename} ({os.path.getsize(png_filename)} bytes)")
        
        password = "test123"
        manager = EnhancedWebImageSteganographyManager(password)
        
        print(f"\n🔒 EMBEDDING TEST")
        print("-" * 30)
        
        # Test 1: Using file path (should work)
        print("Test 1: Hiding DOC file using file path...")
        result1 = manager.hide_data(png_filename, doc_filename, "stego1.png", is_file=True)
        print(f"   Result: {result1['success']}")
        
        if result1['success'] and os.path.exists("stego1.png"):
            extracted1, filename1 = manager.extract_data("stego1.png")
            print(f"   Extracted filename: '{filename1}'")
            print(f"   Expected: '{doc_filename}'")
            print(f"   Correct format: {filename1 == doc_filename}")
        
        # Test 2: Using file content + original filename (backend style)
        print(f"\nTest 2: Hiding DOC file using content + filename...")
        
        with open(doc_filename, 'rb') as f:
            doc_content = f.read()
        
        result2 = manager.hide_data(
            png_filename, 
            doc_content,           # bytes content
            "stego2.png", 
            is_file=True,
            original_filename=doc_filename  # Pass original filename
        )
        print(f"   Result: {result2['success']}")
        
        if result2['success'] and os.path.exists("stego2.png"):
            extracted2, filename2 = manager.extract_data("stego2.png")
            print(f"   Extracted filename: '{filename2}'")
            print(f"   Expected: '{doc_filename}'")
            print(f"   Correct format: {filename2 == doc_filename}")
            
            # Check file extension specifically
            expected_ext = Path(doc_filename).suffix
            actual_ext = Path(filename2).suffix
            print(f"   Expected extension: {expected_ext}")
            print(f"   Actual extension: {actual_ext}")
            
            if actual_ext == expected_ext:
                print(f"   ✅ Extension preserved correctly!")
            else:
                print(f"   ❌ Extension issue: got {actual_ext}, expected {expected_ext}")
        
        # Cleanup
        for file in [doc_filename, png_filename, "stego1.png", "stego2.png"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_simulation():
    """Simulate how the backend processes image steganography"""
    
    print(f"\n🌐 BACKEND SIMULATION TEST")
    print("-" * 30)
    
    try:
        from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
        
        # Create test files
        doc_filename, png_filename = create_test_files()
        
        # Simulate backend process
        password = "backend123"
        carrier_type = "image"
        content_type = "file"
        
        # Step 1: Read content file as bytes (like backend does)
        with open(doc_filename, "rb") as f:
            content_to_hide = f.read()
        
        # Step 2: Determine parameters
        is_file = (content_type == "file")
        original_filename = Path(doc_filename).name
        
        print(f"Backend parameters:")
        print(f"   Content type: {content_type}")
        print(f"   Is file: {is_file}")
        print(f"   Original filename: {original_filename}")
        print(f"   Content size: {len(content_to_hide)} bytes")
        
        # Step 3: Get steganography manager
        manager = EnhancedWebImageSteganographyManager(password)
        
        # Step 4: Check if manager supports original_filename
        import inspect
        sig = inspect.signature(manager.hide_data)
        supports_filename = 'original_filename' in sig.parameters
        print(f"   Supports original_filename: {supports_filename}")
        
        # Step 5: Call hide_data like backend does
        output_path = "backend_stego.png"
        
        if supports_filename:
            result = manager.hide_data(
                png_filename,        # carrier_file_path
                content_to_hide,     # content_to_hide (bytes)
                output_path,         # output_path
                is_file,             # is_file
                original_filename    # original_filename
            )
        else:
            result = manager.hide_data(
                png_filename,        # carrier_file_path
                content_to_hide,     # content_to_hide (bytes)
                output_path,         # output_path
                is_file              # is_file
            )
        
        print(f"   Embedding result: {result['success']}")
        
        # Step 6: Extract and check format
        if result['success'] and os.path.exists(output_path):
            extracted_data, extracted_filename = manager.extract_data(output_path)
            
            print(f"\nExtraction results:")
            print(f"   Data type: {type(extracted_data)}")
            print(f"   Data size: {len(extracted_data)} bytes")
            print(f"   Extracted filename: '{extracted_filename}'")
            print(f"   Original filename: '{original_filename}'")
            
            # Check format preservation
            original_ext = Path(original_filename).suffix
            extracted_ext = Path(extracted_filename).suffix
            
            print(f"   Original extension: {original_ext}")
            print(f"   Extracted extension: {extracted_ext}")
            
            if extracted_ext == original_ext:
                print(f"   ✅ SUCCESS: Format preserved ({original_ext})")
                return True
            else:
                print(f"   ❌ ISSUE: Format changed from {original_ext} to {extracted_ext}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Backend simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        for file in ["test_document.doc", "carrier_image.png", "backend_stego.png"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

def main():
    """Main test function"""
    
    print("🧪 DOC FILE IN PNG IMAGE - FORMAT PRESERVATION TEST")
    print("=" * 70)
    print("Testing: DOC file hidden in PNG should extract as .doc, not .bin\n")
    
    # Test the steganography module directly
    module_test = test_image_steganography()
    
    # Test backend simulation
    backend_test = test_backend_simulation()
    
    print(f"\n" + "=" * 70)
    print("📊 FINAL RESULTS:")
    print(f"   Module test: {'✅ PASSED' if module_test else '❌ FAILED'}")
    print(f"   Backend test: {'✅ PASSED' if backend_test else '❌ FAILED'}")
    
    if module_test and backend_test:
        print("🎉 SUCCESS: DOC files should now extract with .doc extension!")
    else:
        print("❌ ISSUE: Format preservation still needs fixing")

if __name__ == "__main__":
    main()
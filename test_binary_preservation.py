#!/usr/bin/env python3
"""
Test binary format preservation in layered containers
"""

import sys
import os
sys.path.append('.')

def test_binary_format_preservation():
    """Test that binary files (images) are preserved correctly in layered containers"""
    print("🧪 TESTING BINARY FORMAT PRESERVATION")
    print("="*60)
    
    try:
        from enhanced_app import (
            create_layered_data_container,
            extract_layered_data_container,
            is_layered_container
        )
        
        # Create test data
        print("1. Creating test data...")
        
        # Text message
        text_message = "This is a text message that should be preserved"
        print(f"   📄 Text: {text_message}")
        
        # Create a simple PNG image (valid PNG header + minimal data)
        png_data = bytearray([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D,  # IHDR length
            0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x01,  # Width: 1
            0x00, 0x00, 0x00, 0x01,  # Height: 1
            0x08, 0x02, 0x00, 0x00, 0x00,  # Bit depth, color type, etc.
            0x90, 0x77, 0x53, 0xDE,  # CRC
            0x00, 0x00, 0x00, 0x0C,  # IDAT length
            0x49, 0x44, 0x41, 0x54,  # IDAT
            0x78, 0x9C, 0x63, 0x60, 0x60, 0x60, 0x00, 0x00, 0x00, 0x04, 0x00, 0x01,  # Compressed data
            0xDD, 0x8D, 0xB4, 0x1C,  # CRC
            0x00, 0x00, 0x00, 0x00,  # IEND length
            0x49, 0x45, 0x4E, 0x44,  # IEND
            0xAE, 0x42, 0x60, 0x82   # CRC
        ])
        
        png_bytes = bytes(png_data)
        print(f"   🖼️  PNG image: {len(png_bytes)} bytes (starts with {png_bytes[:8].hex()})")
        
        # Verify PNG signature
        if png_bytes.startswith(b'\x89PNG'):
            print(f"   ✅ Valid PNG signature detected")
        else:
            print(f"   ❌ Invalid PNG signature")
            return False
        
        # Test 1: Create layered container with proper format info
        print(f"\n2. Creating layered container with format preservation...")
        
        # Create layers with format information
        layers_info = [
            (png_bytes, "test_image.png"),  # Binary image with filename
            (text_message, "message.txt")   # Text with filename
        ]
        
        layered_container = create_layered_data_container(layers_info)
        print(f"   📦 Created container: {len(layered_container)} chars")
        
        # Test 2: Verify it's detected as layered
        print(f"\n3. Testing layered container detection...")
        is_layered = is_layered_container(layered_container)
        print(f"   🔍 Is layered container: {is_layered}")
        
        if not is_layered:
            print(f"   ❌ Container not detected as layered!")
            return False
        
        # Test 3: Extract layers and verify formats
        print(f"\n4. Extracting layers and verifying formats...")
        extracted_layers = extract_layered_data_container(layered_container)
        print(f"   📁 Extracted {len(extracted_layers)} layers")
        
        # Verify each layer
        success = True
        for i, (layer_content, layer_filename) in enumerate(extracted_layers):
            print(f"\n   Layer {i+1}: {layer_filename}")
            print(f"     Type: {type(layer_content)}")
            print(f"     Size: {len(layer_content)} bytes")
            
            if "image.png" in layer_filename:
                # This should be the PNG image
                if isinstance(layer_content, bytes):
                    print(f"     ✅ PNG preserved as bytes")
                    print(f"     Header: {layer_content[:8].hex()}")
                    
                    if layer_content.startswith(b'\x89PNG'):
                        print(f"     ✅ PNG signature preserved correctly")
                        
                        # Verify full image data matches
                        if layer_content == png_bytes:
                            print(f"     ✅ Complete PNG data preserved perfectly")
                        else:
                            print(f"     ❌ PNG data corrupted (sizes: orig={len(png_bytes)}, extracted={len(layer_content)})")
                            success = False
                    else:
                        print(f"     ❌ PNG signature corrupted")
                        success = False
                else:
                    print(f"     ❌ PNG should be bytes, got {type(layer_content)}")
                    success = False
                    
            elif "message.txt" in layer_filename:
                # This should be the text message
                if isinstance(layer_content, str):
                    print(f"     ✅ Text preserved as string")
                    print(f"     Content: {layer_content}")
                    
                    if layer_content == text_message:
                        print(f"     ✅ Text content preserved perfectly")
                    else:
                        print(f"     ❌ Text content corrupted")
                        success = False
                else:
                    print(f"     ❌ Text should be string, got {type(layer_content)}")
                    success = False
        
        # Test 4: Write to files and verify they can be opened
        print(f"\n5. Testing file write and integrity...")
        
        for layer_content, layer_filename in extracted_layers:
            test_filename = f"test_extracted_{layer_filename}"
            
            try:
                if isinstance(layer_content, str):
                    with open(test_filename, 'w', encoding='utf-8') as f:
                        f.write(layer_content)
                    print(f"   ✅ Text file written: {test_filename}")
                    
                elif isinstance(layer_content, bytes):
                    with open(test_filename, 'wb') as f:
                        f.write(layer_content)
                    print(f"   ✅ Binary file written: {test_filename}")
                    
                    # For PNG, verify it can be read
                    if test_filename.endswith('.png'):
                        # Check file size and header
                        file_size = os.path.getsize(test_filename)
                        print(f"     File size: {file_size} bytes")
                        
                        with open(test_filename, 'rb') as f:
                            header = f.read(8)
                            if header == b'\x89PNG\r\n\x1a\n':
                                print(f"     ✅ PNG file header is valid")
                            else:
                                print(f"     ❌ PNG file header is invalid: {header.hex()}")
                                success = False
                
                # Cleanup test file
                if os.path.exists(test_filename):
                    os.remove(test_filename)
                    
            except Exception as e:
                print(f"   ❌ Error writing {test_filename}: {e}")
                success = False
        
        return success
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_binary_format_preservation()
    
    print(f"\n" + "="*60)
    print("BINARY FORMAT PRESERVATION TEST RESULT")
    print("="*60)
    
    if success:
        print("✅ SUCCESS: Binary formats are preserved correctly!")
        print("   • PNG images maintain their binary format")
        print("   • Text messages remain as readable text")
        print("   • File extensions are preserved")
        print("   • Original data integrity is maintained")
    else:
        print("❌ FAILURE: Binary format preservation has issues")
        print("   The layered container needs further fixes")
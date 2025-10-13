#!/usr/bin/env python3
"""
Direct test of the layered container fix without web server
"""

import sys
import os
sys.path.append('.')

# Test the embedding logic directly
def test_direct_layered_embedding():
    """Test the layered embedding logic directly"""
    print("🧪 DIRECT TEST OF LAYERED CONTAINER LOGIC")
    print("="*50)
    
    try:
        # Import the steganography modules
        from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
        from enhanced_app import (
            create_layered_data_container,
            extract_layered_data_container, 
            is_layered_container
        )
        
        password = "testpass123"
        
        # Create test files
        print("1. Creating test files...")
        
        # Create simple test image (larger for sufficient capacity)
        try:
            from PIL import Image
            import numpy as np
            
            # Create a 100x100 RGB image
            img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save("test.png")
            print(f"   ✅ Created test.png (100x100)")
            
        except ImportError:
            # Create a simple but larger PNG file manually
            # This is a simple 20x20 white image - should be enough
            import struct
            
            width, height = 20, 20
            
            # PNG signature
            png_data = b'\x89PNG\r\n\x1a\n'
            
            # IHDR chunk
            ihdr_data = struct.pack('>2I5B', width, height, 8, 2, 0, 0, 0)
            ihdr_crc = 0x9dadc8a8  # Pre-calculated for this specific header
            png_data += struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
            
            # IDAT chunk (simple white image)
            import zlib
            raw_data = b'\x00' + b'\xff' * (width * 3) # White row
            raw_data = raw_data * height  # Repeat for all rows
            idat_data = zlib.compress(raw_data)
            idat_crc = zlib.crc32(b'IDAT' + idat_data) & 0xffffffff
            png_data += struct.pack('>I', len(idat_data)) + b'IDAT' + idat_data + struct.pack('>I', idat_crc)
            
            # IEND chunk
            iend_crc = 0xae426082
            png_data += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
            
            with open("test.png", "wb") as f:
                f.write(png_data)
            print(f"   ✅ Created test.png (20x20 manual)")
        
        # Test content (keep short for capacity)
        first_content = "FIRST DOC - preserved"
        second_content = "SECOND DOC - not overwrite"
        
        print(f"   📄 First content: {first_content}")
        print(f"   📄 Second content: {second_content}")
        
        # Initialize steganography manager
        stego_manager = EnhancedWebImageSteganographyManager(password)
        
        # Step 1: First embedding
        print(f"\n2. First embedding...")
        
        result1 = stego_manager.hide_data(
            "test.png",
            first_content.encode('utf-8'),
            "step1.png",
            is_file=True,
            original_filename="first.txt"
        )
        
        print(f"   Result: {result1}")
        
        if not result1.get("success"):
            print(f"   ❌ Failed: {result1.get('error')}")
            return False
        
        step1_file = result1.get("output_path", "step1.png")
        print(f"   ✅ First embedding successful: {step1_file}")
        
        # Step 2: Simulate the layered container logic
        print(f"\n3. Simulating second embedding with layered container logic...")
        
        # Try to extract existing data from step1 file
        print(f"   Checking for existing data in {step1_file}...")
        existing_extraction = stego_manager.extract_data(step1_file)
        
        if isinstance(existing_extraction, tuple):
            existing_data, existing_filename = existing_extraction
        else:
            existing_data = existing_extraction
            existing_filename = None
        
        print(f"   Found existing data: {len(existing_data) if existing_data else 0} bytes")
        print(f"   Existing filename: {existing_filename}")
        
        if existing_data:
            # Convert to string if needed
            if isinstance(existing_data, bytes):
                try:
                    existing_data = existing_data.decode('utf-8')
                except:
                    pass
            
            print(f"   ✅ Existing data found! Creating layered container...")
            print(f"   Existing content: {str(existing_data)[:50]}...")
            
            # Check if already layered
            if isinstance(existing_data, str) and is_layered_container(existing_data):
                existing_layers = extract_layered_data_container(existing_data)
                existing_layers = [layer_data for layer_data, _ in existing_layers]
                print(f"   Found {len(existing_layers)} existing layers")
            else:
                existing_layers = [existing_data]
                print(f"   Converting single data to first layer")
            
            # Add new content
            existing_layers.append(second_content)
            print(f"   Added new content as layer {len(existing_layers)}")
            
            # Create layered container
            layered_container = create_layered_data_container(existing_layers)
            print(f"   📦 Created layered container: {len(layered_container)} chars")
            
            # Embed the layered container
            result2 = stego_manager.hide_data(
                step1_file,
                layered_container.encode('utf-8'),
                "step2.png", 
                is_file=True,
                original_filename="layered_container.json"
            )
            
            print(f"   Layered embed result: {result2}")
            
            if not result2.get("success"):
                print(f"   ❌ Layered embedding failed: {result2.get('error')}")
                return False
            
            step2_file = result2.get("output_path", "step2.png")
            print(f"   ✅ Layered embedding successful: {step2_file}")
            
            # Step 3: Extract and verify
            print(f"\n4. Extracting and verifying layered data...")
            
            final_extraction = stego_manager.extract_data(step2_file)
            
            if isinstance(final_extraction, tuple):
                final_data, final_filename = final_extraction
            else:
                final_data = final_extraction
                final_filename = None
            
            print(f"   Final extracted: {len(final_data) if final_data else 0} bytes")
            print(f"   Final filename: {final_filename}")
            
            if isinstance(final_data, bytes):
                try:
                    final_data = final_data.decode('utf-8')
                except:
                    print(f"   ❌ Could not decode extracted data as UTF-8")
                    return False
            
            print(f"   Final data preview: {final_data[:100]}...")
            
            # Check if it's a layered container
            if is_layered_container(final_data):
                print(f"   ✅ Detected layered container!")
                
                layers = extract_layered_data_container(final_data)
                print(f"   📁 Extracted {len(layers)} layers:")
                
                found_first = False
                found_second = False
                
                for i, (layer_content, layer_filename) in enumerate(layers):
                    print(f"     Layer {i+1}: {layer_filename}")
                    print(f"       Content: {str(layer_content)[:50]}...")
                    
                    if "FIRST DOC" in str(layer_content):
                        found_first = True
                        print(f"       ✅ Found first document!")
                    elif "SECOND DOC" in str(layer_content):
                        found_second = True
                        print(f"       ✅ Found second document!")
                
                if found_first and found_second:
                    print(f"\n   🎉 SUCCESS: Both documents preserved!")
                    success = True
                else:
                    print(f"\n   ❌ FAILURE: Missing documents (First: {found_first}, Second: {found_second})")
                    success = False
                    
            else:
                print(f"   ❌ Not a layered container - fix didn't work")
                success = False
        
        else:
            print(f"   ❌ No existing data found - this shouldn't happen")
            success = False
        
        # Cleanup
        cleanup_files = ["test.png", "step1.png", "step2.png"]
        for file in cleanup_files:
            if os.path.exists(file):
                os.remove(file)
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_layered_embedding()
    
    print(f"\n" + "="*50)
    print("FINAL RESULT")
    print("="*50)
    
    if success:
        print("✅ SUCCESS: Layered container logic works correctly!")
        print("   The fix should work when properly integrated")
    else:
        print("❌ FAILURE: Layered container logic has issues")
        print("   Need to debug further")
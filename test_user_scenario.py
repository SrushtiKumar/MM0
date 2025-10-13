#!/usr/bin/env python3
"""
Test the user's exact scenario: MP3 + image + text with same password
"""

import sys
import os
sys.path.append('.')

def test_user_mp3_scenario():
    """Test the exact user scenario that was causing bin format issues"""
    print("🎯 TESTING USER'S MP3 + IMAGE + TEXT SCENARIO")
    print("="*60)
    
    try:
        # Step 1: Create test files
        print("1. Creating test files...")
        
        # Create a simple MP3 file (minimal MP3 header)
        mp3_data = bytearray([
            0xFF, 0xFB, 0x90, 0x00,  # MP3 frame header
            0x00, 0x00, 0x00, 0x00,  # Rest of minimal MP3 data
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x49, 0x44, 0x33, 0x03   # ID3 tag start
        ])
        
        with open('test_mp3_scenario.mp3', 'wb') as f:
            f.write(mp3_data)
        print("   🎵 Created test_mp3_scenario.mp3")
        
        # Create a test PNG image
        png_data = bytearray([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D,  # IHDR length
            0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x02,  # Width: 2
            0x00, 0x00, 0x00, 0x02,  # Height: 2
            0x08, 0x02, 0x00, 0x00, 0x00,  # Bit depth, color type, etc.
            0x01, 0x2B, 0x05, 0x5B,  # CRC
            0x00, 0x00, 0x00, 0x16,  # IDAT length
            0x49, 0x44, 0x41, 0x54,  # IDAT
            # Simple 2x2 image data
            0x78, 0x9C, 0x63, 0xF8, 0xCF, 0x80, 0x01, 0x19, 0x00, 0x40, 0x00, 0x03, 
            0x00, 0xC4, 0xFF, 0x7F, 0x26, 0xE5, 0x0B, 0x1C,
            0x6C, 0xBF, 0xC8, 0x30,  # CRC
            0x00, 0x00, 0x00, 0x00,  # IEND length
            0x49, 0x45, 0x4E, 0x44,  # IEND
            0xAE, 0x42, 0x60, 0x82   # CRC
        ])
        
        with open('test_scenario_image.png', 'wb') as f:
            f.write(png_data)
        print("   🖼️  Created test_scenario_image.png")
        
        # Create text message
        text_message = "This is the secret text message from the user's scenario"
        with open('test_scenario_message.txt', 'w') as f:
            f.write(text_message)
        print("   📄 Created test_scenario_message.txt")
        
        # Step 2: Import steganography functions  
        print("\n2. Importing steganography functions...")
        from enhanced_app import embed_multiple_data, extract_data
        
        password = "samepassword123"
        
        # Step 3: First hide image in MP3
        print(f"\n3. Step 1: Hiding image in MP3 with password '{password}'...")
        
        result1 = embed_multiple_data(
            "test_mp3_scenario.mp3",
            [("test_scenario_image.png", "")],  # Empty message for files
            password
        )
        
        if result1['success']:
            mp3_with_image = result1['output_filename']
            print(f"   ✅ Image embedded in MP3: {mp3_with_image}")
        else:
            print(f"   ❌ Failed to embed image: {result1.get('error', 'Unknown error')}")
            return False
        
        # Step 4: Hide text in the processed MP3
        print(f"\n4. Step 2: Hiding text in processed MP3 with same password '{password}'...")
        
        result2 = embed_multiple_data(
            mp3_with_image,
            [("test_scenario_message.txt", "")],  # Empty message for files  
            password
        )
        
        if result2['success']:
            final_mp3 = result2['output_filename']
            print(f"   ✅ Text embedded in MP3: {final_mp3}")
        else:
            print(f"   ❌ Failed to embed text: {result2.get('error', 'Unknown error')}")
            return False
        
        # Step 5: Extract all data
        print(f"\n5. Extracting all hidden data with password '{password}'...")
        
        extraction_result = extract_data(final_mp3, password)
        
        if extraction_result['success']:
            if extraction_result.get('zip_file'):
                print(f"   ✅ Extraction successful: {extraction_result['zip_file']}")
                
                # Check the ZIP contents
                import zipfile
                with zipfile.ZipFile(extraction_result['zip_file'], 'r') as zf:
                    file_list = zf.namelist()
                    print(f"   📁 ZIP contains {len(file_list)} files:")
                    
                    image_found_correctly = False
                    text_found_correctly = False
                    
                    for filename in file_list:
                        print(f"     📄 {filename}")
                        
                        # Check if image is properly named
                        if filename.endswith('.png'):
                            print(f"       ✅ Image correctly extracted as PNG format")
                            image_found_correctly = True
                            
                            # Verify content
                            with zf.open(filename) as img_file:
                                img_content = img_file.read()
                                if img_content.startswith(b'\x89PNG'):
                                    print(f"       ✅ PNG content verified correctly")
                                else:
                                    print(f"       ❌ PNG content corrupted")
                                    return False
                        
                        elif filename.endswith('.bin'):
                            print(f"       ❌ File still in .bin format - fix not working!")
                            return False
                        
                        elif filename.endswith('.txt'):
                            print(f"       ✅ Text correctly extracted as TXT format")
                            text_found_correctly = True
                            
                            # Verify content
                            with zf.open(filename) as txt_file:
                                txt_content = txt_file.read().decode('utf-8')
                                if text_message in txt_content:
                                    print(f"       ✅ Text content verified correctly")
                                else:
                                    print(f"       ❌ Text content corrupted")
                                    return False
                    
                    if image_found_correctly and text_found_correctly:
                        print(f"\n   🎉 SUCCESS: Both files extracted with correct formats!")
                        return True
                    else:
                        print(f"\n   ❌ PARTIAL SUCCESS: Some files not found with correct formats")
                        return False
            else:
                print(f"   ❌ No ZIP file created")
                return False
        else:
            print(f"   ❌ Extraction failed: {extraction_result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        print(f"\n6. Cleaning up test files...")
        for filename in ['test_mp3_scenario.mp3', 'test_scenario_image.png', 'test_scenario_message.txt']:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"   🗑️  Removed {filename}")

if __name__ == "__main__":
    success = test_user_mp3_scenario()
    
    print(f"\n" + "="*60)
    print("USER SCENARIO TEST RESULT")
    print("="*60)
    
    if success:
        print("✅ SUCCESS: User's scenario now works correctly!")
        print("   • MP3 + image + text scenario completed")
        print("   • Image extracted as .png (not .bin)")
        print("   • Text extracted as .txt")
        print("   • Both files preserved with original content")
        print("   • Same password used for both operations")
        print("")
        print("🎯 ISSUE RESOLVED: Binary format preservation working!")
    else:
        print("❌ FAILURE: User's scenario still has issues")
        print("   Files may still appear as .bin format")
        print("   Need further investigation")
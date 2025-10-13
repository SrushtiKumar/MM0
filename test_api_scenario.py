#!/usr/bin/env python3
"""
Test the user's exact scenario via API: MP3 + image + text with same password
"""

import requests
import os
import time
import zipfile

def test_user_scenario_via_api():
    """Test the exact user scenario via API calls"""
    print("🎯 TESTING USER'S MP3 + IMAGE + TEXT SCENARIO VIA API")
    print("="*60)
    
    try:
        base_url = "http://localhost:8000"
        
        # Step 1: Check if server is running
        print("1. Checking server status...")
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Server is running")
            else:
                print("   ❌ Server not responding correctly")
                return False
        except requests.exceptions.RequestException:
            print("   ❌ Server not running. Please start the server first.")
            return False
        
        # Step 2: Create test files
        print("\n2. Creating test files...")
        
        # Create a simple MP3 file (minimal MP3 header) - larger size
        mp3_data = bytearray([
            0xFF, 0xFB, 0x90, 0x00,  # MP3 frame header
            0x00, 0x00, 0x00, 0x00,  # Rest of minimal MP3 data
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x49, 0x44, 0x33, 0x03   # ID3 tag start
        ] * 5000)  # Make it much bigger for capacity
        
        with open('test_api_carrier.mp3', 'wb') as f:
            f.write(mp3_data)
        print("   🎵 Created test_api_carrier.mp3")
        
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
        
        with open('test_api_image.png', 'wb') as f:
            f.write(png_data)
        print("   🖼️  Created test_api_image.png")
        
        password = "samepassword123"
        
        # Step 3: First hide image in MP3
        print(f"\n3. Step 1: Hiding image in MP3 with password '{password}'...")
        
        # Prepare files for first embedding
        files1 = {
            'carrier_file': ('test_api_carrier.mp3', open('test_api_carrier.mp3', 'rb'), 'audio/mpeg'),
            'content_file': ('test_api_image.png', open('test_api_image.png', 'rb'), 'image/png')
        }
        
        data1 = {
            'password': password,
            'content_type': 'file',
            'carrier_type': 'audio'
        }
        
        response1 = requests.post(f"{base_url}/api/embed", files=files1, data=data1)
        
        # Close the file handles
        files1['carrier_file'][1].close()
        files1['content_file'][1].close()
        
        if response1.status_code == 200:
            result1 = response1.json()
            if result1.get('success'):
                operation_id1 = result1['operation_id']
                print(f"   ✅ Image embedding started: {operation_id1}")
                
                # Wait for completion and download
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    status_response = requests.get(f"{base_url}/api/operations/{operation_id1}/status")
                    if status_response.status_code == 200:
                        status = status_response.json()
                        if status.get('status') == 'completed':
                            print(f"   ✅ Image embedding completed")
                            
                            # Download the result
                            download_response = requests.get(f"{base_url}/api/operations/{operation_id1}/download")
                            if download_response.status_code == 200:
                                mp3_with_image = f"mp3_with_image_{operation_id1}.mp3"
                                with open(mp3_with_image, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"   ✅ Downloaded: {mp3_with_image}")
                                break
                            else:
                                print(f"   ❌ Download failed: {download_response.status_code}")
                                return False
                        elif status.get('status') == 'failed':
                            print(f"   ❌ Embedding failed: {status.get('error')}")
                            return False
                else:
                    print(f"   ❌ Embedding timed out")
                    return False
            else:
                print(f"   ❌ Embedding request failed: {result1.get('error')}")
                return False
        else:
            print(f"   ❌ API request failed: {response1.status_code}")
            return False
        
        # Step 4: Hide text in the processed MP3
        print(f"\n4. Step 2: Hiding text in processed MP3 with same password '{password}'...")
        
        text_message = "This is the secret text message from the user's scenario"
        
        # Prepare files for second embedding
        files2 = {
            'carrier_file': ('mp3_with_image.mp3', open(mp3_with_image, 'rb'), 'audio/mpeg')
        }
        
        data2 = {
            'password': password,
            'content_type': 'text',
            'text_content': text_message,
            'carrier_type': 'audio'
        }
        
        response2 = requests.post(f"{base_url}/api/embed", files=files2, data=data2)
        
        # Close the file handle
        files2['carrier_file'][1].close()
        
        if response2.status_code == 200:
            result2 = response2.json()
            if result2.get('success'):
                operation_id2 = result2['operation_id']
                print(f"   ✅ Text embedding started: {operation_id2}")
                
                # Wait for completion and download
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    status_response = requests.get(f"{base_url}/api/operations/{operation_id2}/status")
                    if status_response.status_code == 200:
                        status = status_response.json()
                        if status.get('status') == 'completed':
                            print(f"   ✅ Text embedding completed")
                            
                            # Download the result
                            download_response = requests.get(f"{base_url}/api/operations/{operation_id2}/download")
                            if download_response.status_code == 200:
                                final_mp3 = f"final_mp3_{operation_id2}.mp3"
                                with open(final_mp3, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"   ✅ Downloaded: {final_mp3}")
                                break
                            else:
                                print(f"   ❌ Download failed: {download_response.status_code}")
                                return False
                        elif status.get('status') == 'failed':
                            print(f"   ❌ Embedding failed: {status.get('error')}")
                            return False
                else:
                    print(f"   ❌ Embedding timed out")
                    return False
            else:
                print(f"   ❌ Embedding request failed: {result2.get('error')}")
                return False
        else:
            print(f"   ❌ API request failed: {response2.status_code}")
            return False
        
        # Step 5: Extract all data
        print(f"\n5. Extracting all hidden data with password '{password}'...")
        
        # Prepare file for extraction
        files3 = {
            'stego_file': ('final_mp3.mp3', open(final_mp3, 'rb'), 'audio/mpeg')
        }
        
        data3 = {
            'password': password
        }
        
        response3 = requests.post(f"{base_url}/api/extract", files=files3, data=data3)
        
        # Close the file handle
        files3['stego_file'][1].close()
        
        if response3.status_code == 200:
            result3 = response3.json()
            if result3.get('success'):
                operation_id3 = result3['operation_id']
                print(f"   ✅ Extraction started: {operation_id3}")
                
                # Wait for completion and download
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    status_response = requests.get(f"{base_url}/api/operations/{operation_id3}/status")
                    if status_response.status_code == 200:
                        status = status_response.json()
                        if status.get('status') == 'completed':
                            print(f"   ✅ Extraction completed")
                            
                            # Download the result
                            download_response = requests.get(f"{base_url}/api/operations/{operation_id3}/download")
                            if download_response.status_code == 200:
                                zip_file = f"extracted_data_{operation_id3}.zip"
                                with open(zip_file, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"   ✅ Downloaded: {zip_file}")
                                
                                # Check the ZIP contents
                                print(f"\n6. Analyzing extracted files...")
                                with zipfile.ZipFile(zip_file, 'r') as zf:
                                    file_list = zf.namelist()
                                    print(f"   📁 ZIP contains {len(file_list)} files:")
                                    
                                    image_found_correctly = False
                                    text_found_correctly = False
                                    bin_files_found = []
                                    
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
                                            bin_files_found.append(filename)
                                        
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
                                    
                                    if bin_files_found:
                                        print(f"\n   ❌ STILL FINDING .BIN FILES: {bin_files_found}")
                                        print(f"   The binary format fix is not working in real API scenario")
                                        return False
                                    elif image_found_correctly and text_found_correctly:
                                        print(f"\n   🎉 SUCCESS: Both files extracted with correct formats!")
                                        return True
                                    else:
                                        print(f"\n   ❌ PARTIAL SUCCESS: Some files not found with correct formats")
                                        return False
                                
                                break
                            else:
                                print(f"   ❌ Download failed: {download_response.status_code}")
                                return False
                        elif status.get('status') == 'failed':
                            print(f"   ❌ Extraction failed: {status.get('error')}")
                            return False
                else:
                    print(f"   ❌ Extraction timed out")
                    return False
            else:
                print(f"   ❌ Extraction request failed: {result3.get('error')}")
                return False
        else:
            print(f"   ❌ API request failed: {response3.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        print(f"\n7. Cleaning up test files...")
        for filename in ['test_api_carrier.mp3', 'test_api_image.png']:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"   🗑️  Removed {filename}")

if __name__ == "__main__":
    success = test_user_scenario_via_api()
    
    print(f"\n" + "="*60)
    print("USER SCENARIO API TEST RESULT")
    print("="*60)
    
    if success:
        print("✅ SUCCESS: User's scenario now works correctly via API!")
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
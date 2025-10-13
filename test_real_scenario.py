#!/usr/bin/env python3
"""
Test the user's scenario using existing WAV file
"""

import requests
import os
import time
import zipfile

def test_with_existing_wav():
    """Test with an existing WAV file"""
    print("🎯 TESTING WITH EXISTING WAV FILE")
    print("="*60)
    
    try:
        base_url = "http://localhost:8000"
        
        # Check if we have an existing WAV file
        wav_file = "audio_with_hidden_doc.wav"
        if not os.path.exists(wav_file):
            print(f"   ❌ WAV file {wav_file} not found")
            return False
        
        print(f"   ✅ Using existing WAV file: {wav_file}")
        
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
        
        with open('test_real_image.png', 'wb') as f:
            f.write(png_data)
        print("   🖼️  Created test_real_image.png")
        
        password = "samepassword123"
        
        # Step 1: Hide image in WAV
        print(f"\n1. Hiding image in WAV with password '{password}'...")
        
        files1 = {
            'carrier_file': (wav_file, open(wav_file, 'rb'), 'audio/wav'),
            'content_file': ('test_real_image.png', open('test_real_image.png', 'rb'), 'image/png')
        }
        
        data1 = {
            'password': password,
            'content_type': 'file',
            'carrier_type': 'audio'
        }
        
        response1 = requests.post(f"{base_url}/api/embed", files=files1, data=data1)
        
        files1['carrier_file'][1].close()
        files1['content_file'][1].close()
        
        if response1.status_code == 200:
            result1 = response1.json()
            if result1.get('success'):
                operation_id1 = result1['operation_id']
                print(f"   ✅ Image embedding started: {operation_id1}")
                
                # Wait for completion
                wav_with_image = None
                for i in range(30):
                    time.sleep(1)
                    status_response = requests.get(f"{base_url}/api/operations/{operation_id1}/status")
                    if status_response.status_code == 200:
                        status = status_response.json()
                        if status.get('status') == 'completed':
                            print(f"   ✅ Image embedding completed")
                            
                            # Download the result
                            download_response = requests.get(f"{base_url}/api/operations/{operation_id1}/download")
                            if download_response.status_code == 200:
                                wav_with_image = f"wav_with_image_{operation_id1}.wav"
                                with open(wav_with_image, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"   ✅ Downloaded: {wav_with_image}")
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
                
                # Step 2: Hide text in the processed WAV
                print(f"\n2. Hiding text in processed WAV with same password '{password}'...")
                
                text_message = "This is the secret text message to test binary format preservation"
                
                files2 = {
                    'carrier_file': ('wav_with_image.wav', open(wav_with_image, 'rb'), 'audio/wav')
                }
                
                data2 = {
                    'password': password,
                    'content_type': 'text',
                    'text_content': text_message,
                    'carrier_type': 'audio'
                }
                
                response2 = requests.post(f"{base_url}/api/embed", files=files2, data=data2)
                files2['carrier_file'][1].close()
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    if result2.get('success'):
                        operation_id2 = result2['operation_id']
                        print(f"   ✅ Text embedding started: {operation_id2}")
                        
                        # Wait for completion
                        final_wav = None
                        for i in range(30):
                            time.sleep(1)
                            status_response = requests.get(f"{base_url}/api/operations/{operation_id2}/status")
                            if status_response.status_code == 200:
                                status = status_response.json()
                                if status.get('status') == 'completed':
                                    print(f"   ✅ Text embedding completed")
                                    
                                    # Download the result
                                    download_response = requests.get(f"{base_url}/api/operations/{operation_id2}/download")
                                    if download_response.status_code == 200:
                                        final_wav = f"final_wav_{operation_id2}.wav"
                                        with open(final_wav, 'wb') as f:
                                            f.write(download_response.content)
                                        print(f"   ✅ Downloaded: {final_wav}")
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
                        
                        # Step 3: Extract all data
                        print(f"\n3. Extracting all hidden data with password '{password}'...")
                        
                        files3 = {
                            'stego_file': ('final_wav.wav', open(final_wav, 'rb'), 'audio/wav')
                        }
                        
                        data3 = {
                            'password': password
                        }
                        
                        response3 = requests.post(f"{base_url}/api/extract", files=files3, data=data3)
                        files3['stego_file'][1].close()
                        
                        if response3.status_code == 200:
                            result3 = response3.json()
                            if result3.get('success'):
                                operation_id3 = result3['operation_id']
                                print(f"   ✅ Extraction started: {operation_id3}")
                                
                                # Wait for completion
                                for i in range(30):
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
                                                
                                                # Check the ZIP contents - THIS IS THE CRITICAL TEST
                                                print(f"\n4. 🔍 ANALYZING EXTRACTED FILES...")
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
                                                            
                                                            # Let's check what this bin file actually contains
                                                            with zf.open(filename) as bin_file:
                                                                bin_content = bin_file.read()
                                                                print(f"         📊 .bin file size: {len(bin_content)} bytes")
                                                                print(f"         📊 .bin file header: {bin_content[:16].hex()}")
                                                                if bin_content.startswith(b'\x89PNG'):
                                                                    print(f"         💡 .bin file contains PNG data!")
                                                        
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
                                                        print(f"   🔧 The binary format fix needs more work")
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
                    else:
                        print(f"   ❌ Text embedding request failed: {result2.get('error')}")
                        return False
                else:
                    print(f"   ❌ API request failed: {response2.status_code}")
                    return False
            else:
                print(f"   ❌ Image embedding request failed: {result1.get('error')}")
                return False
        else:
            print(f"   ❌ API request failed: {response1.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists('test_real_image.png'):
            os.remove('test_real_image.png')

if __name__ == "__main__":
    success = test_with_existing_wav()
    
    print(f"\n" + "="*60)
    print("REAL SCENARIO TEST RESULT")
    print("="*60)
    
    if success:
        print("✅ SUCCESS: Binary format preservation is working!")
        print("   • WAV + image + text scenario completed")
        print("   • Image extracted as .png (not .bin)")
        print("   • Text extracted as .txt")
        print("   • Both files preserved with original content")
        print("   • Same password used for both operations")
        print("")
        print("🎯 USER ISSUE RESOLVED!")
    else:
        print("❌ FAILURE: Binary format preservation still needs work")
        print("   Files may still appear as .bin format")
        print("   The fix is not complete")
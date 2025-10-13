#!/usr/bin/env python3
"""
Test the exact user scenario that's causing the .bin issue
"""

import requests
import os
import time
import zipfile
from pathlib import Path

def test_exact_user_scenario():
    """Test exactly what the user is experiencing"""
    print("🎯 TESTING EXACT USER SCENARIO")
    print("="*60)
    
    base_url = "http://localhost:8000"
    password = "samepassword123"
    
    try:
        # Use an existing audio file with enough capacity
        audio_files = list(Path('.').glob('audio_with_*.wav'))
        if audio_files:
            audio_file = str(audio_files[0])
            print(f"   🎵 Using existing WAV: {audio_file}")
        else:
            print(f"   ❌ No suitable audio files found")
            return False
        
        # Create a test image file
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
        
        image_file = "test_user_image.png"
        with open(image_file, 'wb') as f:
            f.write(png_data)
        print(f"   🖼️  Created test image: {image_file}")
        
        print(f"\n1. First hiding image in MP3 with password '{password}'...")
        
        # Step 1: Hide image in audio file
        files1 = {
            'carrier_file': (audio_file, open(audio_file, 'rb'), 'audio/wav'),
            'content_file': (image_file, open(image_file, 'rb'), 'image/png')
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
                op_id1 = result1['operation_id']
                print(f"   ✅ Started: {op_id1}")
                
                # Wait for completion
                mp3_with_image = None
                for i in range(30):
                    time.sleep(1)
                    status_resp = requests.get(f"{base_url}/api/operations/{op_id1}/status")
                    if status_resp.status_code == 200:
                        status = status_resp.json()
                        if status.get('status') == 'completed':
                            # Download result
                            dl_resp = requests.get(f"{base_url}/api/operations/{op_id1}/download")
                            if dl_resp.status_code == 200:
                                audio_with_image = f"step1_result.wav"
                                with open(audio_with_image, 'wb') as f:
                                    f.write(dl_resp.content)
                                print(f"   ✅ Downloaded: {audio_with_image}")
                                break
                        elif status.get('status') == 'failed':
                            print(f"   ❌ Failed: {status.get('error')}")
                            return False
                else:
                    print(f"   ❌ Timed out")
                    return False
                
                print(f"\n2. Now hiding text in the processed audio file with same password '{password}'...")
                
                # Step 2: Hide text message in the processed audio file
                text_message = "This is my secret text message"
                
                files2 = {
                    'carrier_file': (audio_with_image, open(audio_with_image, 'rb'), 'audio/wav')
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
                        op_id2 = result2['operation_id']
                        print(f"   ✅ Started: {op_id2}")
                        
                        # Wait for completion
                        final_mp3 = None
                        for i in range(30):
                            time.sleep(1)
                            status_resp = requests.get(f"{base_url}/api/operations/{op_id2}/status")
                            if status_resp.status_code == 200:
                                status = status_resp.json()
                                if status.get('status') == 'completed':
                                    # Download result
                                    dl_resp = requests.get(f"{base_url}/api/operations/{op_id2}/download")
                                    if dl_resp.status_code == 200:
                                        final_audio = f"step2_result.wav"
                                        with open(final_audio, 'wb') as f:
                                            f.write(dl_resp.content)
                                        print(f"   ✅ Downloaded: {final_audio}")
                                        break
                                elif status.get('status') == 'failed':
                                    print(f"   ❌ Failed: {status.get('error')}")
                                    return False
                        else:
                            print(f"   ❌ Timed out")
                            return False
                        
                        print(f"\n3. Now extracting with password '{password}' - this is where the .bin issue occurs...")
                        
                        # Step 3: Extract the data
                        files3 = {
                            'stego_file': (final_audio, open(final_audio, 'rb'), 'audio/wav')
                        }
                        
                        data3 = {
                            'password': password
                        }
                        
                        response3 = requests.post(f"{base_url}/api/extract", files=files3, data=data3)
                        files3['stego_file'][1].close()
                        
                        if response3.status_code == 200:
                            result3 = response3.json()
                            if result3.get('success'):
                                op_id3 = result3['operation_id']
                                print(f"   ✅ Started: {op_id3}")
                                
                                # Wait for completion
                                for i in range(30):
                                    time.sleep(1)
                                    status_resp = requests.get(f"{base_url}/api/operations/{op_id3}/status")
                                    if status_resp.status_code == 200:
                                        status = status_resp.json()
                                        if status.get('status') == 'completed':
                                            # Download result
                                            dl_resp = requests.get(f"{base_url}/api/operations/{op_id3}/download")
                                            if dl_resp.status_code == 200:
                                                zip_file = f"user_extraction_result.zip"
                                                with open(zip_file, 'wb') as f:
                                                    f.write(dl_resp.content)
                                                print(f"   ✅ Downloaded: {zip_file}")
                                                
                                                # Analyze what we got
                                                print(f"\n4. 🔍 ANALYZING WHAT USER GETS...")
                                                with zipfile.ZipFile(zip_file, 'r') as zf:
                                                    file_list = zf.namelist()
                                                    print(f"   📁 ZIP contains {len(file_list)} files:")
                                                    
                                                    for filename in file_list:
                                                        print(f"     📄 {filename}")
                                                        
                                                        if filename.endswith('.bin'):
                                                            print(f"       ❌ STILL GETTING .BIN FILES!")
                                                            
                                                            # Check what's in the bin file
                                                            with zf.open(filename) as bin_file:
                                                                content = bin_file.read()
                                                                print(f"         Size: {len(content)} bytes")
                                                                print(f"         Header: {content[:16].hex()}")
                                                                if content.startswith(b'\x89PNG'):
                                                                    print(f"         💡 This .bin file contains PNG data!")
                                                                    return False  # The fix isn't working
                                                        else:
                                                            print(f"       ✅ Proper format: {filename}")
                                                
                                                return True
                                            else:
                                                print(f"   ❌ Download failed: {dl_resp.status_code}")
                                                return False
                                        elif status.get('status') == 'failed':
                                            print(f"   ❌ Failed: {status.get('error')}")
                                            return False
                                else:
                                    print(f"   ❌ Timed out")
                                    return False
                            else:
                                print(f"   ❌ Extraction failed: {result3.get('error')}")
                                return False
                        else:
                            print(f"   ❌ Extract API failed: {response3.status_code}")
                            return False
                    else:
                        print(f"   ❌ Text embed failed: {result2.get('error')}")
                        return False
                else:
                    print(f"   ❌ Text embed API failed: {response2.status_code}")
                    return False
            else:
                print(f"   ❌ Image embed failed: {result1.get('error')}")
                return False
        else:
            print(f"   ❌ Image embed API failed: {response1.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        for f in ['test_user_image.png']:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    success = test_exact_user_scenario()
    
    print(f"\n" + "="*60)
    if success:
        print("✅ SUCCESS: Fix is working!")
    else:
        print("❌ FAILURE: Still getting .bin files - fix needs more work")
    print("="*60)
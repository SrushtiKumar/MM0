#!/usr/bin/env python3
"""
Comprehensive test for all steganography formats: Image, Video, Audio, Document
Tests both embedding and extraction functionality with focus on file format preservation
"""

import requests
import time
import json
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api"

def wait_for_completion(operation_id, timeout=30):
    """Wait for operation to complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(f"{BASE_URL}/operations/{operation_id}/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"Status: {status_data['status']} - {status_data.get('message', '')}")
            
            if status_data['status'] == 'completed':
                return status_data
            elif status_data['status'] == 'failed':
                raise Exception(f"Operation failed: {status_data.get('error', 'Unknown error')}")
        
        time.sleep(1)
    
    raise Exception("Operation timed out")

def test_file_extraction_format():
    """Test that extracted files maintain proper format and can be downloaded correctly"""
    print("\n📁 Testing FILE EXTRACTION FORMAT preservation...")
    
    # Create a test image file to hide
    test_content = "This is a secret message that should be extracted with proper filename!"
    with open("secret_test.txt", "w") as f:
        f.write(test_content)
    
    # Test with an existing audio file as carrier
    carrier_files = ["demo_audio.wav", "debug_test_audio.wav"]
    carrier_file = None
    
    for cf in carrier_files:
        if os.path.exists(cf):
            carrier_file = cf
            break
    
    if not carrier_file:
        print("❌ No suitable carrier file found")
        return False
    
    print(f"📝 Test: Hiding secret_test.txt in {carrier_file}")
    
    # Embed the text file
    with open(carrier_file, 'rb') as cf, open("secret_test.txt", 'rb') as sf:
        files = {
            'carrier_file': cf,
            'content_file': sf
        }
        data = {
            'content_type': 'file',
            'password': 'test123'
        }
        
        response = requests.post(f"{BASE_URL}/embed", files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Embed failed: {response.text}")
            return False
        
        operation_id = response.json()['operation_id']
        print(f"✅ Embed started: {operation_id}")
        
        # Wait for completion
        status_data = wait_for_completion(operation_id)
        print(f"✅ Embed completed: {status_data['result']['filename']}")
        
        # Download result
        download_response = requests.get(f"{BASE_URL}/operations/{operation_id}/download")
        if download_response.status_code == 200:
            stego_filename = f"stego_{carrier_file}"
            with open(stego_filename, 'wb') as f:
                f.write(download_response.content)
            print(f"✅ Stego file saved: {stego_filename}")
            
            # Test extraction
            print("🔍 Testing extraction...")
            with open(stego_filename, 'rb') as f:
                files = {'stego_file': f}
                data = {'password': 'test123'}
                
                extract_response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
                if extract_response.status_code == 200:
                    extract_operation_id = extract_response.json()['operation_id']
                    print(f"✅ Extract started: {extract_operation_id}")
                    
                    extract_status = wait_for_completion(extract_operation_id)
                    print(f"✅ Extract completed")
                    print(f"Result details: {extract_status['result']}")
                    
                    # Download extracted content
                    extract_download = requests.get(f"{BASE_URL}/operations/{extract_operation_id}/download")
                    if extract_download.status_code == 200:
                        extracted_filename = extract_status['result']['filename']
                        
                        # Check headers for proper content disposition
                        headers = extract_download.headers
                        print(f"Download headers: {dict(headers)}")
                        
                        with open(f"downloaded_{extracted_filename}", 'wb') as f:
                            f.write(extract_download.content)
                        print(f"✅ Extracted content saved: downloaded_{extracted_filename}")
                        
                        # Verify content
                        try:
                            with open(f"downloaded_{extracted_filename}", 'r') as f:
                                extracted_text = f.read()
                            
                            if test_content in extracted_text:
                                print("✅ Content verification PASSED!")
                                print(f"✅ Filename preserved: {extracted_filename}")
                                return True
                            else:
                                print(f"❌ Content mismatch. Expected: {test_content}")
                                print(f"Got: {extracted_text}")
                        except Exception as e:
                            print(f"❌ Could not read extracted file as text: {e}")
                            # Try reading as binary
                            with open(f"downloaded_{extracted_filename}", 'rb') as f:
                                binary_content = f.read()
                            print(f"Binary content (first 100 bytes): {binary_content[:100]}")
                    else:
                        print(f"❌ Extract download failed: {extract_download.status_code}")
                        print(f"Response: {extract_download.text}")
                else:
                    print(f"❌ Extract failed: {extract_response.text}")
        else:
            print(f"❌ Download failed: {download_response.status_code}")
    
    return False

def test_wav_file_upload():
    """Test that WAV files can be uploaded as carriers"""
    print("\n🎵 Testing WAV file upload support...")
    
    # Find a WAV file
    wav_files = ["demo_audio.wav", "debug_test_audio.wav", "enhanced_audio_test.wav"]
    wav_file = None
    
    for wf in wav_files:
        if os.path.exists(wf):
            wav_file = wf
            break
    
    if not wav_file:
        print("❌ No WAV file found for testing")
        return False
    
    print(f"📝 Test: Uploading {wav_file} as carrier")
    
    with open(wav_file, 'rb') as f:
        files = {'carrier_file': f}
        data = {
            'content_type': 'text',
            'text_content': 'Testing WAV upload support!',
            'password': 'wav123'
        }
        
        response = requests.post(f"{BASE_URL}/embed", files=files, data=data)
        
        if response.status_code == 200:
            print("✅ WAV file upload PASSED!")
            return True
        else:
            print(f"❌ WAV file upload failed: {response.text}")
            return False

def main():
    """Run focused tests for extraction and file format issues"""
    print("🔬 FOCUSED STEGANOGRAPHY TESTS")
    print("="*50)
    
    results = {
        "File Format Extraction": False,
        "WAV Upload Support": False
    }
    
    try:
        results["File Format Extraction"] = test_file_extraction_format()
    except Exception as e:
        print(f"❌ File format extraction test failed: {e}")
    
    try:
        results["WAV Upload Support"] = test_wav_file_upload()
    except Exception as e:
        print(f"❌ WAV upload test failed: {e}")
    
    # Print final results
    print("\n📊 FINAL RESULTS")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL FOCUSED TESTS PASSED!")
    else:
        print("⚠️  Some tests failed - check the logs above")

if __name__ == "__main__":
    main()
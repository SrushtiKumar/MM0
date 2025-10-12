#!/usr/bin/env python3
"""
Quick API test to verify the fixes are working
"""

import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000/api"

def wait_for_completion(operation_id, timeout=30):
    """Wait for operation to complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(f"{BASE_URL}/operations/{operation_id}/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"  Status: {status_data['status']} - {status_data.get('message', '')}")
            
            if status_data['status'] == 'completed':
                return status_data
            elif status_data['status'] == 'failed':
                print(f"  Error: {status_data.get('error', 'Unknown error')}")
                return None
        
        time.sleep(1)
    
    print(f"  Operation timed out after {timeout} seconds")
    return None

def test_complete_workflow():
    """Test complete embedding and extraction workflow"""
    print("🧪 Testing Complete Steganography Workflow")
    print("="*50)
    
    # Look for existing files
    audio_file = None
    for af in ["demo_audio.wav", "debug_test_audio.wav", "enhanced_audio_test.wav"]:
        if os.path.exists(af):
            audio_file = af
            break
    
    if not audio_file:
        print("❌ No audio file found for testing")
        return False
    
    print(f"📁 Using carrier file: {audio_file}")
    
    # Test 1: WAV file upload support
    print("\n🎵 Test 1: WAV File Upload Support")
    with open(audio_file, 'rb') as f:
        files = {'carrier_file': f}
        data = {
            'content_type': 'text',
            'text_content': 'Testing WAV upload support!',
            'password': 'test123'
        }
        
        response = requests.post(f"{BASE_URL}/embed", files=files, data=data)
        
        if response.status_code == 200:
            print("✅ WAV file upload PASSED")
            operation_id = response.json()['operation_id']
            
            # Wait for completion
            status_data = wait_for_completion(operation_id)
            if status_data:
                print("✅ Embedding completed successfully")
                
                # Test 2: Download with proper format
                print("\n💾 Test 2: Download Result")
                download_response = requests.get(f"{BASE_URL}/operations/{operation_id}/download")
                
                if download_response.status_code == 200:
                    # Check headers
                    content_disposition = download_response.headers.get('Content-Disposition', '')
                    content_type = download_response.headers.get('Content-Type', '')
                    
                    print(f"✅ Download successful")
                    print(f"  Content-Type: {content_type}")
                    print(f"  Content-Disposition: {content_disposition}")
                    
                    # Save file
                    stego_filename = f"test_stego_{audio_file}"
                    with open(stego_filename, 'wb') as f:
                        f.write(download_response.content)
                    print(f"  File saved: {stego_filename}")
                    
                    # Test 3: Extraction with proper filename
                    print("\n🔍 Test 3: Extraction with Proper Filename")
                    with open(stego_filename, 'rb') as f:
                        files = {'stego_file': f}
                        data = {'password': 'test123'}
                        
                        extract_response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
                        
                        if extract_response.status_code == 200:
                            extract_operation_id = extract_response.json()['operation_id']
                            print(f"✅ Extraction started: {extract_operation_id}")
                            
                            extract_status = wait_for_completion(extract_operation_id)
                            if extract_status:
                                print("✅ Extraction completed successfully")
                                
                                # Check result details
                                result = extract_status.get('result', {})
                                extracted_filename = result.get('filename', 'unknown')
                                file_size = result.get('file_size', 0)
                                data_type = result.get('data_type', 'unknown')
                                
                                print(f"  Extracted filename: {extracted_filename}")
                                print(f"  File size: {file_size} bytes")
                                print(f"  Data type: {data_type}")
                                
                                # Test 4: Download extracted file
                                print("\n📥 Test 4: Download Extracted File")
                                extract_download = requests.get(f"{BASE_URL}/operations/{extract_operation_id}/download")
                                
                                if extract_download.status_code == 200:
                                    # Check headers for proper filename
                                    extract_disposition = extract_download.headers.get('Content-Disposition', '')
                                    extract_content_type = extract_download.headers.get('Content-Type', '')
                                    
                                    print(f"✅ Extracted file download successful")
                                    print(f"  Content-Type: {extract_content_type}")
                                    print(f"  Content-Disposition: {extract_disposition}")
                                    
                                    # Save extracted file
                                    final_filename = f"final_{extracted_filename}"
                                    with open(final_filename, 'wb') as f:
                                        f.write(extract_download.content)
                                    print(f"  File saved: {final_filename}")
                                    
                                    # Verify content
                                    try:
                                        with open(final_filename, 'r') as f:
                                            content = f.read()
                                        
                                        if "Testing WAV upload support!" in content:
                                            print("✅ Content verification PASSED")
                                            print("🎉 ALL TESTS PASSED!")
                                            return True
                                        else:
                                            print(f"❌ Content mismatch: {content}")
                                    except Exception as e:
                                        print(f"❌ Could not read file as text: {e}")
                                else:
                                    print(f"❌ Extract download failed: {extract_download.status_code}")
                            else:
                                print("❌ Extraction failed or timed out")
                        else:
                            print(f"❌ Extract request failed: {extract_response.status_code}")
                            print(f"  Response: {extract_response.text}")
                else:
                    print(f"❌ Download failed: {download_response.status_code}")
            else:
                print("❌ Embedding failed or timed out")
        else:
            print(f"❌ WAV file upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
    
    return False

def test_file_formats():
    """Test different file format handling"""
    print("\n📄 Testing Different File Format Handling")
    
    # Create test files
    test_files = {
        "test.txt": "This is a test text file for steganography!",
        "test.json": '{"message": "This is a JSON test file", "type": "test"}',
    }
    
    for filename, content in test_files.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"  Created: {filename}")
    
    # Use audio file as carrier
    audio_file = None
    for af in ["demo_audio.wav", "debug_test_audio.wav"]:
        if os.path.exists(af):
            audio_file = af
            break
    
    if not audio_file:
        print("❌ No audio file found")
        return False
    
    for filename in test_files.keys():
        print(f"\n📎 Testing file format preservation for: {filename}")
        
        # Embed the file
        with open(audio_file, 'rb') as cf, open(filename, 'rb') as tf:
            files = {
                'carrier_file': cf,
                'content_file': tf
            }
            data = {
                'content_type': 'file',
                'password': 'format123'
            }
            
            response = requests.post(f"{BASE_URL}/embed", files=files, data=data)
            
            if response.status_code == 200:
                operation_id = response.json()['operation_id']
                status_data = wait_for_completion(operation_id)
                
                if status_data:
                    # Download stego file
                    download_response = requests.get(f"{BASE_URL}/operations/{operation_id}/download")
                    if download_response.status_code == 200:
                        stego_filename = f"stego_{filename}_{audio_file}"
                        with open(stego_filename, 'wb') as f:
                            f.write(download_response.content)
                        
                        # Extract the file
                        with open(stego_filename, 'rb') as f:
                            files = {'stego_file': f}
                            data = {'password': 'format123'}
                            
                            extract_response = requests.post(f"{BASE_URL}/extract", files=files, data=data)
                            if extract_response.status_code == 200:
                                extract_operation_id = extract_response.json()['operation_id']
                                extract_status = wait_for_completion(extract_operation_id)
                                
                                if extract_status:
                                    extracted_filename = extract_status['result']['filename']
                                    print(f"  ✅ Extracted filename: {extracted_filename}")
                                    
                                    # Check if extension is preserved
                                    original_ext = os.path.splitext(filename)[1]
                                    extracted_ext = os.path.splitext(extracted_filename)[1]
                                    
                                    if original_ext == extracted_ext:
                                        print(f"  ✅ Extension preserved: {original_ext}")
                                    else:
                                        print(f"  ❌ Extension changed: {original_ext} → {extracted_ext}")

if __name__ == "__main__":
    print("🔬 COMPREHENSIVE API FUNCTIONALITY TEST")
    print("="*60)
    
    success = test_complete_workflow()
    
    if success:
        test_file_formats()
    
    print("\n📊 Test completed!")
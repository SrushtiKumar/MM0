#!/usr/bin/env python3
"""
Test File Embedding Workflow - Test with file content instead of text
"""

import requests
import json
import time
import os

API_BASE = "http://localhost:8000/api"

def test_file_workflow():
    """Test complete embed -> extract workflow with file content"""
    
    print("=== FILE WORKFLOW TEST ===\n")
    
    # Create test file content
    test_file_content = "This is test file content for preservation testing!\nLine 2 of the test file.\nLine 3 with special chars: @#$%^&*()"
    test_file_path = "test_content_file.txt"
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_file_content)
    
    print("1. Testing file embed operation...")
    
    try:
        # Use existing image as carrier
        with open("debug_embedded.png", 'rb') as carrier_file, \
             open(test_file_path, 'rb') as content_file:
            
            files = {
                'carrier_file': carrier_file,
                'content_file': content_file
            }
            data = {
                'password': 'filetest123',
                'carrier_type': 'image',
                'content_type': 'file'
            }
            
            print(f"   Embedding file: {test_file_path}")
            embed_response = requests.post(f"{API_BASE}/embed", files=files, data=data, timeout=30)
            print(f"   Embed Status: {embed_response.status_code}")
            
            if embed_response.status_code == 200:
                embed_result = embed_response.json()
                embed_operation_id = embed_result.get('operation_id')
                output_filename = embed_result.get('output_filename')
                print(f"   ✓ Embed Operation ID: {embed_operation_id}")
                print(f"   ✓ Output filename: {output_filename}")
                
                # Check embed status
                print("\n2. Checking embed status...")
                status_response = requests.get(f"{API_BASE}/operations/{embed_operation_id}/status", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Embed Status: {status_data.get('status')}")
                    
                    if status_data.get('status') == 'completed':
                        # Download and test extraction
                        print("\n3. Testing file extract operation...")
                        
                        download_response = requests.get(f"{API_BASE}/download/{output_filename}", timeout=30)
                        if download_response.status_code == 200:
                            embedded_file_path = f"temp_file_embedded_{int(time.time())}.png"
                            with open(embedded_file_path, 'wb') as f:
                                f.write(download_response.content)
                            
                            print(f"   ✓ Downloaded embedded file: {embedded_file_path}")
                            
                            # Extract from this file
                            with open(embedded_file_path, 'rb') as stego_file:
                                extract_files = {
                                    'stego_file': stego_file
                                }
                                extract_data = {
                                    'password': 'filetest123',
                                    'carrier_type': 'image',
                                    'output_format': 'preserve'
                                }
                                
                                extract_response = requests.post(f"{API_BASE}/extract", files=extract_files, data=extract_data, timeout=30)
                                print(f"   Extract Status: {extract_response.status_code}")
                                
                                if extract_response.status_code == 200:
                                    extract_result = extract_response.json()
                                    extract_operation_id = extract_result.get('operation_id')
                                    print(f"   ✓ Extract Operation ID: {extract_operation_id}")
                                    
                                    # Check extract status
                                    print("\n4. Checking extract status...")
                                    time.sleep(2)
                                    
                                    extract_status_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/status", timeout=10)
                                    if extract_status_response.status_code == 200:
                                        extract_status_data = extract_status_response.json()
                                        print(f"   Extract Status: {extract_status_data.get('status')}")
                                        
                                        if extract_status_data.get('status') == 'completed':
                                            # Check extracted results
                                            result = extract_status_data.get('result', {})
                                            extracted_filename = result.get('filename')
                                            preview = result.get('preview')
                                            data_type = result.get('data_type')
                                            
                                            print(f"\n5. File Extraction Results:")
                                            print(f"   Extracted filename: {extracted_filename}")
                                            print(f"   Data type: {data_type}")
                                            print(f"   Preview: {repr(preview[:100]) if preview else 'None'}...")
                                            
                                            # Download extracted file
                                            if extracted_filename:
                                                print(f"\n6. Downloading and verifying extracted file...")
                                                extracted_download = requests.get(f"{API_BASE}/download/{extracted_filename}", timeout=30)
                                                if extracted_download.status_code == 200:
                                                    extracted_content = extracted_download.text
                                                    print(f"   Downloaded content preview: {repr(extracted_content[:100])}...")
                                                    
                                                    if extracted_content.strip() == test_file_content.strip():
                                                        print(f"   ✅ FILE CONTENT VERIFICATION: SUCCESS")
                                                    else:
                                                        print(f"   ❌ FILE CONTENT VERIFICATION: FAILED")
                                                        print(f"      Original length: {len(test_file_content)}")
                                                        print(f"      Extracted length: {len(extracted_content)}")
                                                        print(f"      Original: {repr(test_file_content[:50])}...")
                                                        print(f"      Extracted: {repr(extracted_content[:50])}...")
                                                else:
                                                    print(f"   ❌ Could not download extracted file: {extracted_download.status_code}")
                                        else:
                                            print(f"   ❌ Extract failed: {extract_status_data.get('status')}")
                            
                            # Cleanup
                            try:
                                os.remove(embedded_file_path)
                            except:
                                pass
                                
        # Cleanup
        try:
            os.remove(test_file_path)
        except:
            pass
            
    except Exception as e:
        print(f"   ❌ File workflow error: {e}")
    
    print("\n=== FILE WORKFLOW TEST COMPLETE ===")

if __name__ == "__main__":
    test_file_workflow()
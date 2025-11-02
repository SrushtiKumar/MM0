#!/usr/bin/env python3
"""
Test Complete API Workflow - Test both embed and extract to verify content preservation
"""

import requests
import json
import time
import os

API_BASE = "http://localhost:8000/api"

def test_complete_workflow():
    """Test complete embed -> extract workflow"""
    
    print("=== COMPLETE WORKFLOW TEST ===\n")
    
    # Test content to embed
    test_content = "This is a test message to verify content preservation through the API workflow!"
    
    print("1. Testing embed operation...")
    
    try:
        # Use existing image as carrier
        with open("debug_embedded.png", 'rb') as carrier_file:
            files = {
                'carrier_file': carrier_file
            }
            data = {
                'password': 'workflow123',
                'carrier_type': 'image',
                'content_type': 'text',
                'text_content': test_content
            }
            
            print(f"   Embedding content: '{test_content}'")
            embed_response = requests.post(f"{API_BASE}/embed", files=files, data=data, timeout=30)
            print(f"   Embed Status: {embed_response.status_code}")
            
            if embed_response.status_code == 200:
                embed_result = embed_response.json()
                embed_operation_id = embed_result.get('operation_id')
                output_filename = embed_result.get('output_filename')
                print(f"   ✓ Embed Operation ID: {embed_operation_id}")
                print(f"   ✓ Output filename: {output_filename}")
                
                # Wait for embed to complete and check status
                print("\n2. Checking embed status...")
                status_response = requests.get(f"{API_BASE}/operations/{embed_operation_id}/status", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Embed Status: {status_data.get('status')}")
                    print(f"   Embed Progress: {status_data.get('progress')}%")
                    
                    if status_data.get('status') == 'completed':
                        # Now test extraction
                        print("\n3. Testing extract operation...")
                        
                        # Download the embedded file first
                        download_response = requests.get(f"{API_BASE}/download/{output_filename}", timeout=30)
                        if download_response.status_code == 200:
                            embedded_file_path = f"temp_embedded_{int(time.time())}.png"
                            with open(embedded_file_path, 'wb') as f:
                                f.write(download_response.content)
                            
                            print(f"   ✓ Downloaded embedded file: {embedded_file_path}")
                            
                            # Now extract from this file
                            with open(embedded_file_path, 'rb') as stego_file:
                                extract_files = {
                                    'stego_file': stego_file
                                }
                                extract_data = {
                                    'password': 'workflow123',
                                    'carrier_type': 'image',
                                    'output_format': 'preserve'
                                }
                                
                                extract_response = requests.post(f"{API_BASE}/extract", files=extract_files, data=extract_data, timeout=30)
                                print(f"   Extract Status: {extract_response.status_code}")
                                
                                if extract_response.status_code == 200:
                                    extract_result = extract_response.json()
                                    extract_operation_id = extract_result.get('operation_id')
                                    print(f"   ✓ Extract Operation ID: {extract_operation_id}")
                                    
                                    # Wait a moment then check extract status
                                    print("\n4. Checking extract status...")
                                    time.sleep(2)
                                    
                                    extract_status_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/status", timeout=10)
                                    if extract_status_response.status_code == 200:
                                        extract_status_data = extract_status_response.json()
                                        print(f"   Extract Status: {extract_status_data.get('status')}")
                                        print(f"   Extract Progress: {extract_status_data.get('progress')}%")
                                        
                                        if extract_status_data.get('status') == 'completed':
                                            # Check the extracted content
                                            result = extract_status_data.get('result', {})
                                            extracted_filename = result.get('filename')
                                            preview = result.get('preview')
                                            
                                            print(f"\n5. Extraction Results:")
                                            print(f"   Extracted filename: {extracted_filename}")
                                            print(f"   Preview: {repr(preview)}")
                                            print(f"   Data type: {result.get('data_type')}")
                                            
                                            # Compare content
                                            if preview and test_content in preview:
                                                print(f"   ✅ CONTENT PRESERVATION: SUCCESS")
                                                print(f"      Original: {repr(test_content)}")
                                                print(f"      Extracted: {repr(preview)}")
                                            else:
                                                print(f"   ❌ CONTENT PRESERVATION: FAILED")
                                                print(f"      Expected: {repr(test_content)}")
                                                print(f"      Got: {repr(preview)}")
                                            
                                            # Try to download the extracted file for verification
                                            if extracted_filename:
                                                print(f"\n6. Downloading extracted file...")
                                                extracted_download = requests.get(f"{API_BASE}/download/{extracted_filename}", timeout=30)
                                                if extracted_download.status_code == 200:
                                                    extracted_content = extracted_download.text
                                                    print(f"   Downloaded content: {repr(extracted_content)}")
                                                    
                                                    if extracted_content.strip() == test_content.strip():
                                                        print(f"   ✅ FULL CONTENT VERIFICATION: SUCCESS")
                                                    else:
                                                        print(f"   ❌ FULL CONTENT VERIFICATION: FAILED")
                                                        print(f"      Expected: {repr(test_content)}")
                                                        print(f"      Downloaded: {repr(extracted_content)}")
                                                else:
                                                    print(f"   ❌ Could not download extracted file: {extracted_download.status_code}")
                                        
                                        else:
                                            print(f"   ❌ Extract operation failed: {extract_status_data.get('status')}")
                                            if extract_status_data.get('error'):
                                                print(f"      Error: {extract_status_data.get('error')}")
                                    else:
                                        print(f"   ❌ Could not check extract status: {extract_status_response.status_code}")
                                        print(f"      Response: {extract_status_response.text}")
                                else:
                                    print(f"   ❌ Extract failed: {extract_response.status_code}")
                                    print(f"      Response: {extract_response.text}")
                            
                            # Cleanup
                            try:
                                os.remove(embedded_file_path)
                            except:
                                pass
                                
                        else:
                            print(f"   ❌ Could not download embedded file: {download_response.status_code}")
                    
                    else:
                        print(f"   ❌ Embed operation not completed: {status_data.get('status')}")
                        if status_data.get('error'):
                            print(f"      Error: {status_data.get('error')}")
                else:
                    print(f"   ❌ Could not check embed status: {status_response.status_code}")
            else:
                print(f"   ❌ Embed failed: {embed_response.status_code}")
                print(f"      Response: {embed_response.text}")
                
    except Exception as e:
        print(f"   ❌ Workflow error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== WORKFLOW TEST COMPLETE ===")

if __name__ == "__main__":
    test_complete_workflow()
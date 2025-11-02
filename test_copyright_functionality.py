#!/usr/bin/env python3
"""
Test Copyright Functionality - Verify copyright embedding and extraction
"""

import requests
import json
import time
import os

API_BASE = "http://localhost:8000/api"

def test_copyright_functionality():
    """Test the complete copyright workflow"""
    
    print("=== COPYRIGHT FUNCTIONALITY TEST ===\n")
    
    # Test copyright data
    copyright_data = {
        "author_name": "John Doe",
        "copyright_alias": "JD Productions LLC",
        "timestamp": "2025-11-03T10:30:00.000Z"
    }
    
    print("1. Testing copyright embedding...")
    
    try:
        # Use existing image as carrier
        with open("debug_embedded.png", 'rb') as carrier_file:
            files = {'carrier_file': carrier_file}
            data = {
                'password': 'copyright123',
                'carrier_type': 'image',
                'content_type': 'text',
                'text_content': json.dumps(copyright_data)
            }
            
            print(f"   Embedding copyright data: {json.dumps(copyright_data, indent=2)}")
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
                time.sleep(1)
                status_response = requests.get(f"{API_BASE}/operations/{embed_operation_id}/status", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Embed Status: {status_data.get('status')}")
                    
                    if status_data.get('status') == 'completed':
                        # Now test extraction
                        print("\n3. Testing copyright extraction...")
                        
                        # Download the embedded file first
                        download_response = requests.get(f"{API_BASE}/download/{output_filename}", timeout=30)
                        if download_response.status_code == 200:
                            embedded_file_path = f"temp_copyright_test_{int(time.time())}.png"
                            with open(embedded_file_path, 'wb') as f:
                                f.write(download_response.content)
                            
                            print(f"   ✓ Downloaded embedded file: {embedded_file_path}")
                            
                            # Extract copyright data
                            with open(embedded_file_path, 'rb') as stego_file:
                                extract_files = {
                                    'stego_file': stego_file
                                }
                                extract_data = {
                                    'password': 'copyright123',
                                    'carrier_type': 'image',
                                    'output_format': 'preserve'
                                }
                                
                                extract_response = requests.post(f"{API_BASE}/extract", files=extract_files, data=extract_data, timeout=30)
                                print(f"   Extract Status: {extract_response.status_code}")
                                
                                if extract_response.status_code == 200:
                                    extract_result = extract_response.json()
                                    extract_operation_id = extract_result.get('operation_id')
                                    print(f"   ✓ Extract Operation ID: {extract_operation_id}")
                                    
                                    # Wait and check extract status
                                    print("\n4. Checking extract status...")
                                    time.sleep(2)
                                    
                                    extract_status_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/status", timeout=10)
                                    if extract_status_response.status_code == 200:
                                        extract_status_data = extract_status_response.json()
                                        print(f"   Extract Status: {extract_status_data.get('status')}")
                                        
                                        if extract_status_data.get('status') == 'completed':
                                            # Check the extracted content
                                            result = extract_status_data.get('result', {})
                                            preview = result.get('preview')
                                            
                                            print(f"\n5. Copyright Extraction Results:")
                                            print(f"   Data type: {result.get('data_type')}")
                                            print(f"   Preview: {preview}")
                                            
                                            # Parse and verify copyright data
                                            try:
                                                extracted_copyright = json.loads(preview)
                                                print(f"\n6. Parsed Copyright Data:")
                                                print(f"   Author Name: {extracted_copyright.get('author_name')}")
                                                print(f"   Copyright Alias: {extracted_copyright.get('copyright_alias')}")
                                                print(f"   Timestamp: {extracted_copyright.get('timestamp')}")
                                                
                                                # Verify data integrity
                                                success = (
                                                    extracted_copyright.get('author_name') == copyright_data['author_name'] and
                                                    extracted_copyright.get('copyright_alias') == copyright_data['copyright_alias'] and
                                                    extracted_copyright.get('timestamp') == copyright_data['timestamp']
                                                )
                                                
                                                if success:
                                                    print(f"\n✅ COPYRIGHT TEST: SUCCESS")
                                                    print("   All copyright fields preserved correctly!")
                                                else:
                                                    print(f"\n❌ COPYRIGHT TEST: FAILED")
                                                    print("   Copyright data mismatch")
                                                    
                                            except json.JSONDecodeError:
                                                print(f"\n❌ COPYRIGHT TEST: FAILED")
                                                print("   Could not parse extracted data as JSON")
                                        
                                        else:
                                            print(f"   ❌ Extract operation failed: {extract_status_data.get('status')}")
                            
                            # Cleanup
                            try:
                                os.remove(embedded_file_path)
                            except:
                                pass
                                
                        else:
                            print(f"   ❌ Could not download embedded file: {download_response.status_code}")
                    
                    else:
                        print(f"   ❌ Embed operation not completed: {status_data.get('status')}")
            else:
                print(f"   ❌ Embed failed: {embed_response.status_code}")
                print(f"      Response: {embed_response.text}")
                
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== COPYRIGHT TEST COMPLETE ===")

if __name__ == "__main__":
    test_copyright_functionality()
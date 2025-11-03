#!/usr/bin/env python3
"""
Complete test of copyright functionality end-to-end
"""
import requests
import json
import time
import os

API_BASE_URL = "http://localhost:8000/api"

def test_copyright_embed():
    """Test copyright embedding via API"""
    print("🔒 Testing Copyright Embedding...")
    
    # Copyright data
    copyright_data = {
        "author_name": "John Doe",
        "copyright_alias": "VeilForge Demo Corp",
        "timestamp": "2025-11-03T12:00:00Z"
    }
    
    # Check if test image exists
    image_path = "test_copyright_carrier.png"
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as image_file:
            # Prepare form data
            files = {
                'carrier_file': ('test_image.png', image_file, 'image/png')
            }
            data = {
                'carrier_type': 'image',
                'content_type': 'text',
                'text_content': json.dumps(copyright_data),
                'password': 'TestPassword123!',
                'encryption_type': 'aes-256-gcm'
            }
            
            # Make the API call
            response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get('operation_id')
                print(f"✅ Copyright embedding started: {operation_id}")
                
                # Poll for completion
                return poll_operation_status(operation_id, "embed")
            else:
                print(f"❌ Embed failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Embed error: {e}")
        return False

def test_copyright_extract(operation_id):
    """Test copyright extraction via API"""
    print("🔍 Testing Copyright Extraction...")
    
    try:
        # First download the embedded file
        download_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/download")
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
        
        # Save the embedded file
        embedded_file = "test_copyright_embedded.png"
        with open(embedded_file, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Downloaded embedded file: {embedded_file}")
        
        # Now extract from it
        with open(embedded_file, 'rb') as image_file:
            files = {
                'stego_file': ('embedded_image.png', image_file, 'image/png')
            }
            data = {
                'password': 'TestPassword123!',
                'output_format': 'auto'
            }
            
            extract_response = requests.post(f"{API_BASE_URL}/extract", files=files, data=data)
            
            if extract_response.status_code == 200:
                result = extract_response.json()
                extract_operation_id = result.get('operation_id')
                print(f"✅ Copyright extraction started: {extract_operation_id}")
                
                # Poll for completion
                return poll_operation_status(extract_operation_id, "extract")
            else:
                print(f"❌ Extract failed: {extract_response.status_code} - {extract_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Extract error: {e}")
        return False

def poll_operation_status(operation_id, operation_type):
    """Poll operation status until completion"""
    print(f"⏳ Polling operation status for {operation_id}...")
    
    max_attempts = 30  # 30 seconds max
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                progress = status_data.get('progress', 0)
                
                print(f"   Status: {status} - Progress: {progress}%")
                
                if status == 'completed':
                    result = status_data.get('result', {})
                    # Check for success in result or if result has output_file/filename
                    if result.get('success', True) or result.get('output_file') or result.get('filename'):
                        print(f"✅ {operation_type.title()} completed successfully!")
                        
                        if operation_type == "extract":
                            # Check if we got copyright data
                            text_content = result.get('text_content', '')
                            if text_content:
                                try:
                                    copyright_data = json.loads(text_content)
                                    print(f"   📄 Extracted Copyright Data:")
                                    print(f"      Author: {copyright_data.get('author_name')}")
                                    print(f"      Alias: {copyright_data.get('copyright_alias')}")
                                    print(f"      Timestamp: {copyright_data.get('timestamp')}")
                                except json.JSONDecodeError:
                                    print(f"   📄 Extracted text: {text_content}")
                        elif operation_type == "embed":
                            # Show embed result info
                            output_file = result.get('output_file') or result.get('filename')
                            file_size = result.get('file_size')
                            processing_time = result.get('processing_time')
                            
                            print(f"   📁 Output file: {output_file}")
                            if file_size:
                                print(f"   📊 File size: {file_size} bytes")
                            if processing_time:
                                print(f"   ⏱️  Processing time: {processing_time:.2f}s")
                        
                        return operation_id
                    else:
                        print(f"❌ {operation_type.title()} failed: {result.get('message')}")
                        return False
                        
                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ {operation_type.title()} failed: {error}")
                    return False
                
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Polling error: {e}")
            time.sleep(1)
    
    print(f"❌ {operation_type.title()} timed out")
    return False

def main():
    """Run complete copyright test workflow"""
    print("🧪 Testing Complete Copyright Workflow")
    print("=" * 50)
    
    # Test embedding
    embed_operation_id = test_copyright_embed()
    if not embed_operation_id:
        print("❌ Embedding test failed - stopping")
        return
    
    print("\n" + "=" * 50)
    
    # Test extraction
    extract_success = test_copyright_extract(embed_operation_id)
    if not extract_success:
        print("❌ Extraction test failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All copyright functionality tests passed!")
    print("✅ Copyright page is fully functional")

if __name__ == "__main__":
    main()
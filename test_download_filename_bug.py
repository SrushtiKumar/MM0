"""
Test to reproduce the .xip file extension issue with copyright embedding
"""

import requests
import os
import json

API_URL = "http://localhost:8000/api"
TEST_IMAGE = "copyright_demo_file.png"

def test_copyright_embedding_download():
    """Test copyright embedding and check download filename"""
    print("🧪 Testing copyright embedding download filename issue...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Test image {TEST_IMAGE} not found")
        return False
    
    try:
        # Prepare copyright data
        copyright_data = {
            "author_name": "Test Author Download Fix",
            "copyright_alias": "TADF_2024",
            "timestamp": "2024-11-03T16:00:00Z"
        }
        
        # Embed copyright
        with open(TEST_IMAGE, 'rb') as f:
            files = {'carrier_file': (TEST_IMAGE, f, 'image/png')}
            
            data = {
                'content_type': 'text',
                'text_content': json.dumps(copyright_data),
                'password': 'DownloadTest123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image'
            }
            
            print("📤 Embedding copyright data...")
            response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        if response.status_code != 200:
            print(f"❌ Embed failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
        result = response.json()
        operation_id = result.get('operation_id')
        print(f"✅ Embed initiated: {operation_id}")
        
        # Wait for completion
        import time
        for attempt in range(15):
            time.sleep(1)
            
            status_response = requests.get(f"{API_URL}/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                
                if current_status == 'completed':
                    result_data = status_data.get('result', {})
                    output_filename = result_data.get('filename', 'UNKNOWN')
                    print(f"✅ Operation completed")
                    print(f"📁 Result filename: {output_filename}")
                    
                    # Check if filename has correct extension
                    if output_filename.lower().endswith('.png'):
                        print("✅ Filename has correct .png extension")
                    else:
                        print(f"❌ Wrong filename extension: {output_filename}")
                        print("🔍 This is the bug we need to fix!")
                    
                    # Try to download and check the actual response
                    download_response = requests.get(f"{API_URL}/operations/{operation_id}/download")
                    if download_response.status_code == 200:
                        content_disposition = download_response.headers.get('Content-Disposition', '')
                        print(f"📥 Download Content-Disposition: {content_disposition}")
                        
                        content_type = download_response.headers.get('Content-Type', '')
                        print(f"📄 Download Content-Type: {content_type}")
                        
                        # Extract filename from Content-Disposition
                        if 'filename=' in content_disposition:
                            download_filename = content_disposition.split('filename=')[1].strip('"')
                            print(f"🏷️ Download filename: {download_filename}")
                            
                            if download_filename.lower().endswith('.png'):
                                print("✅ Download has correct extension")
                                return True
                            else:
                                print(f"❌ Download has wrong extension: {download_filename}")
                                return False
                        else:
                            print("❌ No filename in Content-Disposition header")
                            return False
                    else:
                        print(f"❌ Download failed: {download_response.status_code}")
                        return False
                        
                elif current_status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ Operation failed: {error}")
                    return False
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
                
        print("⏰ Operation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_copyright_embedding_download()
    print(f"\n{'✅ DOWNLOAD TEST: PASSED' if success else '❌ DOWNLOAD TEST: FAILED'}")
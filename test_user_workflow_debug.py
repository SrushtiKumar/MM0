"""
Test to simulate the exact user scenario with frontend handling
This will help identify if the issue is with the frontend download handling
"""

import requests
import json
import time

API_URL = "http://localhost:8000/api"

def test_complete_user_workflow():
    """Test the complete workflow that mirrors what the user experienced"""
    print("🔍 Testing complete user workflow for copyright embedding...")
    
    # Use a 4KB image like the user
    test_image = "copyright_demo_file.png"
    
    if not os.path.exists(test_image):
        print(f"❌ Test image {test_image} not found")
        return False
    
    # Step 1: Get supported formats (like frontend does)
    print("📋 Step 1: Getting supported formats...")
    formats_response = requests.get(f"{API_URL}/supported-formats")
    if formats_response.status_code == 200:
        print("✅ Supported formats loaded")
    else:
        print(f"❌ Supported formats failed: {formats_response.status_code}")
        return False
    
    # Step 2: Embed copyright data (exactly like frontend)
    print("📤 Step 2: Embedding copyright data...")
    
    copyright_data = {
        "author_name": "Test User Workflow",
        "copyright_alias": "TUW_2024",
        "timestamp": "2024-11-03T16:30:00Z"
    }
    
    try:
        with open(test_image, 'rb') as f:
            files = {'carrier_file': (test_image, f, 'image/png')}
            
            # Use same parameters as frontend would send
            data = {
                'content_type': 'text',
                'text_content': json.dumps(copyright_data),
                'password': 'UserWorkflowTest123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image',
                'project_name': 'Copyright User Test',
                'project_description': 'Testing user workflow'
            }
            
            embed_response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code}")
            print(f"Response: {embed_response.text}")
            return False
            
        embed_result = embed_response.json()
        operation_id = embed_result.get('operation_id')
        print(f"✅ Embed initiated: {operation_id}")
        
        # Step 3: Poll for completion (like frontend does)
        print("⏳ Step 3: Polling for completion...")
        
        for attempt in range(20):  # Longer timeout
            time.sleep(1)
            
            status_response = requests.get(f"{API_URL}/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                progress = status_data.get('progress', 0)
                
                print(f"  Attempt {attempt + 1}: Status = {current_status}, Progress = {progress}%")
                
                if current_status == 'completed':
                    result_data = status_data.get('result', {})
                    print("✅ Operation completed successfully!")
                    
                    # Check the result structure
                    print("📊 Result data structure:")
                    for key, value in result_data.items():
                        print(f"  {key}: {value}")
                    
                    # Step 4: Download (like frontend does)
                    print("📥 Step 4: Downloading result...")
                    
                    download_response = requests.get(f"{API_URL}/operations/{operation_id}/download")
                    
                    if download_response.status_code == 200:
                        # Check headers
                        headers = download_response.headers
                        print("📋 Download response headers:")
                        for key, value in headers.items():
                            print(f"  {key}: {value}")
                        
                        # Check for filename in Content-Disposition
                        content_disposition = headers.get('Content-Disposition', '')
                        if 'filename=' in content_disposition:
                            filename = content_disposition.split('filename=')[1].strip('"')
                            print(f"🏷️ Server-provided filename: {filename}")
                            
                            if filename.lower().endswith('.png'):
                                print("✅ Correct .png extension from server")
                            else:
                                print(f"❌ Wrong extension from server: {filename}")
                        else:
                            print("⚠️ No filename in Content-Disposition")
                        
                        # Check what the frontend would use for download name
                        frontend_filename = result_data.get('filename') or result_data.get('output_filename') or 'copyright_result.zip'
                        print(f"🖥️ Frontend would use filename: {frontend_filename}")
                        
                        if frontend_filename.lower().endswith('.png'):
                            print("✅ Frontend filename has correct extension")
                            return True
                        else:
                            print(f"❌ Frontend filename has wrong extension: {frontend_filename}")
                            print("🔍 This is likely the source of the .xip issue!")
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
        print(f"❌ Workflow error: {e}")
        return False

if __name__ == "__main__":
    import os
    success = test_complete_user_workflow()
    print(f"\n{'✅ USER WORKFLOW: WORKING' if success else '❌ USER WORKFLOW: ISSUES FOUND'}")
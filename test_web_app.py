#!/usr/bin/env python3

"""
Test script to verify the VeilForge web application works end-to-end
"""

import requests
import time
import os
from PIL import Image
import numpy as np

def create_test_image():
    """Create a test image for steganography."""
    # Create a test image
    img_array = np.random.randint(0, 256, (400, 400, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    test_image = "test_web_app.png"
    img.save(test_image)
    return test_image

def test_web_application():
    """Test the complete web application functionality."""
    print("🔧 Testing VeilForge Web Application")
    
    base_url = "http://localhost:8000"
    
    try:
        # Check if server is running
        response = requests.get(base_url)
        if response.status_code != 200:
            print("❌ Server is not running or not responding")
            return False
        
        print("✅ Server is running")
        
        # Create test image
        test_image = create_test_image()
        print(f"✅ Created test image: {test_image}")
        
        # Test message
        test_message = "Hello from VeilForge! This is a test message. 🚀"
        password = "testpass123"
        
        print(f"📝 Test message: {test_message}")
        print(f"🔑 Password: {password}")
        
        # Test Hide Operation
        print("\n🔒 Testing Hide Operation...")
        
        with open(test_image, 'rb') as f:
            files = {'container_file': f}
            data = {
                'secret_text': test_message,
                'password': password,
                'enhanced_mode': False
            }
            
            response = requests.post(f"{base_url}/api/hide", files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Hide request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        hide_result = response.json()
        job_id = hide_result['job_id']
        print(f"✅ Hide operation started: {job_id}")
        
        # Poll for completion
        max_wait = 30  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            response = requests.get(f"{base_url}/api/job/{job_id}")
            if response.status_code == 200:
                job_status = response.json()
                print(f"📊 Job status: {job_status['status']} - {job_status.get('message', '')}")
                
                if job_status['status'] == 'completed':
                    print("✅ Hide operation completed successfully!")
                    break
                elif job_status['status'] == 'failed':
                    print(f"❌ Hide operation failed: {job_status.get('error', 'Unknown error')}")
                    return False
            
            time.sleep(1)
            wait_time += 1
        
        if wait_time >= max_wait:
            print("❌ Hide operation timed out")
            return False
        
        # Test Download
        print("\n📥 Testing Download...")
        
        response = requests.get(f"{base_url}/api/download/{job_id}")
        if response.status_code != 200:
            print(f"❌ Download failed: {response.status_code}")
            return False
        
        # Save downloaded file
        stego_file = "downloaded_stego.png"
        with open(stego_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded stego file: {stego_file}")
        
        # Test Extract Operation
        print("\n🔓 Testing Extract Operation...")
        
        with open(stego_file, 'rb') as f:
            files = {'stego_file': f}
            data = {'password': password}
            
            response = requests.post(f"{base_url}/api/extract", files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Extract request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        extract_result = response.json()
        extract_job_id = extract_result['job_id']
        print(f"✅ Extract operation started: {extract_job_id}")
        
        # Poll for extract completion
        wait_time = 0
        
        while wait_time < max_wait:
            response = requests.get(f"{base_url}/api/job/{extract_job_id}")
            if response.status_code == 200:
                job_status = response.json()
                print(f"📊 Extract status: {job_status['status']} - {job_status.get('message', '')}")
                
                if job_status['status'] == 'completed':
                    print("✅ Extract operation completed successfully!")
                    break
                elif job_status['status'] == 'failed':
                    print(f"❌ Extract operation failed: {job_status.get('error', 'Unknown error')}")
                    return False
            
            time.sleep(1)
            wait_time += 1
        
        if wait_time >= max_wait:
            print("❌ Extract operation timed out")
            return False
        
        # Download extracted data
        print("\n📥 Testing Extract Download...")
        
        response = requests.get(f"{base_url}/api/download/{extract_job_id}")
        if response.status_code != 200:
            print(f"❌ Extract download failed: {response.status_code}")
            return False
        
        # Read extracted data
        extracted_data = response.content.decode('utf-8')
        print(f"📝 Extracted message: {extracted_data}")
        
        # Verify
        if extracted_data.strip() == test_message:
            print("\n🎉 SUCCESS: Complete end-to-end test passed!")
            print("✅ Hide operation works")
            print("✅ Download works") 
            print("✅ Extract operation works")
            print("✅ Data integrity verified")
            return True
        else:
            print(f"\n❌ FAILURE: Messages don't match!")
            print(f"   Original: {test_message}")
            print(f"   Extracted: {extracted_data}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test files
        for filename in [test_image, "downloaded_stego.png"]:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🧹 Cleaned up: {filename}")

if __name__ == "__main__":
    success = test_web_application()
    if success:
        print("\n🎊 VeilForge Web Application is working perfectly!")
    else:
        print("\n💥 VeilForge Web Application test failed")
    
    input("\nPress Enter to continue...")
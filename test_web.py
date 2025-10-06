"""
Test script for VeilForge Web Application
Run this to verify the web app is working correctly.
"""

import requests
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PASSWORD = "test123456"

def test_api_endpoints():
    """Test basic API endpoints"""
    print("Testing VeilForge Web Application...")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/supported-formats")
        if response.status_code == 200:
            print("✅ Server is running")
            formats = response.json()
            print(f"   Supported formats: {list(formats.keys())}")
        else:
            print("❌ Server not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
        return False
    
    # Test with a simple text file
    test_file_path = "test_container.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test container file for steganography. " * 100)
    
    try:
        # Test analyze endpoint
        print("\n📊 Testing capacity analysis...")
        with open(test_file_path, "rb") as f:
            files = {"file": f}
            data = {"request_data": "{}"}
            response = requests.post(f"{BASE_URL}/api/analyze", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful")
            print(f"   Container type: {result.get('container_type', 'unknown')}")
            print(f"   Estimated capacity: {result.get('estimated_capacity', 0)} bytes")
            print(f"   Safe capacity: {result.get('safe_capacity', 0)} bytes")
        else:
            print(f"❌ Analysis failed: {response.text}")
        
        # Test hide endpoint (basic mode)
        print("\n🔒 Testing hide operation...")
        with open(test_file_path, "rb") as f:
            files = {"container_file": f}
            request_data = {
                "password": TEST_PASSWORD,
                "data": "This is a secret test message!",
                "is_enhanced": False
            }
            data = {"request_data": str(request_data).replace("'", '"')}
            response = requests.post(f"{BASE_URL}/api/hide", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ Hide operation started (Job ID: {job_id})")
            
            # Poll job status
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                response = requests.get(f"{BASE_URL}/api/job/{job_id}")
                if response.status_code == 200:
                    job_status = response.json()
                    print(f"   Status: {job_status['status']} - {job_status['message']}")
                    
                    if job_status['status'] == 'completed':
                        print("✅ Hide operation completed successfully")
                        
                        # Download the result
                        response = requests.get(f"{BASE_URL}/api/download/{job_id}")
                        if response.status_code == 200:
                            output_file = f"test_output_{job_id}.txt"
                            with open(output_file, "wb") as f:
                                f.write(response.content)
                            print(f"✅ Downloaded result to {output_file}")
                            
                            # Test extract operation
                            print("\n🔓 Testing extract operation...")
                            with open(output_file, "rb") as f:
                                files = {"container_file": f}
                                request_data = {
                                    "password": TEST_PASSWORD,
                                    "is_enhanced": False
                                }
                                data = {"request_data": str(request_data).replace("'", '"')}
                                response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
                            
                            if response.status_code == 200:
                                extract_result = response.json()
                                extract_job_id = extract_result.get("job_id")
                                print(f"✅ Extract operation started (Job ID: {extract_job_id})")
                                
                                # Poll extract job status
                                for j in range(30):  # Wait up to 30 seconds
                                    time.sleep(1)
                                    response = requests.get(f"{BASE_URL}/api/job/{extract_job_id}")
                                    if response.status_code == 200:
                                        extract_status = response.json()
                                        print(f"   Status: {extract_status['status']} - {extract_status['message']}")
                                        
                                        if extract_status['status'] == 'completed':
                                            print("✅ Extract operation completed successfully")
                                            
                                            # Download extracted data
                                            response = requests.get(f"{BASE_URL}/api/download/{extract_job_id}")
                                            if response.status_code == 200:
                                                extracted_file = f"extracted_{extract_job_id}.txt"
                                                with open(extracted_file, "wb") as f:
                                                    f.write(response.content)
                                                
                                                # Verify content
                                                with open(extracted_file, "r") as f:
                                                    extracted_content = f.read()
                                                
                                                if "This is a secret test message!" in extracted_content:
                                                    print("✅ Message extracted successfully and verified!")
                                                else:
                                                    print(f"❌ Extracted content doesn't match: {extracted_content}")
                                                
                                                # Cleanup
                                                os.remove(extracted_file)
                                            break
                                        elif extract_status['status'] == 'failed':
                                            print(f"❌ Extract operation failed: {extract_status['message']}")
                                            break
                            
                            # Cleanup
                            os.remove(output_file)
                        break
                    elif job_status['status'] == 'failed':
                        print(f"❌ Hide operation failed: {job_status['message']}")
                        break
        else:
            print(f"❌ Hide operation failed: {response.text}")
    
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print("\n" + "=" * 50)
    print("✅ VeilForge Web Application test completed!")
    print("\nTo use the web interface, open your browser to:")
    print(f"   {BASE_URL}")
    return True

if __name__ == "__main__":
    test_api_endpoints()
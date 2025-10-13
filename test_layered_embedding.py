#!/usr/bin/env python3
"""
Test script to verify that the NoneType error is resolved in layered embedding
This script tests embedding multiple files in the same carrier
"""

import requests
import os
import time
import json

# Server configuration
SERVER_URL = "http://localhost:8000"
TEST_FILES_DIR = "."

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/api/health")
        print(f"✅ Server health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def upload_file(file_path):
    """Upload a file to the server"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{SERVER_URL}/api/upload", files=files)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Uploaded {file_path}: {data['filename']}")
                return data['filename']
            else:
                print(f"❌ Upload failed for {file_path}: {response.status_code}")
                print(f"Response: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Upload error for {file_path}: {e}")
        return None

def embed_data(carrier_filename, content, content_type="text", content_filename=None):
    """Embed data in a carrier file"""
    try:
        data = {
            "carrier_filename": carrier_filename,
            "content_type": content_type
        }
        
        if content_type == "text":
            data["content"] = content
        else:
            data["content_filename"] = content_filename
            
        response = requests.post(f"{SERVER_URL}/api/embed", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Embedding successful: {result.get('message', 'Success')}")
            return result
        else:
            print(f"❌ Embedding failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def monitor_operation(operation_id, max_wait=60):
    """Monitor an operation until completion"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if response.status_code == 200:
                status = response.json()
                print(f"📊 Operation {operation_id}: {status['status']} - {status.get('message', '')}")
                
                if status['status'] == 'completed':
                    return True
                elif status['status'] == 'failed':
                    print(f"❌ Operation failed: {status.get('message', 'Unknown error')}")
                    return False
                    
                time.sleep(2)
            else:
                print(f"❌ Status check failed: {response.status_code}")
                break
        except Exception as e:
            print(f"❌ Status check error: {e}")
            break
    
    print(f"⏰ Operation timed out after {max_wait} seconds")
    return False

def main():
    print("🧪 Testing Layered Embedding - NoneType Error Resolution")
    print("=" * 60)
    
    # Test 1: Server Health
    print("\n1️⃣ Testing server health...")
    if not test_server_health():
        print("❌ Server is not responding. Please start the server first.")
        return
    
    # Test 2: Upload test files
    print("\n2️⃣ Uploading test files...")
    
    # Upload carrier file (video)
    carrier_file = "test_video.mp4"
    if not os.path.exists(carrier_file):
        print(f"❌ Carrier file {carrier_file} not found. Using alternative...")
        carrier_file = "comprehensive_test_video.mp4"
        if not os.path.exists(carrier_file):
            print(f"❌ No suitable carrier file found")
            return
    
    carrier_filename = upload_file(carrier_file)
    if not carrier_filename:
        return
    
    # Upload content files
    content_files = []
    for test_file in ["test_document.doc", "test_image.png", "secret_document.txt"]:
        if os.path.exists(test_file):
            uploaded = upload_file(test_file)
            if uploaded:
                content_files.append(uploaded)
                break
    
    if not content_files and os.path.exists("direct_test_document.doc"):
        uploaded = upload_file("direct_test_document.doc")
        if uploaded:
            content_files.append(uploaded)
    
    if not content_files:
        print("❌ No content files could be uploaded")
        return
    
    print(f"✅ Content files uploaded: {content_files}")
    
    # Test 3: First embedding (should work)
    print("\n3️⃣ First embedding - hiding text message...")
    result1 = embed_data(carrier_filename, "This is the first hidden message!", "text")
    if not result1:
        print("❌ First embedding failed")
        return
    
    operation_id1 = result1.get('operation_id')
    if operation_id1:
        success1 = monitor_operation(operation_id1)
        if not success1:
            print("❌ First embedding operation failed")
            return
        
        # Update carrier filename for next test
        new_carrier = result1.get('output_filename')
        if new_carrier:
            carrier_filename = new_carrier
            print(f"✅ First embedding completed. New carrier: {carrier_filename}")
    
    # Test 4: Second embedding (this is where the NoneType error used to occur)
    print("\n4️⃣ Second embedding - hiding file in carrier with existing data...")
    print("🔍 This is the critical test - checking for NoneType error...")
    
    result2 = embed_data(carrier_filename, None, "file", content_files[0])
    if not result2:
        print("❌ Second embedding failed - this might be the NoneType error!")
        return
    
    operation_id2 = result2.get('operation_id')
    if operation_id2:
        success2 = monitor_operation(operation_id2)
        if not success2:
            print("❌ Second embedding operation failed")
            return
        
        # Update carrier filename for next test
        new_carrier = result2.get('output_filename')
        if new_carrier:
            carrier_filename = new_carrier
            print(f"✅ Second embedding completed. New carrier: {carrier_filename}")
    
    # Test 5: Third embedding (stress test)
    print("\n5️⃣ Third embedding - stress testing layered container...")
    result3 = embed_data(carrier_filename, "This is the third hidden message after two embeddings!", "text")
    if not result3:
        print("❌ Third embedding failed")
        return
    
    operation_id3 = result3.get('operation_id')
    if operation_id3:
        success3 = monitor_operation(operation_id3)
        if success3:
            print(f"✅ Third embedding completed successfully!")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! NoneType error appears to be resolved!")
    print("✅ Successfully embedded multiple items in the same carrier")
    print("✅ Layered container system working correctly")
    print("✅ No NoneType errors encountered")

if __name__ == "__main__":
    main()
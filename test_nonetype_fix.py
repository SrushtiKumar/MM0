#!/usr/bin/env python3
"""
Direct test for NoneType error resolution using existing files
"""

import requests
import json
import time

SERVER_URL = "http://localhost:8000"

def test_embed_in_existing_carrier():
    """Test embedding in a carrier that already has hidden data"""
    
    # Use a carrier that already contains layered data
    carrier_with_data = "carrier_stego_carrier_file_example_MP4_640_3MG_1760283794_4fd50fe8_1760283795_8eaaabcc_1760284314_aa81354c.mp4"
    content_file = "content_doc_1760284314_87a26158.docx"
    
    print(f"🧪 Testing second embedding in carrier with existing data")
    print(f"📹 Carrier: {carrier_with_data}")
    print(f"📄 Content: {content_file}")
    
    # Test 1: Embed text in carrier with existing data
    print("\n1️⃣ Embedding text message...")
    
    data = {
        "carrier_filename": carrier_with_data,
        "content_type": "text",
        "content": "This is a test message to check if NoneType error is resolved!"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/api/embed", json=data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ First embedding successful!")
            print(f"Operation ID: {result.get('operation_id')}")
            
            # Monitor operation
            operation_id = result.get('operation_id')
            if operation_id:
                print("📊 Monitoring operation...")
                success = monitor_operation(operation_id)
                if success:
                    print("✅ Text embedding completed successfully!")
                    return True
                else:
                    print("❌ Text embedding failed during processing")
                    return False
        else:
            print(f"❌ Embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during embedding: {e}")
        return False

def test_embed_file_in_existing_carrier():
    """Test embedding a file in carrier with existing layered data"""
    
    # Use a carrier that has multiple layers already
    carrier_with_layers = "carrier_stego_carrier_file_example_MP4_640_3MG_1760283794_4fd50fe8_1760283795_8eaaabcc_1760284314_aa81354c.mp4"
    content_file = "content_doc_1760284314_87a26158.docx"
    
    print(f"\n2️⃣ Testing file embedding in carrier with layered data...")
    print(f"📹 Carrier: {carrier_with_layers}")
    print(f"📄 Content: {content_file}")
    
    data = {
        "carrier_filename": carrier_with_layers,
        "content_type": "file",
        "content_filename": content_file
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/api/embed", json=data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Second embedding request successful!")
            print(f"Operation ID: {result.get('operation_id')}")
            
            # Monitor operation - this is where NoneType error used to occur
            operation_id = result.get('operation_id')
            if operation_id:
                print("📊 Monitoring operation (critical test for NoneType error)...")
                success = monitor_operation(operation_id)
                if success:
                    print("🎉 File embedding completed successfully! No NoneType error!")
                    return True
                else:
                    print("❌ File embedding failed - possible NoneType error")
                    return False
        else:
            print(f"❌ Embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during file embedding: {e}")
        return False

def monitor_operation(operation_id, max_wait=30):
    """Monitor operation with detailed status"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   📊 {status['status']} - {status.get('message', '')}")
                
                if status['status'] == 'completed':
                    return True
                elif status['status'] == 'failed':
                    print(f"   ❌ Failure reason: {status.get('message', 'Unknown error')}")
                    return False
                    
                time.sleep(2)
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                break
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
            break
    
    print(f"   ⏰ Operation timed out")
    return False

def main():
    print("🔍 DIRECT TEST: NoneType Error Resolution")
    print("=" * 50)
    
    # Check server health
    try:
        health = requests.get(f"{SERVER_URL}/api/health")
        print(f"✅ Server health: {health.status_code}")
    except:
        print("❌ Server not responding")
        return
    
    # Test 1: Text embedding in existing carrier
    success1 = test_embed_in_existing_carrier()
    
    # Test 2: File embedding in existing carrier (critical test)
    success2 = test_embed_file_in_existing_carrier()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        print("✅ NoneType error appears to be RESOLVED!")
        print("✅ Layered embedding working correctly!")
    else:
        print("❌ Some tests failed")
        print("🔍 NoneType error may still exist")

if __name__ == "__main__":
    main()
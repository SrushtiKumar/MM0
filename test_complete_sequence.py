#!/usr/bin/env python3
"""
Test NoneType resolution by creating test files and uploading them via the API
"""
import requests
import os
import time
from pathlib import Path

SERVER_URL = "http://localhost:8000"

def create_test_files():
    """Create simple test files for embedding"""
    
    # Create a simple text file
    with open("test_message.txt", "w") as f:
        f.write("This is a test message for embedding!")
    
    # Create a simple carrier file (copy an existing one)
    import shutil
    carrier_source = None
    for candidate in ["test_video.mp4", "comprehensive_test_video.mp4", "debug_test_video.mp4"]:
        if os.path.exists(candidate):
            carrier_source = candidate
            break
    
    if carrier_source:
        shutil.copy2(carrier_source, "clean_carrier.mp4")
        print(f"✅ Created clean_carrier.mp4 from {carrier_source}")
        return True
    else:
        print("❌ No suitable carrier file found")
        return False

def test_embedding_sequence():
    """Test the sequence that causes NoneType error"""
    
    print("🧪 Testing NoneType Error Resolution - Complete Sequence")
    print("=" * 60)
    
    # Step 1: Create test files
    if not create_test_files():
        return False
    
    # Step 2: First embedding
    print("\n1️⃣ First embedding - initial data in clean carrier...")
    
    with open("clean_carrier.mp4", "rb") as carrier_file, open("test_message.txt", "rb") as content_file:
        files = {
            "carrier_file": carrier_file,
            "content_file": content_file
        }
        data = {
            "content_type": "file",
            "password": "test123",
            "encryption_type": "aes-256-gcm"
        }
        
        try:
            response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ First embedding started: {result.get('operation_id')}")
                
                # Monitor first operation
                if monitor_operation(result.get('operation_id')):
                    first_output = result.get('output_filename')
                    print(f"✅ First embedding completed: {first_output}")
                    
                    # Step 3: Second embedding (critical test)
                    print(f"\n2️⃣ Second embedding - this is where NoneType error occurred...")
                    return test_second_embedding(first_output)
                else:
                    print("❌ First embedding failed")
                    return False
            else:
                print(f"❌ First embedding request failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during first embedding: {e}")
            return False

def test_second_embedding(carrier_with_data):
    """Test second embedding in carrier that already has data"""
    
    # Create second content
    with open("second_message.txt", "w") as f:
        f.write("This is the SECOND message - testing for NoneType error!")
    
    # Copy the carrier with data from uploads directory
    uploads_path = Path("uploads") / carrier_with_data
    if uploads_path.exists():
        carrier_path = f"carrier_with_data_{int(time.time())}.mp4"
        import shutil
        shutil.copy2(uploads_path, carrier_path)
        print(f"✅ Copied carrier with data: {carrier_path}")
    else:
        print(f"❌ Cannot find carrier file: {uploads_path}")
        return False
    
    print(f"🔍 CRITICAL TEST: Embedding in carrier with existing layered data...")
    print(f"📹 Carrier: {carrier_path}")
    print(f"📄 Content: second_message.txt")
    
    with open(carrier_path, "rb") as carrier_file, open("second_message.txt", "rb") as content_file:
        files = {
            "carrier_file": carrier_file,
            "content_file": content_file
        }
        data = {
            "content_type": "file", 
            "password": "test123",
            "encryption_type": "aes-256-gcm"
        }
        
        try:
            response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Second embedding started: {result.get('operation_id')}")
                print(f"🔍 Monitoring for NoneType errors...")
                
                # This is the critical test - monitor for NoneType errors
                success = monitor_operation(result.get('operation_id'))
                if success:
                    print(f"🎉 SUCCESS! Second embedding completed without NoneType error!")
                    print(f"✅ NoneType error has been RESOLVED!")
                    return True
                else:
                    print(f"❌ Second embedding failed - NoneType error may still exist")
                    return False
            else:
                print(f"❌ Second embedding request failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during second embedding: {e}")
            return False

def monitor_operation(operation_id, max_wait=30):
    """Monitor operation with detailed output"""
    if not operation_id:
        return False
        
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
                    print(f"   ❌ Failure: {status.get('message', 'Unknown error')}")
                    return False
                    
                time.sleep(2)
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                break
        except Exception as e:
            print(f"   ❌ Status error: {e}")
            break
    
    print(f"   ⏰ Timed out")
    return False

def main():
    # Check server health
    try:
        health = requests.get(f"{SERVER_URL}/api/health")
        if health.status_code != 200:
            print("❌ Server not healthy")
            return
    except:
        print("❌ Server not responding")
        return
    
    print("✅ Server is healthy")
    
    # Run the complete test sequence
    success = test_embedding_sequence()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 NOTYPE ERROR RESOLUTION TEST: PASSED!")
        print("✅ Successfully embedded multiple files in same carrier")
        print("✅ No NoneType errors detected")
        print("✅ Layered container system working correctly")
    else:
        print("❌ NOTYPE ERROR RESOLUTION TEST: FAILED!")
        print("🔍 Please check server logs for detailed error information")

if __name__ == "__main__":
    main()
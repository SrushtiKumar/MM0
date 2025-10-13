#!/usr/bin/env python3
"""
Comprehensive test for mixed content type embedding in layered containers
Tests the specific scenario: hide file -> hide text -> hide another file
"""

import requests
import time
import os
from pathlib import Path

SERVER_URL = "http://localhost:8000"

def create_test_files():
    """Create test files for the mixed content type test"""
    
    # Create text files
    with open("first_message.txt", "w") as f:
        f.write("This is the FIRST hidden message!")
    
    with open("second_message.txt", "w") as f:
        f.write("This is the SECOND hidden message - testing mixed content types!")
    
    # Create a simple binary file
    with open("test_data.bin", "wb") as f:
        f.write(b"Binary test data: \x00\x01\x02\x03\xFF\xFE\xFD")
    
    # Use existing carrier file
    carrier_source = None
    for candidate in ["test_video.mp4", "comprehensive_test_video.mp4", "debug_test_video.mp4"]:
        if os.path.exists(candidate):
            carrier_source = candidate
            break
    
    if carrier_source:
        import shutil
        shutil.copy2(carrier_source, "mixed_test_carrier.mp4")
        print(f"✅ Created test carrier: mixed_test_carrier.mp4")
        return True
    else:
        print("❌ No suitable carrier file found")
        return False

def embed_content(carrier_file, content_file=None, text_content=None, password="test123"):
    """Embed content in carrier file"""
    
    with open(carrier_file, "rb") as cf:
        files = {"carrier_file": cf}
        data = {
            "password": password,
            "encryption_type": "aes-256-gcm"
        }
        
        if content_file:
            with open(content_file, "rb") as cont_f:
                files["content_file"] = cont_f
                data["content_type"] = "file"
                print(f"📁 Embedding file: {content_file}")
        else:
            data["content_type"] = "text"
            data["text_content"] = text_content
            print(f"📝 Embedding text: {text_content[:50]}...")
        
        try:
            response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get('operation_id')
                output_filename = result.get('output_filename')
                print(f"✅ Embedding started: {operation_id}")
                print(f"📤 Expected output: {output_filename}")
                
                if monitor_operation(operation_id):
                    return output_filename
                else:
                    return None
            else:
                print(f"❌ Embedding failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Exception during embedding: {e}")
            return None

def monitor_operation(operation_id, max_wait=30):
    """Monitor operation until completion"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if response.status_code == 200:
                status = response.json()
                print(f"  📊 {status['status']} - {status.get('message', '')}")
                
                if status['status'] == 'completed':
                    return True
                elif status['status'] == 'failed':
                    print(f"  ❌ Failure: {status.get('message', 'Unknown error')}")
                    return False
                    
                time.sleep(2)
            else:
                print(f"  ❌ Status check failed: {response.status_code}")
                break
        except Exception as e:
            print(f"  ❌ Status error: {e}")
            break
    
    print(f"  ⏰ Timed out")
    return False

def test_mixed_content_embedding():
    """Test the specific scenario that was causing NoneType errors"""
    
    print("🧪 TESTING MIXED CONTENT TYPE EMBEDDING")
    print("=" * 60)
    print("Scenario: File → Text → File (with same password)")
    print()
    
    # Step 1: Embed first file
    print("1️⃣ STEP 1: Embedding first file in clean carrier...")
    carrier1 = embed_content("mixed_test_carrier.mp4", content_file="first_message.txt")
    if not carrier1:
        print("❌ Step 1 failed")
        return False
    
    # Copy the result from uploads directory for next step
    uploads_carrier1 = Path("uploads") / carrier1
    if uploads_carrier1.exists():
        import shutil
        shutil.copy2(uploads_carrier1, "carrier_with_file.mp4")
        print(f"✅ Step 1 completed: carrier_with_file.mp4")
    else:
        print(f"❌ Cannot find output file: {uploads_carrier1}")
        return False
    
    # Step 2: Embed text message (this usually works)
    print("\n2️⃣ STEP 2: Embedding text message in carrier with existing file...")
    carrier2 = embed_content("carrier_with_file.mp4", text_content="This is a text message added to carrier with existing file!")
    if not carrier2:
        print("❌ Step 2 failed")
        return False
    
    # Copy the result for next step
    uploads_carrier2 = Path("uploads") / carrier2
    if uploads_carrier2.exists():
        import shutil
        shutil.copy2(uploads_carrier2, "carrier_with_file_and_text.mp4")
        print(f"✅ Step 2 completed: carrier_with_file_and_text.mp4")
    else:
        print(f"❌ Cannot find output file: {uploads_carrier2}")
        return False
    
    # Step 3: Embed another file (this is where NoneType error occurred)
    print("\n3️⃣ STEP 3: Embedding second file in carrier with existing file+text...")
    print("🔍 CRITICAL TEST: This is where NoneType error used to occur!")
    carrier3 = embed_content("carrier_with_file_and_text.mp4", content_file="second_message.txt")
    if not carrier3:
        print("❌ Step 3 failed - NoneType error may still exist")
        return False
    
    print(f"✅ Step 3 completed: {carrier3}")
    
    # Step 4: Try one more embedding to stress test
    print("\n4️⃣ STEP 4: Embedding binary file for stress test...")
    uploads_carrier3 = Path("uploads") / carrier3
    if uploads_carrier3.exists():
        import shutil
        shutil.copy2(uploads_carrier3, "carrier_with_multiple_layers.mp4")
        
        carrier4 = embed_content("carrier_with_multiple_layers.mp4", content_file="test_data.bin")
        if carrier4:
            print(f"✅ Step 4 completed: {carrier4}")
            return True
        else:
            print("❌ Step 4 failed")
            return False
    else:
        print(f"❌ Cannot find output file for step 4: {uploads_carrier3}")
        return False

def main():
    print("🔧 MIXED CONTENT TYPE EMBEDDING TEST")
    print("Testing the fix for NoneType errors when embedding different file types")
    print()
    
    # Check server health
    try:
        health = requests.get(f"{SERVER_URL}/api/health")
        if health.status_code != 200:
            print("❌ Server not healthy")
            return
        print("✅ Server is healthy")
    except:
        print("❌ Server not responding")
        return
    
    # Create test files
    if not create_test_files():
        return
    
    # Run the test
    success = test_mixed_content_embedding()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! MIXED CONTENT TYPE EMBEDDING WORKS!")
        print("✅ Can hide files, then text, then files again")
        print("✅ No NoneType errors encountered")
        print("✅ Layered container system handles mixed content types correctly")
        print("✅ The fix is working properly!")
    else:
        print("❌ FAILED! NoneType error or embedding issues still exist")
        print("🔍 Check server logs for detailed error information")

if __name__ == "__main__":
    main()
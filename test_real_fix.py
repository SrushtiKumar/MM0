#!/usr/bin/env python3
"""
Test the fixed layered container system with real scenario
"""

import requests
import time
import json
import os
import zipfile
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8001"  # Using port 8001
TEST_PASSWORD = "testpass123"

def wait_for_operation(operation_id, max_wait=30):
    """Wait for an operation to complete"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/api/operations/{operation_id}/status")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   Status: {status_data['status']} - {status_data.get('message', '')}")
                if status_data["status"] == "completed":
                    return status_data
                elif status_data["status"] == "failed":
                    raise Exception(f"Operation failed: {status_data.get('error', 'Unknown error')}")
        except requests.exceptions.ConnectionError:
            print("   Server not running - starting it...")
            return None
        time.sleep(2)
    raise Exception("Operation timed out")

def test_sequential_embedding():
    """Test the exact user scenario that was broken"""
    print("🧪 TESTING SEQUENTIAL EMBEDDING FIX")
    print("="*50)
    
    # Create test files
    print("1. Creating test files...")
    
    # Document 1
    doc1_content = "FIRST DOCUMENT\n\nThis is the original content that was getting overwritten.\nIMPORTANT: This must be preserved!"
    with open("doc1.txt", "w") as f:
        f.write(doc1_content)
    
    # Document 2  
    doc2_content = "SECOND DOCUMENT\n\nThis is the additional content that was causing corruption.\nThis should NOT overwrite the first document!"
    with open("doc2.txt", "w") as f:
        f.write(doc2_content)
    
    # Simple test image (1x1 PNG)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    with open("test_image.png", "wb") as f:
        f.write(png_data)
    
    print(f"   ✅ Created doc1.txt ({len(doc1_content)} chars)")
    print(f"   ✅ Created doc2.txt ({len(doc2_content)} chars)")
    print(f"   ✅ Created test_image.png")
    
    try:
        # Step 1: First embedding
        print(f"\n2. FIRST EMBEDDING - Hiding doc1.txt in test_image.png")
        
        with open("test_image.png", "rb") as carrier, open("doc1.txt", "rb") as content:
            files = {
                "carrier_file": ("test_image.png", carrier, "image/png"),
                "content_file": ("doc1.txt", content, "text/plain")
            }
            data = {
                "content_type": "file",
                "password": TEST_PASSWORD,
                "encryption_type": "basic"
            }
            
            response = requests.post(f"{BASE_URL}/api/embed", files=files, data=data)
        
        if response.status_code != 200:
            print(f"   ❌ First embedding request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        first_result = response.json()
        first_op_id = first_result["operation_id"]
        print(f"   Operation ID: {first_op_id}")
        
        # Wait for completion
        first_status = wait_for_operation(first_op_id)
        if not first_status:
            print("   ❌ Server not responding")
            return False
            
        first_output = first_status["result"]["output_file"]
        print(f"   ✅ First embedding completed: {Path(first_output).name}")
        
        # Step 2: Second embedding (the critical test!)
        print(f"\n3. SECOND EMBEDDING - Hiding doc2.txt in SAME FILE (this used to cause corruption)")
        
        with open(first_output, "rb") as carrier, open("doc2.txt", "rb") as content:
            files = {
                "carrier_file": (Path(first_output).name, carrier, "image/png"),
                "content_file": ("doc2.txt", content, "text/plain")
            }
            data = {
                "content_type": "file",
                "password": TEST_PASSWORD,  # SAME PASSWORD!
                "encryption_type": "basic"
            }
            
            response = requests.post(f"{BASE_URL}/api/embed", files=files, data=data)
        
        if response.status_code != 200:
            print(f"   ❌ Second embedding request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        second_result = response.json()
        second_op_id = second_result["operation_id"]
        print(f"   Operation ID: {second_op_id}")
        
        # Wait for completion
        second_status = wait_for_operation(second_op_id)
        if not second_status:
            print("   ❌ Server not responding")
            return False
            
        final_output = second_status["result"]["output_file"]
        print(f"   ✅ Second embedding completed: {Path(final_output).name}")
        
        # Step 3: Extract and verify
        print(f"\n4. EXTRACTION - This is where corruption was happening")
        
        with open(final_output, "rb") as stego_file:
            files = {
                "stego_file": (Path(final_output).name, stego_file, "image/png")
            }
            data = {
                "password": TEST_PASSWORD,
                "output_format": "auto"
            }
            
            response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
        
        if response.status_code != 200:
            print(f"   ❌ Extraction request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        extract_result = response.json()
        extract_op_id = extract_result["operation_id"]
        print(f"   Operation ID: {extract_op_id}")
        
        # Wait for extraction
        extract_status = wait_for_operation(extract_op_id)
        if not extract_status:
            print("   ❌ Server not responding")
            return False
            
        extracted_file = extract_status["result"]["output_file"]
        extracted_filename = extract_status["result"]["filename"]
        print(f"   ✅ Extraction completed: {extracted_filename}")
        
        # Step 4: Verify results
        print(f"\n5. VERIFICATION")
        
        success = False
        
        if extracted_filename.endswith('.zip'):
            print(f"   📦 Extracted a ZIP file - GOOD! This means layered container worked")
            
            # Extract ZIP and check contents
            with zipfile.ZipFile(extracted_file, 'r') as zip_ref:
                files_in_zip = zip_ref.namelist()
                print(f"   📁 Files in ZIP: {files_in_zip}")
                
                # Extract to temp directory
                zip_ref.extractall("temp_extracted")
                
                # Check contents
                found_docs = []
                for file in files_in_zip:
                    file_path = Path("temp_extracted") / file
                    with open(file_path, 'r') as f:
                        content = f.read()
                        print(f"   📄 {file}: {content[:50]}...")
                        
                        if "FIRST DOCUMENT" in content:
                            found_docs.append("First")
                        elif "SECOND DOCUMENT" in content:
                            found_docs.append("Second")
                
                if "First" in found_docs and "Second" in found_docs:
                    print(f"   ✅ BOTH documents found and preserved!")
                    success = True
                else:
                    print(f"   ❌ Missing documents. Found: {found_docs}")
            
            # Cleanup extracted files
            import shutil
            if Path("temp_extracted").exists():
                shutil.rmtree("temp_extracted")
                
        else:
            print(f"   ❌ Extracted a single file ({extracted_filename}) - this indicates the fix didn't work")
            
            # Check what was extracted
            with open(extracted_file, 'r') as f:
                content = f.read()
                print(f"   📄 Extracted content: {content[:100]}...")
                
                if "FIRST DOCUMENT" in content and "SECOND DOCUMENT" in content:
                    print(f"   🤔 Both documents in one file - possible but not ideal")
                elif "FIRST DOCUMENT" in content:
                    print(f"   ❌ Only first document found - second was lost!")
                elif "SECOND DOCUMENT" in content:
                    print(f"   ❌ Only second document found - first was overwritten!")
                else:
                    print(f"   ❌ Neither document found clearly - corruption occurred!")
        
        # Cleanup
        cleanup_files = ["doc1.txt", "doc2.txt", "test_image.png"]
        for file in cleanup_files:
            if Path(file).exists():
                os.remove(file)
        
        return success
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TESTING DATA CORRUPTION VULNERABILITY FIX")
    print("This test simulates the exact user scenario that was broken\n")
    
    success = test_sequential_embedding()
    
    print(f"\n" + "="*50)
    print("FINAL RESULT")
    print("="*50)
    
    if success:
        print("✅ SUCCESS: Data corruption vulnerability has been FIXED!")
        print("   Both documents were preserved in separate layers")
        print("   No data loss occurred during sequential embedding")
    else:
        print("❌ FAILURE: Data corruption vulnerability still exists!")
        print("   The fix needs more work")
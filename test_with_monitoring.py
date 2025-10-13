#!/usr/bin/env python3
"""
Simple test with status monitoring to see the layered container messages
"""

import requests
import time
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8001"
TEST_PASSWORD = "testpass123"

def monitor_operation(operation_id):
    """Monitor an operation and print all status updates"""
    print(f"Monitoring operation {operation_id}...")
    
    for attempt in range(30):  # 30 seconds max
        try:
            response = requests.get(f"{BASE_URL}/api/operations/{operation_id}/status")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                message = status_data.get("message", "")
                
                print(f"  [{progress}%] {status}: {message}")
                
                if status == "completed":
                    return status_data
                elif status == "failed":
                    print(f"  ERROR: {status_data.get('error', 'Unknown error')}")
                    return None
                    
        except Exception as e:
            print(f"  Monitor error: {e}")
            
        time.sleep(1)
    
    print("  Operation timed out")
    return None

def test_sequential_with_monitoring():
    """Test sequential embedding with detailed monitoring"""
    print("🧪 TESTING WITH STATUS MONITORING")
    print("="*50)
    
    # Create test files
    doc1 = "First document content - should be preserved"
    doc2 = "Second document content - should not overwrite first"
    
    with open("doc1.txt", "w") as f:
        f.write(doc1)
    with open("doc2.txt", "w") as f:
        f.write(doc2)
    
    # Create test image using PIL if available
    try:
        from PIL import Image
        import numpy as np
        img = Image.fromarray(np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8))
        img.save("test.png")
        print("✅ Created 100x100 test image")
    except:
        # Fallback to existing image if PIL not available
        from test_direct_logic_fixed import *  # This has the manual PNG creation
        print("✅ Using fallback test image")
    
    try:
        # First embedding
        print("\n1. FIRST EMBEDDING")
        with open("test.png", "rb") as carrier, open("doc1.txt", "rb") as content:
            files = {
                "carrier_file": ("test.png", carrier, "image/png"),
                "content_file": ("doc1.txt", content, "text/plain")
            }
            data = {
                "content_type": "file",
                "password": TEST_PASSWORD,
                "encryption_type": "basic"
            }
            
            response = requests.post(f"{BASE_URL}/api/embed", files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ First embed failed: {response.text}")
            return False
        
        first_result = response.json()
        first_op_id = first_result["operation_id"]
        
        first_status = monitor_operation(first_op_id)
        if not first_status:
            return False
        
        first_output = first_status["result"]["output_file"]
        print(f"✅ First embedding completed: {Path(first_output).name}")
        
        # Second embedding
        print(f"\n2. SECOND EMBEDDING (this should trigger layered container)")
        with open(first_output, "rb") as carrier, open("doc2.txt", "rb") as content:
            files = {
                "carrier_file": (Path(first_output).name, carrier, "image/png"),
                "content_file": ("doc2.txt", content, "text/plain")
            }
            data = {
                "content_type": "file",
                "password": TEST_PASSWORD,  # Same password!
                "encryption_type": "basic"
            }
            
            response = requests.post(f"{BASE_URL}/api/embed", files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Second embed failed: {response.text}")
            return False
        
        second_result = response.json()
        second_op_id = second_result["operation_id"]
        
        second_status = monitor_operation(second_op_id)
        if not second_status:
            return False
        
        second_output = second_status["result"]["output_file"]
        print(f"✅ Second embedding completed: {Path(second_output).name}")
        
        # Extraction
        print(f"\n3. EXTRACTION")
        with open(second_output, "rb") as stego_file:
            files = {
                "stego_file": (Path(second_output).name, stego_file, "image/png")
            }
            data = {
                "password": TEST_PASSWORD,
                "output_format": "auto"
            }
            
            response = requests.post(f"{BASE_URL}/api/extract", files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Extract failed: {response.text}")
            return False
        
        extract_result = response.json()
        extract_op_id = extract_result["operation_id"]
        
        extract_status = monitor_operation(extract_op_id)
        if not extract_status:
            return False
        
        extracted_file = extract_status["result"]["output_file"]
        extracted_filename = extract_status["result"]["filename"]
        print(f"✅ Extraction completed: {extracted_filename}")
        
        # Check result
        if extracted_filename.endswith('.zip'):
            print(f"🎉 SUCCESS: Got ZIP file - layered container worked!")
            return True
        else:
            print(f"❌ FAILURE: Got single file - layered container didn't work")
            with open(extracted_file, 'r') as f:
                content = f.read()
                print(f"Content: {content[:100]}...")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    finally:
        # Cleanup
        for file in ["doc1.txt", "doc2.txt", "test.png"]:
            if Path(file).exists():
                os.remove(file)

if __name__ == "__main__":
    success = test_sequential_with_monitoring()
    
    print(f"\n" + "="*50)
    if success:
        print("✅ SUCCESS: Layered container system working!")
    else:
        print("❌ FAILURE: Need to debug further")
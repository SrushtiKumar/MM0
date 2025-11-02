#!/usr/bin/env python3
"""
Complete end-to-end test: Embed, Download, Verify, and Extract
"""

import requests
from PIL import Image
import numpy as np
import os
import time

def test_complete_workflow():
    print("🧪 Complete Image Steganography Workflow Test")
    print("=" * 60)
    
    # Create test PNG
    print("1️⃣ Creating test PNG...")
    img = Image.fromarray(np.random.randint(0, 255, (150, 150, 3), dtype='uint8'), 'RGB')
    img.save('carrier_test.png', 'PNG')
    print("✅ Test PNG created")

    # Create test text  
    print("2️⃣ Creating secret document...")
    secret_content = "This is my SECRET document!\nIt contains confidential information.\nLine 3 of secret data."
    with open('secret_test.txt', 'w') as f:
        f.write(secret_content)
    print("✅ Secret document created")

    try:
        # Step 1: Embed via API
        print("\n3️⃣ Embedding secret in image via API...")
        with open('carrier_test.png', 'rb') as pf, open('secret_test.txt', 'rb') as tf:
            embed_response = requests.post('http://localhost:8000/api/embed', 
                files={
                    'carrier_file': pf, 
                    'content_file': tf
                },
                data={
                    'content_type': 'document',
                    'password': 'test123'
                })
        
        if embed_response.status_code != 200:
            print(f"❌ Embedding failed: {embed_response.text}")
            return False
            
        embed_data = embed_response.json()
        operation_id = embed_data.get('operation_id')
        print(f"✅ Embedding started - Operation ID: {operation_id}")
        
        # Wait for processing
        time.sleep(3)
        
        # Step 2: Download processed image
        print("\n4️⃣ Downloading processed steganographic image...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.text}")
            return False
            
        with open('stego_image.png', 'wb') as f:
            f.write(download_response.content)
        print("✅ Steganographic image downloaded")
        
        # Step 3: Verify image integrity
        print("\n5️⃣ Verifying image can be opened normally...")
        try:
            stego_img = Image.open('stego_image.png')
            print(f"✅ SUCCESS: Image opens perfectly! Size: {stego_img.size}, Mode: {stego_img.mode}")
            
            # Save a copy to verify it's truly valid
            stego_img.save('verified_copy.png', 'PNG')
            print("✅ Image can be re-saved - format is completely valid!")
            
        except Exception as e:
            print(f"❌ Image is corrupted: {e}")
            return False
        
        # Step 4: Extract hidden data
        print("\n6️⃣ Extracting hidden data from steganographic image...")
        with open('stego_image.png', 'rb') as f:
            extract_response = requests.post('http://localhost:8000/api/extract',
                files={'stego_file': f},
                data={'password': 'test123'})
                
        if extract_response.status_code != 200:
            print(f"❌ Extraction failed: {extract_response.text}")
            return False
            
        extract_data = extract_response.json()
        extract_operation_id = extract_data.get('operation_id')
        print(f"✅ Extraction started - Operation ID: {extract_operation_id}")
        
        # Wait for extraction (longer time needed)
        print("⏳ Waiting for extraction to complete...")
        time.sleep(5)
        
        # Check operation status first
        status_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/status')
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"📊 Extraction status: {status_data}")
        
        # Download extracted file
        print("\n7️⃣ Downloading extracted secret file...")
        extract_download = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/download')
        
        if extract_download.status_code != 200:
            print(f"❌ Extract download failed: {extract_download.text}")
            return False
            
        with open('extracted_secret.txt', 'wb') as f:
            f.write(extract_download.content)
        print("✅ Secret file extracted")
        
        # Step 5: Verify extracted content
        print("\n8️⃣ Verifying extracted content matches original...")
        with open('extracted_secret.txt', 'r') as f:
            extracted_content = f.read()
            
        if secret_content in extracted_content:
            print("✅ SUCCESS: Extracted content matches original!")
            print(f"📝 Original: {repr(secret_content[:50])}...")
            print(f"📤 Extracted: {repr(extracted_content[:50])}...")
        else:
            print("❌ Extracted content doesn't match original")
            print(f"📝 Original: {repr(secret_content)}")
            print(f"📤 Extracted: {repr(extracted_content)}")
            return False
        
        print("\n🎉 COMPLETE SUCCESS!")
        print("✅ Image steganography corruption is FULLY RESOLVED!")
        print("✅ Processed images are readable AND carry hidden data!")
        print("✅ Full workflow: Embed → Download → Open → Extract → Verify ✓")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up test files...")
        for f in ['carrier_test.png', 'secret_test.txt', 'stego_image.png', 'verified_copy.png', 'extracted_secret.txt']:
            try: 
                os.remove(f)
            except: 
                pass

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n🎯 RESOLUTION CONFIRMED: Image steganography corruption completely FIXED!")
    else:
        print("\n❌ Issues remain")
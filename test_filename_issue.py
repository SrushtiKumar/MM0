#!/usr/bin/env python3
"""
Test to demonstrate and fix the filename issue
"""

import requests
import tempfile
import os
from PIL import Image
import time

def test_filename_preservation():
    """Test that extracted files preserve their original filename"""
    print("🔍 FILENAME PRESERVATION TEST")
    print("=" * 50)
    
    try:
        # Create test files with specific names
        carrier_img = Image.new('RGB', (100, 100), color='blue')
        carrier_path = "test_carrier.png"
        carrier_img.save(carrier_path, 'PNG')
        
        secret_img = Image.new('RGB', (50, 50), color='red')
        secret_path = "my_secret_image.jpg"  # Clear, specific name
        secret_img.save(secret_path, 'JPEG')
        
        print(f"✅ Created files:")
        print(f"   Carrier: {carrier_path}")
        print(f"   Secret: {secret_path}")
        
        # Step 1: Embed via API
        print("\n📤 Step 1: Embedding via API...")
        with open(carrier_path, 'rb') as carrier_file:
            with open(secret_path, 'rb') as secret_file:
                files = {
                    'carrier_file': ('test_carrier.png', carrier_file, 'image/png'),
                    'content_file': ('my_secret_image.jpg', secret_file, 'image/jpeg')  # Specific filename
                }
                data = {
                    'carrier_type': 'image',
                    'content_type': 'file',
                    'password': 'test123'
                }
                
                response = requests.post('http://localhost:8000/api/embed', files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Embed failed: {response.status_code} - {response.text}")
            return False
            
        embed_result = response.json()
        operation_id = embed_result['operation_id']
        print(f"✅ Embed operation started: {operation_id}")
        
        # Step 2: Wait for completion
        print("⏳ Step 2: Waiting for embedding completion...")
        for i in range(10):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            
            if status_data.get('status') == 'completed':
                print("✅ Embedding completed successfully!")
                break
            elif status_data.get('status') == 'failed':
                print(f"❌ Embedding failed: {status_data.get('error')}")
                return False
            time.sleep(0.5)
        
        # Step 3: Download stego file
        print("📥 Step 3: Downloading stego file...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        stego_path = "output_stego.png"
        with open(stego_path, 'wb') as f:
            f.write(download_response.content)
        print(f"✅ Stego file downloaded: {len(download_response.content)} bytes")
        
        # Step 4: Extract via API
        print("\n🔓 Step 4: Extracting via API...")
        with open(stego_path, 'rb') as stego_file:
            files = {'stego_file': ('output_stego.png', stego_file, 'image/png')}
            data = {'carrier_type': 'image', 'password': 'test123'}
            
            extract_response = requests.post('http://localhost:8000/api/extract', files=files, data=data)
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.status_code} - {extract_response.text}")
            return False
            
        extract_result = extract_response.json()
        extract_operation_id = extract_result['operation_id']
        print(f"✅ Extract operation started: {extract_operation_id}")
        print("📊 Server logs should show debug information now...")
        
        # Step 5: Wait for extraction completion
        print("⏳ Step 5: Waiting for extraction completion...")
        final_result = None
        for i in range(10):
            extract_status_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/status')
            extract_status_data = extract_status_response.json()
            
            if extract_status_data.get('status') == 'completed':
                print("✅ Extraction completed!")
                final_result = extract_status_data.get('result', {})
                break
            elif extract_status_data.get('status') == 'failed':
                print(f"❌ Extraction failed: {extract_status_data.get('error')}")
                return False
            time.sleep(0.5)
        
        # Step 6: Analyze results
        print("\n📊 ANALYSIS:")
        print(f"   Expected filename: my_secret_image.jpg")
        print(f"   Actual filename: {final_result.get('filename', 'N/A')}")
        print(f"   Original filename field: {final_result.get('original_filename', 'N/A')}")
        print(f"   Data type: {final_result.get('data_type', 'N/A')}")
        print(f"   File size: {final_result.get('file_size', 'N/A')}")
        
        # Step 7: Download and verify extracted file
        print("\n📤 Step 6: Downloading extracted file...")
        extracted_download_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/download')
        
        extracted_filename = final_result.get('filename', 'extracted_file.bin')
        with open(extracted_filename, 'wb') as f:
            f.write(extracted_download_response.content)
        
        print(f"✅ Downloaded: {extracted_filename}")
        
        # Verify it's a valid JPEG
        with open(extracted_filename, 'rb') as f:
            first_bytes = f.read(10)
        
        print(f"   First 10 bytes: {first_bytes.hex()}")
        is_jpeg = first_bytes.startswith(b'\xff\xd8\xff\xe0') and b'JFIF' in first_bytes
        print(f"   Is valid JPEG: {is_jpeg}")
        
        if is_jpeg:
            try:
                with Image.open(extracted_filename) as img:
                    print(f"   ✅ Image successfully opened: {img.size} {img.mode}")
            except Exception as e:
                print(f"   ❌ Could not open as image: {e}")
        
        # Final verdict
        filename_correct = final_result.get('filename', '').endswith('.jpg')
        content_correct = is_jpeg
        
        print(f"\n🎯 RESULTS:")
        print(f"   Filename preservation: {'✅ PASS' if filename_correct else '❌ FAIL'}")
        print(f"   Content preservation: {'✅ PASS' if content_correct else '❌ FAIL'}")
        print(f"   Overall: {'✅ SUCCESS' if (filename_correct and content_correct) else '❌ NEEDS FIX'}")
        
        # Cleanup
        for f in [carrier_path, secret_path, stego_path, extracted_filename]:
            if os.path.exists(f):
                os.remove(f)
        
        return filename_correct and content_correct
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_filename_preservation()
    exit(0 if success else 1)
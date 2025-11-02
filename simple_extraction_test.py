#!/usr/bin/env python3
"""
Simple focused test for extraction issue
"""

import requests
import tempfile
import os
from PIL import Image
import time

def create_test_files():
    """Create simple test files"""
    # Create a PNG carrier
    img = Image.new('RGB', (100, 100), color='blue')
    carrier_path = "simple_carrier.png"
    img.save(carrier_path, 'PNG')
    
    # Create a JPG secret
    secret_img = Image.new('RGB', (50, 50), color='red')
    secret_path = "simple_secret.jpg"
    secret_img.save(secret_path, 'JPEG')
    
    return carrier_path, secret_path

def test_simple_api_workflow():
    """Test a simple API workflow with detailed logging"""
    print("🧪 SIMPLE API EXTRACTION TEST")
    print("=" * 40)
    
    try:
        # Create test files
        carrier_path, secret_path = create_test_files()
        
        # 1. Embed
        print("📤 Step 1: Embedding...")
        with open(carrier_path, 'rb') as carrier_file:
            with open(secret_path, 'rb') as secret_file:
                files = {
                    'carrier_file': ('carrier.png', carrier_file, 'image/png'),
                    'content_file': ('secret.jpg', secret_file, 'image/jpeg')
                }
                data = {
                    'carrier_type': 'image',
                    'content_type': 'file',
                    'password': 'test123'
                }
                
                response = requests.post('http://localhost:8000/api/embed', 
                                       files=files, data=data)
                
        if response.status_code != 200:
            print(f"❌ Embed failed: {response.status_code}")
            return
            
        embed_result = response.json()
        operation_id = embed_result['operation_id']
        print(f"✅ Embed started: {operation_id}")
        
        # 2. Wait for embedding to complete
        print("⏳ Step 2: Waiting for embedding...")
        for i in range(10):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            
            print(f"   Status response: {status_data}")
            
            if status_data.get('status') == 'completed':
                print("✅ Embedding completed!")
                break
            elif status_data.get('status') == 'failed':
                print(f"❌ Embedding failed: {status_data.get('error', 'Unknown error')}")
                return
            time.sleep(1)
        
        # 3. Download stego file
        print("📥 Step 3: Downloading stego file...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return
            
        stego_path = "test_stego.png"
        with open(stego_path, 'wb') as f:
            f.write(download_response.content)
        print(f"✅ Stego file saved: {len(download_response.content)} bytes")
        
        # 4. Extract
        print("🔓 Step 4: Extracting...")
        with open(stego_path, 'rb') as stego_file:
            files = {'stego_file': ('stego.png', stego_file, 'image/png')}
            data = {
                'carrier_type': 'image',
                'password': 'test123'
            }
            
            extract_response = requests.post('http://localhost:8000/api/extract',
                                           files=files, data=data)
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.status_code}")
            return
            
        extract_result = extract_response.json()
        extract_operation_id = extract_result['operation_id']
        print(f"✅ Extract started: {extract_operation_id}")
        
        # 5. Wait for extraction to complete
        print("⏳ Step 5: Waiting for extraction...")
        for i in range(10):
            extract_status_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/status')
            extract_status_data = extract_status_response.json()
            
            print(f"   Status check {i+1}: {extract_status_data.get('status', 'N/A')}")
            
            if extract_status_data['status'] == 'completed':
                print("✅ Extraction completed!")
                print(f"   Result details:")
                result = extract_status_data.get('result', {})
                print(f"     - Filename: {result.get('filename', 'N/A')}")
                print(f"     - Data type: {result.get('data_type', 'N/A')}")
                print(f"     - File size: {result.get('file_size', 'N/A')}")
                print(f"     - Original filename: {result.get('original_filename', 'N/A')}")
                if result.get('preview'):
                    print(f"     - Preview: {result['preview'][:100]}...")
                break
            elif extract_status_data['status'] == 'failed':
                print(f"❌ Extraction failed: {extract_status_data.get('error', 'Unknown error')}")
                return
            time.sleep(1)
        
        # 6. Download extracted file
        print("📤 Step 6: Downloading extracted file...")
        extracted_download_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/download')
        
        if extracted_download_response.status_code != 200:
            print(f"❌ Extract download failed: {extracted_download_response.status_code}")
            return
            
        extracted_filename = result.get('filename', 'extracted_file.bin')
        with open(extracted_filename, 'wb') as f:
            f.write(extracted_download_response.content)
        print(f"✅ Extracted file saved: {extracted_filename} ({len(extracted_download_response.content)} bytes)")
        
        # 7. Check if extracted file is valid
        print("🔍 Step 7: Validating extracted file...")
        print(f"   Content-Type: {extracted_download_response.headers.get('content-type', 'N/A')}")
        
        # Check first few bytes
        with open(extracted_filename, 'rb') as f:
            first_bytes = f.read(20)
        print(f"   First 20 bytes (hex): {first_bytes.hex()}")
        print(f"   First 20 bytes (repr): {repr(first_bytes)}")
        
        # Try to open as image if it should be an image
        if extracted_filename.endswith(('.jpg', '.jpeg', '.png')):
            try:
                with Image.open(extracted_filename) as img:
                    print(f"   ✅ Valid image: {img.size} {img.mode}")
            except Exception as e:
                print(f"   ❌ Invalid image: {e}")
        
        # Cleanup
        for f in [carrier_path, secret_path, stego_path, extracted_filename]:
            if os.path.exists(f):
                os.remove(f)
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_api_workflow()
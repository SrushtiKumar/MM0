#!/usr/bin/env python3
"""
Simple test to capture server debug output
"""

import requests
import tempfile
import os
from PIL import Image
import time
import subprocess
import threading

def capture_server_logs():
    """Capture server output while running test"""
    print("🔍 SIMPLE API TEST WITH LOG CAPTURE")
    print("=" * 50)
    
    try:
        # Create test files
        carrier_img = Image.new('RGB', (100, 100), color='blue')
        carrier_path = "simple_carrier.png"
        carrier_img.save(carrier_path, 'PNG')
        
        secret_img = Image.new('RGB', (50, 50), color='red')
        secret_path = "simple_secret.jpg"
        secret_img.save(secret_path, 'JPEG')
        
        print(f"✅ Created test files:")
        print(f"   Carrier: {carrier_path}")
        print(f"   Secret: {secret_path}")
        
        # Embed via API
        print(f"\n📤 Step 1: Embedding...")
        with open(carrier_path, 'rb') as carrier_file:
            with open(secret_path, 'rb') as secret_file:
                files = {
                    'carrier_file': ('simple_carrier.png', carrier_file, 'image/png'),
                    'content_file': ('simple_secret.jpg', secret_file, 'image/jpeg')
                }
                data = {
                    'carrier_type': 'image',
                    'content_type': 'file',
                    'password': 'test123'
                }
                
                response = requests.post('http://localhost:8000/api/embed', files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Embed failed: {response.status_code}")
            return
            
        embed_result = response.json()
        operation_id = embed_result['operation_id']
        print(f"✅ Embed started: {operation_id}")
        
        # Wait for embedding
        print(f"⏳ Step 2: Waiting for embedding...")
        for i in range(10):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            
            if status_data.get('status') == 'completed':
                print("✅ Embedding completed!")
                break
            time.sleep(0.5)
        
        # Download stego file
        print(f"📥 Step 3: Downloading stego file...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        stego_path = "api_stego.png"
        with open(stego_path, 'wb') as f:
            f.write(download_response.content)
        print(f"✅ Stego file saved: {len(download_response.content)} bytes")
        
        # Extract via API
        print(f"\n🔓 Step 4: Extracting...")
        print(f"   >>> Server should show debug messages now <<<")
        
        with open(stego_path, 'rb') as stego_file:
            files = {'stego_file': ('api_stego.png', stego_file, 'image/png')}
            data = {'carrier_type': 'image', 'password': 'test123'}
            
            extract_response = requests.post('http://localhost:8000/api/extract', files=files, data=data)
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.status_code}")
            return
            
        extract_result = extract_response.json()
        extract_operation_id = extract_result['operation_id']
        print(f"✅ Extract started: {extract_operation_id}")
        
        # Wait for extraction
        print(f"⏳ Step 5: Waiting for extraction...")
        final_result = None
        for i in range(10):
            extract_status_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/status')
            extract_status_data = extract_status_response.json()
            
            if extract_status_data.get('status') == 'completed':
                print("✅ Extraction completed!")
                final_result = extract_status_data.get('result', {})
                break
            time.sleep(0.5)
        
        print(f"\n📊 RESULTS:")
        print(f"   Filename: {final_result.get('filename', 'N/A')}")
        print(f"   Original filename: {final_result.get('original_filename', 'N/A')}")
        print(f"   Data type: {final_result.get('data_type', 'N/A')}")
        
        # Cleanup
        for f in [carrier_path, secret_path, stego_path]:
            if os.path.exists(f):
                os.remove(f)
        
        return final_result.get('filename', '').endswith('.jpg')
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = capture_server_logs()
    print(f"\n🎯 Filename fixed: {'✅ YES' if success else '❌ NO'}")
    exit(0 if success else 1)
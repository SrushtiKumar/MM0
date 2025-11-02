#!/usr/bin/env python3
"""
Test image and document steganography filename preservation
"""

import requests
import time
import os
from pathlib import Path

def test_image_steganography():
    """Test Python file in image"""
    
    print("🖼️ Testing Python File in Image Steganography")
    print("=" * 50)
    
    # Create test Python file
    with open('test_image_py.py', 'w') as f:
        f.write('print("Hello from image steganography!")')
    
    print(f"📂 Created test file: test_image_py.py ({os.path.getsize('test_image_py.py')} bytes)")
    
    # Test with image
    image_file = "debug_embedded.png"
    if not Path(image_file).exists():
        print(f"❌ Image file not found: {image_file}")
        return
    
    # Embed
    with open(image_file, 'rb') as img_f, open('test_image_py.py', 'rb') as py_f:
        data = {
            'password': 'test123',
            'content_type': 'file',
            'carrier_type': 'image'
        }
        files = {
            'carrier_file': (image_file, img_f),
            'content_file': ('test_image_py.py', py_f)
        }
        
        print("🔐 Sending embed request...")
        response = requests.post("http://localhost:8000/api/embed", data=data, files=files)
        print(f"📡 Embed response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            op_id = result['operation_id']
            print(f"✅ Operation started: {op_id}")
            
            # Wait for completion
            for i in range(30):
                time.sleep(1)
                status_resp = requests.get(f"http://localhost:8000/api/operations/{op_id}/status")
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    status = status_data['status']
                    print(f"📊 Status: {status}")
                    
                    if status == 'completed':
                        print("✅ Embedding completed!")
                        test_image_extraction(op_id)
                        break
                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown')
                        print(f"❌ Embedding failed: {error}")
                        break
            else:
                print("❌ Timeout")
        else:
            print(f"❌ Embed failed: {response.text}")
    
    # Cleanup
    os.unlink('test_image_py.py')

def test_image_extraction(embed_op_id):
    """Test extraction from image"""
    
    print("\n🔓 Testing Image Extraction")
    
    # Download stego image
    download_resp = requests.get(f"http://localhost:8000/api/operations/{embed_op_id}/download")
    if download_resp.status_code == 200:
        with open('test_stego.png', 'wb') as f:
            f.write(download_resp.content)
        print(f"💾 Downloaded stego image ({len(download_resp.content)} bytes)")
        
        # Extract
        with open('test_stego.png', 'rb') as stego_f:
            data = {'password': 'test123'}
            files = {'stego_file': ('test_stego.png', stego_f)}
            
            response = requests.post("http://localhost:8000/api/extract", data=data, files=files)
            print(f"📡 Extract response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                extract_op_id = result['operation_id']
                print(f"✅ Extract operation: {extract_op_id}")
                
                # Wait for extraction
                for i in range(30):
                    time.sleep(1)
                    status_resp = requests.get(f"http://localhost:8000/api/operations/{extract_op_id}/status")
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        status = status_data['status']
                        print(f"📊 Extract Status: {status}")
                        
                        if status == 'completed':
                            print("✅ Extraction completed!")
                            
                            # Check filename
                            extract_download = requests.get(f"http://localhost:8000/api/operations/{extract_op_id}/download")
                            if extract_download.status_code == 200:
                                content_disp = extract_download.headers.get('Content-Disposition', '')
                                print(f"📋 Content-Disposition: {content_disp}")
                                
                                import re
                                filename_match = re.search(r'filename="([^"]+)"', content_disp)
                                if filename_match:
                                    filename = filename_match.group(1)
                                    print(f"📂 Extracted filename: {filename}")
                                    
                                    if filename.endswith('.py'):
                                        print("🎉 SUCCESS: Image steganography preserved .py extension!")
                                    else:
                                        print(f"❌ FAILED: Expected .py, got {Path(filename).suffix}")
                                else:
                                    print("❌ No filename found")
                            break
                        elif status == 'failed':
                            error = status_data.get('error', 'Unknown')
                            print(f"❌ Extraction failed: {error}")
                            break
                else:
                    print("❌ Extraction timeout")
            else:
                print(f"❌ Extract request failed: {response.text}")
        
        os.unlink('test_stego.png')

if __name__ == "__main__":
    test_image_steganography()
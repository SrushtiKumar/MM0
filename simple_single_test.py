#!/usr/bin/env python3
"""
Simple single test to verify the main fixes work
"""

import requests
import time
import os

def test_video_python():
    """Simple test of Python file in video"""
    
    print("🎯 Testing Python File in Video")
    
    # Create simple Python file
    with open('simple_test.py', 'w') as f:
        f.write('print("Hello World!")')
    
    print(f"📂 Created simple_test.py ({os.path.getsize('simple_test.py')} bytes)")
    
    # Embed in video
    with open('clean_carrier.mp4', 'rb') as video_f, open('simple_test.py', 'rb') as py_f:
        data = {
            'password': 'test123',
            'content_type': 'file',
            'carrier_type': 'video'
        }
        files = {
            'carrier_file': ('clean_carrier.mp4', video_f),
            'content_file': ('simple_test.py', py_f)
        }
        
        print("🔐 Sending embed request...")
        response = requests.post("http://localhost:8000/api/embed", data=data, files=files)
        print(f"📡 Embed response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            op_id = result['operation_id']
            print(f"✅ Operation started: {op_id}")
            
            # Check status
            for i in range(30):
                time.sleep(1)
                status_resp = requests.get(f"http://localhost:8000/api/operations/{op_id}/status")
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    status = status_data['status']
                    print(f"📊 Status: {status}")
                    
                    if status == 'completed':
                        print("✅ Embedding completed successfully!")
                        
                        # Try extraction
                        test_extraction(op_id)
                        break
                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown')
                        print(f"❌ Embedding failed: {error}")
                        break
            else:
                print("❌ Timeout waiting for embedding")
        else:
            print(f"❌ Embed request failed: {response.text}")
    
    # Cleanup
    os.unlink('simple_test.py')

def test_extraction(embed_op_id):
    """Test extracting from the embedded file"""
    
    print("\n🔓 Testing Extraction")
    
    # Download the stego video first
    download_resp = requests.get(f"http://localhost:8000/api/operations/{embed_op_id}/download")
    if download_resp.status_code == 200:
        with open('test_stego.mp4', 'wb') as f:
            f.write(download_resp.content)
        print(f"💾 Downloaded stego video ({len(download_resp.content)} bytes)")
        
        # Extract from it
        with open('test_stego.mp4', 'rb') as stego_f:
            data = {'password': 'test123'}
            files = {'stego_file': ('test_stego.mp4', stego_f)}
            
            response = requests.post("http://localhost:8000/api/extract", data=data, files=files)
            print(f"📡 Extract response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                extract_op_id = result['operation_id'] 
                print(f"✅ Extract operation started: {extract_op_id}")
                
                # Check extraction status
                for i in range(30):
                    time.sleep(1)
                    status_resp = requests.get(f"http://localhost:8000/api/operations/{extract_op_id}/status")
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        status = status_data['status']
                        print(f"📊 Extract Status: {status}")
                        
                        if status == 'completed':
                            print("✅ Extraction completed!")
                            
                            # Download extracted file
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
                                        print("🎉 SUCCESS: .py extension preserved!")
                                    else:
                                        print(f"❌ FAILED: Expected .py, got {filename}")
                                        
                                else:
                                    print("❌ No filename in Content-Disposition")
                            break
                        elif status == 'failed':
                            error = status_data.get('error', 'Unknown')
                            print(f"❌ Extraction failed: {error}")
                            break
                else:
                    print("❌ Timeout waiting for extraction")
            else:
                print(f"❌ Extract request failed: {response.text}")
        
        os.unlink('test_stego.mp4')
    else:
        print(f"❌ Failed to download stego video")

if __name__ == "__main__":
    test_video_python()
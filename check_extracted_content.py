#!/usr/bin/env python3
"""
Check what the extracted content looks like to debug verification
"""

import requests
import tempfile
import os
from PIL import Image
import time

def check_extracted_content():
    """Check what extracted content actually contains"""
    print("🔍 CHECKING EXTRACTED CONTENT")
    print("=" * 40)
    
    # Create test files
    carrier_path = "content_check_carrier.png"
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(carrier_path)
    
    secret_content = "This is the exact secret content we want to extract."
    secret_path = "content_check_secret.txt"
    with open(secret_path, 'w') as f:
        f.write(secret_content)
    
    print(f"✅ Original secret content:")
    print(f"   Length: {len(secret_content)} chars")
    print(f"   Content: {repr(secret_content)}")
    
    try:
        # Embed
        with open(carrier_path, 'rb') as cf, open(secret_path, 'rb') as sf:
            embed_response = requests.post('http://localhost:8000/api/embed',
                files={'carrier_file': cf, 'content_file': sf},
                data={'carrier_type': 'image', 'content_type': 'file', 'password': 'test123'})
        
        embed_data = embed_response.json()
        operation_id = embed_data['operation_id']
        
        # Wait for completion
        for i in range(15):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            if status_data.get('status') == 'completed':
                break
            time.sleep(0.5)
        
        # Download stego
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        stego_path = "content_check_stego.png"
        with open(stego_path, 'wb') as f:
            f.write(download_response.content)
        
        # Extract
        with open(stego_path, 'rb') as pf:
            extract_response = requests.post('http://localhost:8000/api/extract',
                files={'stego_file': pf},
                data={'carrier_type': 'image', 'password': 'test123'})
        
        extract_data = extract_response.json()
        extract_operation_id = extract_data['operation_id']
        
        # Wait for extraction completion
        for i in range(15):
            extract_status_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/status')
            extract_status_data = extract_status_response.json()
            
            if extract_status_data.get('status') == 'completed':
                result = extract_status_data.get('result', {})
                print(f"\n✅ Extraction completed:")
                print(f"   Filename: {result.get('filename', 'N/A')}")
                print(f"   Data type: {result.get('data_type', 'N/A')}")
                print(f"   File size: {result.get('file_size', 'N/A')} bytes")
                break
            time.sleep(0.5)
        
        # Download extracted content
        extract_download = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/download')
        
        print(f"\n📥 Downloaded extracted content:")
        print(f"   Status: {extract_download.status_code}")
        print(f"   Content-Type: {extract_download.headers.get('content-type', 'N/A')}")
        print(f"   Content-Length: {len(extract_download.content)} bytes")
        
        # Try different ways to read the content
        print(f"\n🔍 Content analysis:")
        
        # Raw bytes
        raw_bytes = extract_download.content
        print(f"   Raw bytes length: {len(raw_bytes)}")
        print(f"   First 50 bytes: {raw_bytes[:50]}")
        print(f"   First 50 bytes (hex): {raw_bytes[:50].hex()}")
        
        # Try UTF-8 decode
        try:
            text_content = raw_bytes.decode('utf-8')
            print(f"   UTF-8 decoded length: {len(text_content)} chars")
            print(f"   UTF-8 content: {repr(text_content)}")
            
            # Check if original content is in extracted content
            if secret_content in text_content:
                print(f"   ✅ Original content FOUND in extracted content!")
            else:
                print(f"   ❌ Original content NOT FOUND in extracted content")
                print(f"   Looking for: {repr(secret_content)}")
                
        except UnicodeDecodeError as e:
            print(f"   ❌ UTF-8 decode failed: {e}")
        
        # Try different encodings
        for encoding in ['latin-1', 'ascii']:
            try:
                decoded = raw_bytes.decode(encoding)
                if secret_content in decoded:
                    print(f"   ✅ Content found with {encoding} encoding!")
                    break
            except:
                pass
        
        # Cleanup
        for f in [carrier_path, secret_path, stego_path]:
            if os.path.exists(f):
                os.remove(f)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_extracted_content()
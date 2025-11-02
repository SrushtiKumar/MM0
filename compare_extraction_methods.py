#!/usr/bin/env python3
"""
Compare the working debug test vs comprehensive test to find the difference
"""

import requests
import tempfile
import os
from PIL import Image
import time

def test_debug_style():
    """Test using the same style as our working debug test"""
    print("🔍 DEBUG STYLE TEST (This should work)")
    print("=" * 40)
    
    # Create test files  
    carrier_img = Image.new('RGB', (100, 100), color='blue')
    carrier_path = "debug_carrier.png"
    carrier_img.save(carrier_path, 'PNG')
    
    secret_img = Image.new('RGB', (50, 50), color='red')
    secret_path = "debug_secret.jpg"
    secret_img.save(secret_path, 'JPEG')
    
    try:
        # Embed
        with open(carrier_path, 'rb') as carrier_file:
            with open(secret_path, 'rb') as secret_file:
                files = {
                    'carrier_file': ('debug_carrier.png', carrier_file, 'image/png'),
                    'content_file': ('debug_secret.jpg', secret_file, 'image/jpeg')
                }
                data = {
                    'carrier_type': 'image',
                    'content_type': 'file',
                    'password': 'test123'
                }
                
                embed_response = requests.post('http://localhost:8000/api/embed', files=files, data=data)
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code}")
            return False
            
        embed_result = embed_response.json()
        operation_id = embed_result['operation_id']
        
        # Wait for completion
        for i in range(10):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            if status_data.get('status') == 'completed':
                break
            time.sleep(0.5)
        
        # Download
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        stego_path = "debug_stego.png"
        with open(stego_path, 'wb') as f:
            f.write(download_response.content)
        
        # Extract
        with open(stego_path, 'rb') as stego_file:
            files = {'stego_file': ('debug_stego.png', stego_file, 'image/png')}
            data = {'carrier_type': 'image', 'password': 'test123'}
            extract_response = requests.post('http://localhost:8000/api/extract', files=files, data=data)
        
        print(f"   Extract status: {extract_response.status_code}")
        if extract_response.status_code == 200:
            print("   ✅ DEBUG STYLE WORKS!")
            return True
        else:
            print(f"   ❌ DEBUG STYLE FAILED: {extract_response.text}")
            return False
            
    finally:
        for f in [carrier_path, secret_path, "debug_stego.png"]:
            if os.path.exists(f):
                os.remove(f)

def test_comprehensive_style():
    """Test using the same style as comprehensive test"""
    print("\n🔍 COMPREHENSIVE STYLE TEST")
    print("=" * 40)
    
    # Create files similar to comprehensive test
    carrier_path = "comp_carrier.png"
    img = Image.new('RGB', (200, 200), color='red')
    img.save(carrier_path)
    
    secret_content = "This is secret content for testing steganography."
    secret_path = "secret_content.txt"
    with open(secret_path, 'w') as f:
        f.write(secret_content)
    
    try:
        # Embed (similar to comprehensive test)
        with open(carrier_path, 'rb') as carrier_file:
            with open(secret_path, 'rb') as secret_file:
                embed_response = requests.post('http://localhost:8000/api/embed',
                    files={
                        'carrier_file': carrier_file,
                        'content_file': secret_file
                    },
                    data={
                        'carrier_type': 'image',
                        'content_type': 'file', 
                        'password': 'test123'
                    })
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code}")
            return False
            
        embed_data = embed_response.json()
        operation_id = embed_data['operation_id']
        
        # Wait for completion
        for i in range(10):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            if status_data.get('status') == 'completed':
                break
            time.sleep(0.5)
        
        # Download
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        processed_path = "comp_processed.png"
        with open(processed_path, 'wb') as f:
            f.write(download_response.content)
        
        # Extract (exactly like comprehensive test)
        with open(processed_path, 'rb') as pf:
            extract_response = requests.post('http://localhost:8000/api/extract',
                files={'stego_file': pf},
                data={'carrier_type': 'image', 'password': 'test123'})
        
        print(f"   Extract status: {extract_response.status_code}")
        if extract_response.status_code == 200:
            print("   ✅ COMPREHENSIVE STYLE WORKS!")
            return True
        else:
            print(f"   ❌ COMPREHENSIVE STYLE FAILED")
            try:
                error_data = extract_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {extract_response.text}")
            return False
            
    finally:
        for f in [carrier_path, secret_path, "comp_processed.png"]:
            if os.path.exists(f):
                os.remove(f)

def main():
    print("🔬 COMPARING WORKING vs FAILING EXTRACTION METHODS")
    print("=" * 60)
    
    debug_works = test_debug_style()
    comp_works = test_comprehensive_style()
    
    print(f"\n📊 RESULTS:")
    print(f"   Debug style (file to file): {'✅' if debug_works else '❌'}")
    print(f"   Comprehensive style (text file): {'✅' if comp_works else '❌'}")
    
    if debug_works and not comp_works:
        print(f"\n🎯 ISSUE IDENTIFIED:")
        print(f"   The problem is likely related to:")
        print(f"   - Text file vs image file as secret content")
        print(f"   - Different file naming in the request")
        print(f"   - File upload format differences")

if __name__ == "__main__":
    main()
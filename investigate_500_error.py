#!/usr/bin/env python3
"""
Detailed 500 error investigation - capture exact error response
"""

import requests
import tempfile
import os
from PIL import Image
import time
import json

def test_extract_with_error_capture():
    """Test extraction and capture detailed error information"""
    print("🔍 DETAILED 500 ERROR INVESTIGATION")
    print("=" * 50)
    
    try:
        # Create test files (similar to comprehensive test)
        carrier_path = "error_test_carrier.png"
        img = Image.new('RGB', (200, 200), color='red')
        img.save(carrier_path)
        
        secret_content = "This is secret content for testing steganography extraction errors."
        secret_path = "error_test_secret.txt"
        with open(secret_path, 'w') as f:
            f.write(secret_content)
        
        print(f"✅ Created test files:")
        print(f"   Carrier: {carrier_path} ({os.path.getsize(carrier_path)} bytes)")
        print(f"   Secret: {secret_path} ({os.path.getsize(secret_path)} bytes)")
        
        # Step 1: Embed
        print(f"\n📤 Step 1: Embedding...")
        with open(carrier_path, 'rb') as cf, open(secret_path, 'rb') as sf:
            embed_response = requests.post('http://localhost:8000/api/embed',
                files={'carrier_file': cf, 'content_file': sf},
                data={'carrier_type': 'image', 'content_type': 'file', 'password': 'test123'})
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code}")
            print(f"   Response: {embed_response.text}")
            return False
            
        embed_data = embed_response.json()
        operation_id = embed_data['operation_id']
        print(f"✅ Embed started: {operation_id}")
        
        # Step 2: Wait for completion
        print(f"⏳ Step 2: Waiting for embedding completion...")
        for i in range(30):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            
            if status_data.get('status') == 'completed':
                print("✅ Embedding completed!")
                break
            elif status_data.get('status') == 'failed':
                print(f"❌ Embedding failed: {status_data.get('error')}")
                return False
            time.sleep(0.5)
        
        # Step 3: Download
        print(f"📥 Step 3: Downloading stego file...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
            
        stego_path = "error_test_stego.png"
        with open(stego_path, 'wb') as f:
            f.write(download_response.content)
        print(f"✅ Stego downloaded: {len(download_response.content)} bytes")
        
        # Verify stego file integrity
        try:
            with Image.open(stego_path) as img:
                print(f"   Stego image: {img.size} {img.mode}")
        except Exception as e:
            print(f"   ⚠️ Stego image issue: {e}")
        
        # Step 4: Extract with detailed error capture
        print(f"\n🔓 Step 4: Extracting with error capture...")
        
        # Test Method 1: Same as comprehensive test
        print(f"   Method 1: Using comprehensive test approach...")
        with open(stego_path, 'rb') as pf:
            extract_response = requests.post('http://localhost:8000/api/extract',
                files={'stego_file': pf},
                data={'carrier_type': 'image', 'password': 'test123'})
        
        print(f"   Response status: {extract_response.status_code}")
        print(f"   Response headers: {dict(extract_response.headers)}")
        
        if extract_response.status_code == 500:
            print(f"❌ 500 Error captured!")
            
            # Try to get JSON error details
            try:
                error_json = extract_response.json()
                print(f"   JSON Error Details:")
                print(f"   {json.dumps(error_json, indent=4)}")
            except:
                print(f"   Raw Error Response:")
                print(f"   {extract_response.text}")
            
            return False
            
        elif extract_response.status_code == 200:
            print(f"✅ Method 1 worked! Extraction started successfully.")
            extract_data = extract_response.json()
            extract_operation_id = extract_data['operation_id']
            print(f"   Operation ID: {extract_operation_id}")
            
            # Check extraction completion
            print(f"   Checking extraction status...")
            for i in range(15):
                extract_status_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/status')
                extract_status_data = extract_status_response.json()
                
                status = extract_status_data.get('status')
                if status == 'completed':
                    print(f"   ✅ Extraction completed successfully!")
                    result = extract_status_data.get('result', {})
                    print(f"   Extracted filename: {result.get('filename', 'N/A')}")
                    print(f"   Data type: {result.get('data_type', 'N/A')}")
                    return True
                elif status == 'failed':
                    print(f"   ❌ Extraction processing failed: {extract_status_data.get('error')}")
                    return False
                time.sleep(0.5)
            
            print(f"   ❌ Extraction timeout")
            return False
            
        else:
            print(f"❌ Unexpected response code: {extract_response.status_code}")
            print(f"   Response: {extract_response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for f in [carrier_path, secret_path, "error_test_stego.png"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

def test_file_format_differences():
    """Test different file formats to see if specific formats cause 500 errors"""
    print("\n🔬 TESTING DIFFERENT FILE FORMATS")
    print("=" * 50)
    
    formats_to_test = [
        ('image', '.png', lambda: Image.new('RGB', (100, 100), color='blue')),
        ('image', '.jpg', lambda: Image.new('RGB', (100, 100), color='green')),
    ]
    
    secret_content = "Test secret for format testing."
    
    for carrier_type, ext, create_func in formats_to_test:
        print(f"\n📋 Testing {carrier_type} with {ext} format...")
        
        try:
            # Create carrier
            carrier_path = f"format_test_carrier{ext}"
            if ext in ['.png', '.jpg']:
                img = create_func()
                img.save(carrier_path, 'PNG' if ext == '.png' else 'JPEG')
            
            # Create secret
            secret_path = "format_test_secret.txt"
            with open(secret_path, 'w') as f:
                f.write(secret_content)
            
            # Quick embed and extract test
            with open(carrier_path, 'rb') as cf, open(secret_path, 'rb') as sf:
                embed_response = requests.post('http://localhost:8000/api/embed',
                    files={'carrier_file': cf, 'content_file': sf},
                    data={'carrier_type': carrier_type, 'content_type': 'file', 'password': 'test123'})
            
            if embed_response.status_code == 200:
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
                if download_response.status_code == 200:
                    stego_path = f"format_test_stego{ext}"
                    with open(stego_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    # Test extraction
                    with open(stego_path, 'rb') as pf:
                        extract_response = requests.post('http://localhost:8000/api/extract',
                            files={'stego_file': pf},
                            data={'carrier_type': carrier_type, 'password': 'test123'})
                    
                    print(f"   Extract status: {extract_response.status_code}")
                    if extract_response.status_code != 200:
                        print(f"   ❌ {carrier_type} {ext} causes error!")
                        if extract_response.status_code == 500:
                            try:
                                error_data = extract_response.json()
                                print(f"   Error: {error_data}")
                            except:
                                print(f"   Raw error: {extract_response.text}")
                    else:
                        print(f"   ✅ {carrier_type} {ext} works!")
            
            # Cleanup
            for f in [carrier_path, secret_path, f"format_test_stego{ext}"]:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass
                        
        except Exception as e:
            print(f"   ❌ Error testing {carrier_type} {ext}: {e}")

if __name__ == "__main__":
    print("🚨 INVESTIGATING 500 EXTRACTION ERRORS")
    print("This will help identify the exact cause and solution.")
    print()
    
    success = test_extract_with_error_capture()
    test_file_format_differences()
    
    print(f"\n🎯 Investigation Complete")
    if not success:
        print("❌ 500 error reproduced - check output for details")
    else:
        print("✅ No 500 error found - extraction working")
    
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Exact replica of comprehensive test with detailed error capture
"""

import requests
import tempfile
import os
from PIL import Image
import time
import json
import numpy as np
from scipy.io import wavfile
import cv2

def create_test_image(path):
    """Create a test image"""
    img = Image.new('RGB', (200, 200), color='red')
    img.save(path)
    return path

def create_test_audio(path):
    """Create a test audio file"""
    sample_rate = 44100
    duration = 2
    samples = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
    samples = (samples * 32767).astype(np.int16)
    wavfile.write(path, sample_rate, samples)
    return path

def create_test_video(path):
    """Create a test video file"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, 10.0, (100, 100))
    
    for i in range(20):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[:, :] = [i*10 % 255, (i*20) % 255, (i*30) % 255]
        out.write(frame)
    
    out.release()
    return path

def create_test_document(path):
    """Create a test document"""
    content = """This is a test document for steganography.

This paragraph has more content to test text steganography.
We want to ensure the document integrity is maintained.

Final paragraph with additional text for testing purposes."""
    
    with open(path, 'w') as f:
        f.write(content)
    return path

def test_single_type_detailed(carrier_type):
    """Test a single steganography type with detailed error reporting"""
    print(f"\n🔧 DETAILED TEST: {carrier_type.upper()} Steganography")
    print("-" * 50)
    
    secret_content = f"This is secret content for {carrier_type} steganography testing."
    
    try:
        # Create carrier file
        carrier_file = f"detailed_{carrier_type}_carrier"
        if carrier_type == 'image':
            carrier_file += '.png'
            create_test_image(carrier_file)
        elif carrier_type == 'audio':
            carrier_file += '.wav'
            create_test_audio(carrier_file)
        elif carrier_type == 'video':
            carrier_file += '.mp4'
            create_test_video(carrier_file)
        elif carrier_type == 'document':
            carrier_file += '.txt'
            create_test_document(carrier_file)
        
        print(f"✅ Created carrier: {carrier_file} ({os.path.getsize(carrier_file)} bytes)")
        
        # Create secret file using NamedTemporaryFile (exactly like comprehensive test)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as secret_file:
            secret_file.write(secret_content)
            secret_path = secret_file.name
        
        print(f"✅ Created secret: {secret_path} ({os.path.getsize(secret_path)} bytes)")
        
        # 1. Embed (exactly like comprehensive test)
        print("1️⃣ Embedding via API...")
        with open(carrier_file, 'rb') as cf, open(secret_path, 'rb') as sf:
            embed_response = requests.post('http://localhost:8000/api/embed',
                files={'carrier_file': cf, 'content_file': sf},
                data={'carrier_type': carrier_type, 'content_type': 'file', 'password': 'test123'})
        
        if embed_response.status_code != 200:
            print(f"❌ Embedding failed: {embed_response.status_code}")
            print(f"   Response: {embed_response.text}")
            return False
        
        embed_data = embed_response.json()
        operation_id = embed_data['operation_id']
        print(f"✅ Embedding started: {operation_id}")
        
        # 2. Wait for completion (with proper polling)
        print("2️⃣ Waiting for processing...")
        for i in range(30):
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            
            if status_data.get('status') == 'completed':
                print("✅ Processing completed!")
                break
            elif status_data.get('status') == 'failed':
                print(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}")
                return False
            time.sleep(0.5)
        else:
            print("❌ Processing timeout")
            return False
        
        # 3. Download (exactly like comprehensive test)
        print("3️⃣ Downloading processed file...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
        
        # Save using NamedTemporaryFile (exactly like comprehensive test)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{carrier_type}') as processed_file:
            processed_file.write(download_response.content)
            processed_path = processed_file.name
        
        print(f"✅ File downloaded: {processed_path} ({os.path.getsize(processed_path)} bytes)")
        
        # 4. Extract (exactly like comprehensive test, but with detailed error capture)
        print("4️⃣ Extracting via API...")
        print(f"   File path: {processed_path}")
        print(f"   File size: {os.path.getsize(processed_path)} bytes")
        
        # Read file and check first few bytes
        with open(processed_path, 'rb') as f:
            first_bytes = f.read(20)
        print(f"   First 20 bytes: {first_bytes.hex()}")
        
        # Make extraction request (exactly like comprehensive test)
        with open(processed_path, 'rb') as pf:
            print(f"   Making extraction request...")
            extract_response = requests.post('http://localhost:8000/api/extract',
                files={'stego_file': pf},
                data={'carrier_type': carrier_type, 'password': 'test123'})
        
        print(f"   Response status: {extract_response.status_code}")
        print(f"   Response headers: {dict(extract_response.headers)}")
        
        if extract_response.status_code == 500:
            print(f"❌ 500 ERROR CAPTURED!")
            print(f"   Content-Type: {extract_response.headers.get('content-type', 'N/A')}")
            
            # Try to parse JSON error
            try:
                error_json = extract_response.json()
                print(f"   JSON Error Details:")
                print(f"   {json.dumps(error_json, indent=4)}")
            except:
                print(f"   Raw Error Response:")
                print(f"   '{extract_response.text}'")
            
            return False
            
        elif extract_response.status_code == 200:
            print(f"✅ Extraction request successful!")
            extract_data = extract_response.json()
            extract_operation_id = extract_data['operation_id']
            print(f"   Operation ID: {extract_operation_id}")
            return True
        else:
            print(f"❌ Unexpected status: {extract_response.status_code}")
            print(f"   Response: {extract_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for f in [carrier_file, secret_path, processed_path]:
            if 'f' in locals() and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

def main():
    print("🔬 EXACT COMPREHENSIVE TEST REPLICA WITH ERROR CAPTURE")
    print("=" * 60)
    
    # Test each type individually to isolate the issue
    types_to_test = ['image', 'audio', 'video', 'document']
    results = {}
    
    for carrier_type in types_to_test:
        try:
            success = test_single_type_detailed(carrier_type)
            results[carrier_type] = success
            
            # Add delay between tests to avoid server overload
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ {carrier_type} test crashed: {e}")
            results[carrier_type] = False
    
    print(f"\n📊 DETAILED RESULTS:")
    print("=" * 40)
    for carrier_type, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{carrier_type.upper():12} steganography: {status}")
    
    all_success = all(results.values())
    print(f"\n🎯 Overall: {'✅ ALL WORKING' if all_success else '❌ SOME FAILED'}")
    
    return all_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Comprehensive test for file embedding issues
"""

import requests
import time
import os
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_python_file_embedding():
    """Test Python file embedding and extraction with correct extensions"""
    
    print("🐍 Testing Python File Embedding & Extension Preservation")
    print("=" * 65)
    
    # Create a test Python file
    test_py_content = '''#!/usr/bin/env python3
"""Test Python file for steganography"""

def hello_world():
    print("Hello from hidden Python file!")
    return "This is a Python file"

if __name__ == "__main__":
    hello_world()
'''
    
    test_py_path = "test_embedding.py"
    with open(test_py_path, 'w') as f:
        f.write(test_py_content)
    
    print(f"✅ Created test Python file: {test_py_path}")
    
    # Test embedding in audio (main issue)
    audio_file = "direct_test_audio.wav"
    if Path(audio_file).exists():
        print(f"\n🎵 Testing Python file in Audio ({audio_file})")
        result = embed_and_extract(audio_file, test_py_path, "audio", ".py")
        if result:
            print("✅ Audio Python embedding successful with correct extension!")
        else:
            print("❌ Audio Python embedding failed")
    
    # Test embedding in video
    video_file = "clean_carrier.mp4" 
    if Path(video_file).exists():
        print(f"\n📹 Testing Python file in Video ({video_file})")
        result = embed_and_extract(video_file, test_py_path, "video", ".py")
        if result:
            print("✅ Video Python embedding successful!")
        else:
            print("❌ Video Python embedding failed")
    
    # Test embedding in image
    image_file = "debug_embedded.png"
    if Path(image_file).exists():
        print(f"\n🖼️  Testing Python file in Image ({image_file})")
        result = embed_and_extract(image_file, test_py_path, "image", ".py")
        if result:
            print("✅ Image Python embedding successful!")
        else:
            print("❌ Image Python embedding failed")
    
    # Cleanup
    os.unlink(test_py_path)

def test_document_file_embedding():
    """Test document file embedding"""
    
    print("\n📄 Testing Document File Embedding")
    print("=" * 40)
    
    # Look for document files
    doc_files = []
    for ext in ['.doc', '.docx']:
        doc_files.extend(Path('.').glob(f'*{ext}'))
    
    if not doc_files:
        print("⏭️ No .doc/.docx files found for testing")
        return
        
    doc_file = str(doc_files[0])
    print(f"📄 Testing with document: {doc_file}")
    
    # Test embedding in image
    image_file = "debug_embedded.png"
    if Path(image_file).exists():
        print(f"\n🖼️  Testing Document file in Image ({image_file})")
        
        expected_ext = Path(doc_file).suffix
        result = embed_and_extract(image_file, doc_file, "image", expected_ext)
        if result:
            print("✅ Document embedding successful with correct extension!")
        else:
            print("❌ Document embedding failed")

def embed_and_extract(carrier_file, content_file, carrier_type, expected_extension):
    """Helper function to embed and extract, return True if successful with correct extension"""
    
    password = "test123"
    
    try:
        # Step 1: Embed
        print(f"  🔐 Embedding {content_file} in {carrier_file}...")
        
        with open(carrier_file, 'rb') as carrier_f, open(content_file, 'rb') as content_f:
            embed_data = {
                'password': password,
                'content_type': 'file',
                'carrier_type': carrier_type
            }
            embed_files = {
                'carrier_file': (carrier_file, carrier_f),
                'content_file': (content_file, content_f)
            }
            
            response = requests.post(f"{API_BASE}/api/embed", data=embed_data, files=embed_files)
            
            if response.status_code != 200:
                print(f"    ❌ Embed failed: {response.status_code} - {response.text}")
                return False
                
            embed_result = response.json()
            operation_id = embed_result['operation_id']
            print(f"    ✅ Embed started: {operation_id}")
            
        # Wait for embedding
        for i in range(30):
            time.sleep(0.5)
            status_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()['status']
                if status == "completed":
                    break
                elif status == "failed":
                    print(f"    ❌ Embed operation failed")
                    return False
        else:
            print(f"    ❌ Embed timeout")
            return False
            
        # Download stego file
        download_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/download")
        if download_response.status_code != 200:
            print(f"    ❌ Download failed")
            return False
            
        stego_filename = f"test_stego_{int(time.time())}{Path(carrier_file).suffix}"
        with open(stego_filename, 'wb') as f:
            f.write(download_response.content)
            
        print(f"    ✅ Stego file saved: {stego_filename}")
        
        # Step 2: Extract
        print(f"  🔓 Extracting from {stego_filename}...")
        
        with open(stego_filename, 'rb') as stego_f:
            extract_data = {
                'password': password,
                'output_format': 'auto'
            }
            extract_files = {
                'stego_file': (stego_filename, stego_f)
            }
            
            response = requests.post(f"{API_BASE}/api/extract", data=extract_data, files=extract_files)
            
            if response.status_code != 200:
                print(f"    ❌ Extract failed: {response.status_code} - {response.text}")
                os.unlink(stego_filename)
                return False
                
            extract_result = response.json()
            extract_operation_id = extract_result['operation_id']
            
        # Wait for extraction
        for i in range(30):
            time.sleep(0.5)
            status_response = requests.get(f"{API_BASE}/api/operations/{extract_operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data['status']
                if status == "completed":
                    break
                elif status == "failed":
                    error_msg = status_data.get('error', 'Unknown')
                    print(f"    ❌ Extract operation failed: {error_msg}")
                    os.unlink(stego_filename)
                    return False
        else:
            print(f"    ❌ Extract timeout")
            os.unlink(stego_filename)
            return False
            
        # Download extracted file
        download_response = requests.get(f"{API_BASE}/api/operations/{extract_operation_id}/download")
        if download_response.status_code != 200:
            print(f"    ❌ Extract download failed")
            os.unlink(stego_filename)
            return False
            
        # Check Content-Disposition for filename
        content_disp = download_response.headers.get('Content-Disposition', '')
        print(f"    📋 Content-Disposition: {content_disp}")
        
        # Extract filename from Content-Disposition
        import re
        filename_match = re.search(r'filename="([^"]+)"', content_disp)
        if filename_match:
            extracted_filename = filename_match.group(1)
            print(f"    📂 Extracted filename: {extracted_filename}")
            
            # Check if extension matches expected
            extracted_ext = Path(extracted_filename).suffix
            if extracted_ext.lower() == expected_extension.lower():
                print(f"    ✅ Extension correct: {extracted_ext}")
                success = True
            else:
                print(f"    ❌ Extension wrong: expected {expected_extension}, got {extracted_ext}")
                success = False
        else:
            print(f"    ❌ No filename found in Content-Disposition")
            success = False
            
        # Save extracted file for verification
        extracted_path = f"test_extracted_{int(time.time())}{expected_extension}"
        with open(extracted_path, 'wb') as f:
            f.write(download_response.content)
            
        print(f"    💾 Extracted file saved: {extracted_path}")
        
        # Compare file sizes
        original_size = Path(content_file).stat().st_size
        extracted_size = len(download_response.content)
        
        if original_size == extracted_size:
            print(f"    ✅ File size match: {original_size} bytes")
        else:
            print(f"    ⚠️  File size difference: {original_size} vs {extracted_size} bytes")
        
        # Cleanup
        os.unlink(stego_filename)
        os.unlink(extracted_path)
        
        return success
        
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_python_file_embedding()
    test_document_file_embedding()
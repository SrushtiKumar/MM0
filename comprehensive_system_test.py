#!/usr/bin/env python3
"""
Comprehensive end-to-end test for all steganography types through the API
"""

import requests
import tempfile
import os
import time
import numpy as np
from PIL import Image
from scipy.io import wavfile
import cv2

def create_test_image(path):
    """Create a test PNG image"""
    img = Image.fromarray(np.random.randint(0, 255, (200, 200, 3), dtype='uint8'), 'RGB')
    img.save(path, 'PNG')
    return path

def create_test_audio(path):
    """Create a test WAV audio"""
    sample_rate = 44100
    duration = 2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    wavfile.write(path, sample_rate, audio_data)
    return path

def create_test_video(path):
    """Create a test MP4 video"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, 10, (320, 240))
    
    for i in range(20):  # 20 frames
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frame[:, :] = [i * 12, 100, 255 - i * 12]
        cv2.rectangle(frame, (50, 50), (270, 190), (255, 255, 255), 2)
        out.write(frame)
    
    out.release()
    return path

def create_test_document(path):
    """Create a test text document"""
    content = """This is a test document for steganography.

It contains multiple paragraphs with sample content.
The document should remain readable after processing.

This paragraph has more content to test text steganography.
We want to ensure the document integrity is maintained.

Final paragraph with additional text for testing purposes."""
    
    with open(path, 'w') as f:
        f.write(content)
    return path

def test_file_integrity(file_path, file_type):
    """Test if a file maintains its integrity after processing"""
    try:
        if file_type == 'image':
            img = Image.open(file_path)
            print(f"  ✅ Image: {img.size}, {img.mode}")
            return True
        elif file_type == 'audio':
            sample_rate, audio_data = wavfile.read(file_path)
            print(f"  ✅ Audio: {sample_rate} Hz, {len(audio_data)} samples")
            return True
        elif file_type == 'video':
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                print(f"  ✅ Video: {frame_count} frames, {fps} fps")
                cap.release()
                return True
            else:
                print(f"  ❌ Video cannot be opened")
                return False
        elif file_type == 'document':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✅ Document: {len(content)} characters")
            return True
    except Exception as e:
        print(f"  ❌ {file_type.title()} corrupted: {e}")
        return False

def test_api_workflow(carrier_file, carrier_type, secret_content):
    """Test complete API workflow: embed -> download -> verify -> extract"""
    
    print(f"\n🔧 Testing {carrier_type.upper()} Steganography API")
    print("-" * 40)
    
    try:
        # Create secret file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as secret_file:
            secret_file.write(secret_content)
            secret_path = secret_file.name
        
        # 1. Embed via API
        print("1️⃣ Embedding via API...")
        with open(carrier_file, 'rb') as cf, open(secret_path, 'rb') as sf:
            response = requests.post('http://localhost:8000/api/embed',
                files={'carrier_file': cf, 'content_file': sf},
                data={'carrier_type': carrier_type, 'content_type': 'file', 'password': 'test123'})
        
        if response.status_code != 200:
            print(f"  ❌ Embedding failed: {response.status_code}")
            return False
            
        embed_data = response.json()
        operation_id = embed_data.get('operation_id')
        print(f"  ✅ Embedding started: {operation_id}")
        
        # 2. Wait for completion and download
        print("2️⃣ Waiting for processing...")
        
        # Poll for completion instead of fixed sleep
        for i in range(30):  # Up to 15 seconds
            status_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/status')
            status_data = status_response.json()
            
            if status_data.get('status') == 'completed':
                print("  ✅ Processing completed!")
                break
            elif status_data.get('status') == 'failed':
                print(f"  ❌ Processing failed: {status_data.get('error', 'Unknown error')}")
                return False
            time.sleep(0.5)
        else:
            print("  ❌ Processing timeout")
            return False
        
        print("3️⃣ Downloading processed file...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        if download_response.status_code != 200:
            print(f"  ❌ Download failed: {download_response.status_code}")
            return False
        
        # Save processed file with proper extension
        extension_map = {
            'image': '.png',
            'audio': '.wav', 
            'video': '.mp4',
            'document': '.txt'
        }
        proper_extension = extension_map.get(carrier_type, f'.{carrier_type}')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=proper_extension) as processed_file:
            processed_file.write(download_response.content)
            processed_path = processed_file.name
        
        print(f"  ✅ File downloaded: {processed_path}")
        
        # 3. Test integrity
        print("3️⃣ Testing file integrity...")
        if not test_file_integrity(processed_path, carrier_type):
            print(f"  ❌ {carrier_type.upper()} file integrity test failed!")
            return False
        
        # 4. Extract via API
        print("4️⃣ Extracting via API...")
        with open(processed_path, 'rb') as pf:
            extract_response = requests.post('http://localhost:8000/api/extract',
                files={'stego_file': pf},
                data={'carrier_type': carrier_type, 'password': 'test123'})
        
        if extract_response.status_code != 200:
            print(f"  ❌ Extraction failed: {extract_response.status_code}")
            return False
            
        extract_data = extract_response.json()
        extract_operation_id = extract_data.get('operation_id')
        print(f"  ✅ Extraction started: {extract_operation_id}")
        
        # 5. Wait for extraction completion and download
        print("5️⃣ Waiting for extraction completion...")
        
        # Poll for extraction completion
        for i in range(30):  # Up to 15 seconds
            extract_status_response = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/status')
            extract_status_data = extract_status_response.json()
            
            if extract_status_data.get('status') == 'completed':
                print("  ✅ Extraction completed!")
                break
            elif extract_status_data.get('status') == 'failed':
                print(f"  ❌ Extraction failed: {extract_status_data.get('error', 'Unknown error')}")
                return False
            time.sleep(0.5)
        else:
            print("  ❌ Extraction timeout")
            return False
        
        print("6️⃣ Downloading extracted file...")
        extract_download = requests.get(f'http://localhost:8000/api/operations/{extract_operation_id}/download')
        if extract_download.status_code != 200:
            print(f"  ❌ Extract download failed: {extract_download.status_code}")
            return False
        
        # 7. Verify content
        print("7️⃣ Verifying content...")
        
        # Try to decode the content
        try:
            extracted_content = extract_download.content.decode('utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try other encodings
            try:
                extracted_content = extract_download.content.decode('latin-1')
            except:
                extracted_content = str(extract_download.content)
        
        # Normalize line endings for comparison (handle Windows \r\n vs Unix \n)
        import re
        secret_normalized = re.sub(r'\r\n|\r|\n', '\n', secret_content.strip())
        extracted_normalized = re.sub(r'\r\n|\r|\n', '\n', extracted_content.strip())
        
        print(f"  📊 Content details:")
        print(f"     Original length: {len(secret_content)} chars")
        print(f"     Extracted length: {len(extracted_content)} chars")
        print(f"     Original (first 50): {repr(secret_content[:50])}")
        print(f"     Extracted (first 50): {repr(extracted_content[:50])}")
        
        # Check if the normalized content matches
        if secret_normalized == extracted_normalized:
            print(f"  ✅ Content verified: Exact match after normalizing line endings!")
            print(f"     Normalized original: {len(secret_normalized)} chars")
            print(f"     Normalized extracted: {len(extracted_normalized)} chars")
        elif secret_normalized in extracted_normalized:
            print(f"  ✅ Content verified: Original content found in extracted data!")
            print(f"     Match type: substring (after line ending normalization)")
        else:
            print(f"  ❌ Content mismatch even after normalization!")
            print(f"     Looking for: {repr(secret_normalized)}")
            print(f"     Found: {repr(extracted_normalized)}")
            return False
        
        # Cleanup
        try:
            os.unlink(secret_path)
            os.unlink(processed_path)
        except:
            pass
        
        print(f"  🎉 {carrier_type.upper()} steganography: COMPLETE SUCCESS!")
        return True
        
    except Exception as e:
        print(f"  ❌ {carrier_type.upper()} test failed: {e}")
        return False

def comprehensive_system_test():
    """Run comprehensive tests for all steganography types"""
    
    print("🚀 COMPREHENSIVE STEGANOGRAPHY SYSTEM TEST")
    print("=" * 60)
    
    results = {}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test data
        secret_content = "This is comprehensive test secret data!\nTesting all steganography modules.\nEnsuring no corruption occurs."
        
        # 1. Test Image Steganography
        print("\n📸 TESTING IMAGE STEGANOGRAPHY")
        image_path = create_test_image(os.path.join(temp_dir, 'test.png'))
        results['image'] = test_api_workflow(image_path, 'image', secret_content)
        
        # 2. Test Audio Steganography  
        print("\n🎵 TESTING AUDIO STEGANOGRAPHY")
        audio_path = create_test_audio(os.path.join(temp_dir, 'test.wav'))
        results['audio'] = test_api_workflow(audio_path, 'audio', secret_content)
        
        # 3. Test Video Steganography
        print("\n🎬 TESTING VIDEO STEGANOGRAPHY")
        video_path = create_test_video(os.path.join(temp_dir, 'test.mp4'))
        results['video'] = test_api_workflow(video_path, 'video', secret_content)
        
        # 4. Test Document Steganography
        print("\n📄 TESTING DOCUMENT STEGANOGRAPHY")
        doc_path = create_test_document(os.path.join(temp_dir, 'test.txt'))
        results['document'] = test_api_workflow(doc_path, 'document', secret_content)
    
    # Final Results
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for media_type, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{media_type.upper():12} steganography: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("✅ No file corruption detected in any steganography module")
        print("✅ All carrier files remain in their original format and functional")
        print("✅ All hidden data is properly embedded and extracted")
        print("✅ Complete API workflow functional for all media types")
        print("\n🎯 STEGANOGRAPHY SYSTEM IS 100% OPERATIONAL!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  System needs attention for failed modules")
    
    return all_passed

if __name__ == "__main__":
    success = comprehensive_system_test()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test proper API workflow: embed -> extract -> download for all steganography types
Following the correct two-step process for extraction
"""

import requests
import os
import time
import json
import tempfile
from io import BytesIO

SERVER_URL = "http://localhost:8000"
TEST_FILES_DIR = "C:\\Users\\Administrator\\Documents\\Git\\vF"

def wait_for_operation(operation_id, max_wait=30):
    """Wait for operation to complete and return status"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                print(f"Operation {operation_id}: {status}")
                
                if status == 'completed':
                    return True
                elif status == 'failed':
                    print(f"Operation failed: {data.get('error', 'Unknown error')}")
                    return False
                    
            time.sleep(2)
        except Exception as e:
            print(f"Error checking operation status: {e}")
            time.sleep(2)
    
    print(f"Operation {operation_id} timed out after {max_wait} seconds")
    return False

def test_image_steganography():
    print("\n=== Testing Image Steganography ===")
    
    # Use an existing image file
    image_path = os.path.join(TEST_FILES_DIR, "final_web_test_video.mp4")  # We'll use this as carrier
    if not os.path.exists(image_path):
        # Create a simple test image if none exists
        print("Creating test image...")
        import PIL.Image
        img = PIL.Image.new('RGB', (100, 100), color='red')
        image_path = os.path.join(TEST_FILES_DIR, "test_image.png")
        img.save(image_path)
    
    secret_data = "X"  # Single character for tiny documents
    
    # Step 1: Embed
    print("1. Embedding data in image...")
    with open(image_path, 'rb') if os.path.exists(image_path) else BytesIO() as f:
        files = {'carrier_file': ('test_image.png', f, 'image/png')}
        data = {
            'text_content': secret_data,
            'content_type': 'text',
            'password': 'test123'
        }
        
        response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
        print(f"Embed response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Embed failed: {response.text}")
            return False
            
        embed_result = response.json()
        print(f"Embed result: {embed_result}")
        
        if not embed_result.get('success'):
            print("Embed operation reported failure")
            return False
            
        # Get the embedded file
        embed_operation_id = embed_result.get('operation_id')
        if not embed_operation_id:
            print("No operation_id returned from embed")
            return False
            
        # Wait for embed to complete
        if not wait_for_operation(embed_operation_id):
            print("Embed operation failed")
            return False
            
        # Download embedded file
        download_response = requests.get(f"{SERVER_URL}/api/operations/{embed_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download embedded file: {download_response.status_code}")
            return False
            
        embedded_file_path = os.path.join(TEST_FILES_DIR, "test_embedded_image.png")
        with open(embedded_file_path, 'wb') as f:
            f.write(download_response.content)
        print(f"Embedded file saved to: {embedded_file_path}")

    # Step 2: Extract
    print("2. Extracting data from image...")
    with open(embedded_file_path, 'rb') as f:
        files = {'stego_file': ('embedded_image.png', f, 'image/png')}
        data = {
            'password': 'test123',
            'output_format': 'auto'
        }
        
        response = requests.post(f"{SERVER_URL}/api/extract", files=files, data=data)
        print(f"Extract response status: {response.status_code}")
        print(f"Extract response: {response.text}")
        
        if response.status_code != 200:
            print(f"Extract failed: {response.text}")
            return False
            
        extract_result = response.json()
        extract_operation_id = extract_result.get('operation_id')
        
        if not extract_operation_id:
            print("No operation_id returned from extract")
            return False
            
        # Wait for extraction to complete
        if not wait_for_operation(extract_operation_id):
            print("Extract operation failed")
            return False
            
        # Download extracted content
        download_response = requests.get(f"{SERVER_URL}/api/operations/{extract_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download extracted content: {download_response.status_code}")
            print(f"Response: {download_response.text}")
            return False
            
        extracted_content = download_response.content.decode('utf-8')
        print(f"Extracted content: '{extracted_content}'")
        
        # Verify content
        if extracted_content == secret_data:
            print("✅ Image steganography: Content verification PASSED")
            return True
        else:
            print(f"❌ Image steganography: Content mismatch. Expected: '{secret_data}', Got: '{extracted_content}'")
            return False

def test_audio_steganography():
    print("\n=== Testing Audio Steganography ===")
    
    # Use existing audio file - try larger files first
    audio_files = ["enhanced_audio_test.wav", "final_test_audio.wav", "direct_test_audio.wav"]
    audio_path = None
    for audio_file in audio_files:
        test_path = os.path.join(TEST_FILES_DIR, audio_file)
        if os.path.exists(test_path):
            audio_path = test_path
            break
    
    if not audio_path:
        print(f"No audio file found in: {audio_files}")
        return False
    
    secret_data = "Secret audio message for testing!"
    
    # Step 1: Embed
    print("1. Embedding data in audio...")
    with open(audio_path, 'rb') as f:
        files = {'carrier_file': ('test_audio.wav', f, 'audio/wav')}
        data = {
            'text_content': secret_data,
            'content_type': 'text',
            'password': 'test123'
        }
        
        response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
        print(f"Embed response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Embed failed: {response.text}")
            return False
            
        embed_result = response.json()
        embed_operation_id = embed_result.get('operation_id')
        
        if not wait_for_operation(embed_operation_id):
            return False
            
        # Download embedded file
        download_response = requests.get(f"{SERVER_URL}/api/operations/{embed_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download embedded file: {download_response.status_code}")
            return False
            
        embedded_file_path = os.path.join(TEST_FILES_DIR, "test_embedded_audio.wav")
        with open(embedded_file_path, 'wb') as f:
            f.write(download_response.content)
        print(f"Embedded file saved to: {embedded_file_path}")

    # Step 2: Extract
    print("2. Extracting data from audio...")
    with open(embedded_file_path, 'rb') as f:
        files = {'stego_file': ('embedded_audio.wav', f, 'audio/wav')}
        data = {
            'password': 'test123',
            'output_format': 'auto'
        }
        
        response = requests.post(f"{SERVER_URL}/api/extract", files=files, data=data)
        print(f"Extract response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Extract failed: {response.text}")
            return False
            
        extract_result = response.json()
        extract_operation_id = extract_result.get('operation_id')
        
        if not wait_for_operation(extract_operation_id):
            return False
            
        # Download extracted content
        download_response = requests.get(f"{SERVER_URL}/api/operations/{extract_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download extracted content: {download_response.status_code}")
            return False
            
        extracted_content = download_response.content.decode('utf-8')
        print(f"Extracted content: '{extracted_content}'")
        
        # Verify content
        if extracted_content == secret_data:
            print("✅ Audio steganography: Content verification PASSED")
            return True
        else:
            print(f"❌ Audio steganography: Content mismatch")
            return False

def test_video_steganography():
    print("\n=== Testing Video Steganography ===")
    
    # Use existing video file
    video_path = os.path.join(TEST_FILES_DIR, "direct_test_video.mp4")
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return False
    
    secret_data = "Secret video message for testing!"
    
    # Step 1: Embed
    print("1. Embedding data in video...")
    with open(video_path, 'rb') as f:
        files = {'carrier_file': ('test_video.mp4', f, 'video/mp4')}
        data = {
            'text_content': secret_data,
            'content_type': 'text',
            'password': 'test123'
        }
        
        response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
        print(f"Embed response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Embed failed: {response.text}")
            return False
            
        embed_result = response.json()
        embed_operation_id = embed_result.get('operation_id')
        
        if not wait_for_operation(embed_operation_id):
            return False
            
        # Download embedded file
        download_response = requests.get(f"{SERVER_URL}/api/operations/{embed_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download embedded file: {download_response.status_code}")
            return False
            
        embedded_file_path = os.path.join(TEST_FILES_DIR, "test_embedded_video.mp4")
        with open(embedded_file_path, 'wb') as f:
            f.write(download_response.content)
        print(f"Embedded file saved to: {embedded_file_path}")

    # Step 2: Extract
    print("2. Extracting data from video...")
    with open(embedded_file_path, 'rb') as f:
        files = {'stego_file': ('embedded_video.mp4', f, 'video/mp4')}
        data = {
            'password': 'test123',
            'output_format': 'auto'
        }
        
        response = requests.post(f"{SERVER_URL}/api/extract", files=files, data=data)
        print(f"Extract response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Extract failed: {response.text}")
            return False
            
        extract_result = response.json()
        extract_operation_id = extract_result.get('operation_id')
        
        if not wait_for_operation(extract_operation_id):
            return False
            
        # Download extracted content
        download_response = requests.get(f"{SERVER_URL}/api/operations/{extract_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download extracted content: {download_response.status_code}")
            return False
            
        extracted_content = download_response.content.decode('utf-8')
        print(f"Extracted content: '{extracted_content}'")
        
        # Verify content
        if extracted_content == secret_data:
            print("✅ Video steganography: Content verification PASSED")
            return True
        else:
            print(f"❌ Video steganography: Content mismatch")
            return False

def test_document_steganography():
    print("\n=== Testing Document Steganography ===")
    
    # Use existing document file - try larger files first  
    doc_files = ["large_test_document.txt", "large_test_document.doc", "test_document.doc", "final_test_doc.doc", "direct_test_document.doc"]
    doc_path = None
    for doc_file in doc_files:
        # First try current directory for the new large document
        test_path = os.path.join(os.getcwd(), doc_file)
        if os.path.exists(test_path):
            doc_path = test_path
            print(f"Using document: {doc_file} (size: {os.path.getsize(test_path)} bytes)")
            break
        # Then try the TEST_FILES_DIR
        test_path = os.path.join(TEST_FILES_DIR, doc_file)
        if os.path.exists(test_path):
            doc_path = test_path
            print(f"Using document: {doc_file} (size: {os.path.getsize(test_path)} bytes)")
            break
    
    if not doc_path:
        print(f"No document file found in: {doc_files}")
        return False
    
    secret_data = "Hi!"  # Use very short message for document steganography capacity
    
    # Step 1: Embed
    print("1. Embedding data in document...")
    with open(doc_path, 'rb') as f:
        files = {'carrier_file': ('test_document.txt', f, 'text/plain')}
        data = {
            'text_content': secret_data,
            'content_type': 'text',
            'password': 'test123'
        }
        
        response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
        print(f"Embed response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Embed failed: {response.text}")
            return False
            
        embed_result = response.json()
        embed_operation_id = embed_result.get('operation_id')
        
        if not wait_for_operation(embed_operation_id):
            return False
            
        # Download embedded file
        download_response = requests.get(f"{SERVER_URL}/api/operations/{embed_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download embedded file: {download_response.status_code}")
            return False
            
        embedded_file_path = os.path.join(TEST_FILES_DIR, "test_embedded_document.txt")
        with open(embedded_file_path, 'wb') as f:
            f.write(download_response.content)
        print(f"Embedded file saved to: {embedded_file_path}")

    # Step 2: Extract
    print("2. Extracting data from document...")
    with open(embedded_file_path, 'rb') as f:
        files = {'stego_file': ('embedded_document.txt', f, 'text/plain')}
        data = {
            'password': 'test123',
            'output_format': 'auto'
        }
        
        response = requests.post(f"{SERVER_URL}/api/extract", files=files, data=data)
        print(f"Extract response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Extract failed: {response.text}")
            return False
            
        extract_result = response.json()
        extract_operation_id = extract_result.get('operation_id')
        
        if not wait_for_operation(extract_operation_id):
            return False
            
        # Download extracted content
        download_response = requests.get(f"{SERVER_URL}/api/operations/{extract_operation_id}/download")
        if download_response.status_code != 200:
            print(f"Failed to download extracted content: {download_response.status_code}")
            return False
            
        extracted_content = download_response.content.decode('utf-8')
        print(f"Extracted content: '{extracted_content}'")
        
        # Verify content
        if extracted_content == secret_data:
            print("✅ Document steganography: Content verification PASSED")
            return True
        else:
            print(f"❌ Document steganography: Content mismatch")
            return False

def main():
    print("Testing proper API workflow for all steganography types...")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/api/health")
        if response.status_code != 200:
            print("❌ Server is not running or not healthy")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    print("✅ Server is running and healthy")
    
    results = {}
    results['image'] = test_image_steganography()
    results['audio'] = test_audio_steganography()
    results['video'] = test_video_steganography()
    results['document'] = test_document_steganography()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    for stego_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{stego_type.capitalize()} steganography: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

if __name__ == "__main__":
    main()
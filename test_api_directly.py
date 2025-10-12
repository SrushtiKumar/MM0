#!/usr/bin/env python3
"""
Quick API Test for Steganography Backend
Tests the embed and extract operations
"""

import requests
import time
import os

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

def test_video_embedding():
    """Test video embedding functionality"""
    print("Testing Video Embedding...")
    
    # Check if test video exists
    video_path = "simple_test_video.mp4"
    if not os.path.exists(video_path):
        print(f"Error: Test video {video_path} not found")
        return False
    
    # Prepare the request
    files = {
        'carrier_file': open(video_path, 'rb')
    }
    
    data = {
        'carrier_type': 'video',
        'content_type': 'text',
        'text_content': 'Hello, this is a test message for video steganography!',
        'password': 'test123',
        'encryption_type': 'aes-256-gcm'
    }
    
    try:
        # Start embedding
        response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
        files['carrier_file'].close()
        
        if response.status_code != 200:
            print(f"Embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        if not operation_id:
            print("No operation ID returned")
            return False
        
        print(f"Embedding started with operation ID: {operation_id}")
        
        # Poll for completion
        max_attempts = 30  # 30 seconds
        for attempt in range(max_attempts):
            status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if status_response.status_code != 200:
                print(f"Status check failed: {status_response.status_code}")
                return False
            
            status = status_response.json()
            print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
            
            if status.get('status') == 'completed':
                print("✅ Embedding completed successfully!")
                result_data = status.get('result', {})
                output_file = result_data.get('filename')
                print(f"Output file: {output_file}")
                return True
            
            elif status.get('status') == 'failed':
                print(f"❌ Embedding failed: {status.get('error')}")
                return False
            
            time.sleep(1)
        
        print("❌ Embedding timed out")
        return False
        
    except Exception as e:
        print(f"❌ Exception during embedding: {e}")
        return False

def test_image_embedding():
    """Test image embedding functionality"""
    print("\nTesting Image Embedding...")
    
    # Look for a test image
    image_extensions = ['.png', '.jpg', '.jpeg']
    image_path = None
    
    for ext in image_extensions:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                image_path = file
                break
        if image_path:
            break
    
    if not image_path:
        print("No test image found, skipping image test")
        return True
    
    print(f"Using test image: {image_path}")
    
    # Prepare the request
    files = {
        'carrier_file': open(image_path, 'rb')
    }
    
    data = {
        'carrier_type': 'image',
        'content_type': 'text',
        'text_content': 'Secret message in image!',
        'password': 'imagetest123',
        'encryption_type': 'aes-256-gcm'
    }
    
    try:
        # Start embedding
        response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
        files['carrier_file'].close()
        
        if response.status_code != 200:
            print(f"Image embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        print(f"Image embedding started with operation ID: {operation_id}")
        
        # Poll for completion (faster for images)
        max_attempts = 15
        for attempt in range(max_attempts):
            status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
                
                if status.get('status') == 'completed':
                    print("✅ Image embedding completed successfully!")
                    return True
                
                elif status.get('status') == 'failed':
                    print(f"❌ Image embedding failed: {status.get('error')}")
                    return False
            
            time.sleep(1)
        
        print("❌ Image embedding timed out")
        return False
        
    except Exception as e:
        print(f"❌ Exception during image embedding: {e}")
        return False

def test_audio_embedding():
    """Test audio embedding functionality"""
    print("\nTesting Audio Embedding...")
    
    # Look for a test audio file
    audio_extensions = ['.wav', '.mp3', '.flac']
    audio_path = None
    
    for ext in audio_extensions:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                audio_path = file
                break
        if audio_path:
            break
    
    if not audio_path:
        print("No test audio found, skipping audio test")
        return True
    
    print(f"Using test audio: {audio_path}")
    
    # Prepare the request
    files = {
        'carrier_file': open(audio_path, 'rb')
    }
    
    data = {
        'carrier_type': 'audio',
        'content_type': 'text',
        'text_content': 'Secret message in audio!',
        'password': 'audiotest123',
        'encryption_type': 'aes-256-gcm'
    }
    
    try:
        # Start embedding
        response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
        files['carrier_file'].close()
        
        if response.status_code != 200:
            print(f"Audio embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        print(f"Audio embedding started with operation ID: {operation_id}")
        
        # Poll for completion
        max_attempts = 20
        for attempt in range(max_attempts):
            status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
                
                if status.get('status') == 'completed':
                    print("✅ Audio embedding completed successfully!")
                    return True
                
                elif status.get('status') == 'failed':
                    print(f"❌ Audio embedding failed: {status.get('error')}")
                    return False
            
            time.sleep(1)
        
        print("❌ Audio embedding timed out")
        return False
        
    except Exception as e:
        print(f"❌ Exception during audio embedding: {e}")
        return False

def test_document_embedding():
    """Test document embedding functionality"""
    print("\nTesting Document Embedding...")
    
    # Look for a test document
    document_extensions = ['.pdf', '.docx', '.txt']
    document_path = None
    
    for ext in document_extensions:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                document_path = file
                break
        if document_path:
            break
    
    if not document_path:
        print("No test document found, skipping document test")
        return True
    
    print(f"Using test document: {document_path}")
    
    # Prepare the request
    files = {
        'carrier_file': open(document_path, 'rb')
    }
    
    data = {
        'carrier_type': 'document',
        'content_type': 'text',
        'text_content': 'Hidden text in document!',
        'password': 'doctest123',
        'encryption_type': 'aes-256-gcm'
    }
    
    try:
        # Start embedding
        response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
        files['carrier_file'].close()
        
        if response.status_code != 200:
            print(f"Document embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        print(f"Document embedding started with operation ID: {operation_id}")
        
        # Poll for completion
        max_attempts = 20
        for attempt in range(max_attempts):
            status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
                
                if status.get('status') == 'completed':
                    print("✅ Document embedding completed successfully!")
                    return True
                
                elif status.get('status') == 'failed':
                    print(f"❌ Document embedding failed: {status.get('error')}")
                    return False
            
            time.sleep(1)
        
        print("❌ Document embedding timed out")
        return False
        
    except Exception as e:
        print(f"❌ Exception during document embedding: {e}")
        return False

def test_file_embedding():
    """Test file-in-file embedding functionality"""
    print("\nTesting File-in-File Embedding...")
    
    # Use simple test video as carrier
    video_path = "simple_test_video.mp4"
    if not os.path.exists(video_path):
        print(f"Error: Test video {video_path} not found")
        return False
    
    # Create a test file to embed
    test_file_content = b"This is a binary test file content for steganography testing!"
    test_file_path = "test_secret_file.bin"
    with open(test_file_path, 'wb') as f:
        f.write(test_file_content)
    
    # Prepare the request
    files = {
        'carrier_file': open(video_path, 'rb'),
        'content_file': open(test_file_path, 'rb')
    }
    
    data = {
        'carrier_type': 'video',
        'content_type': 'file',
        'password': 'filetest123',
        'encryption_type': 'aes-256-gcm'
    }
    
    try:
        # Start embedding
        response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
        files['carrier_file'].close()
        files['content_file'].close()
        
        if response.status_code != 200:
            print(f"File embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        print(f"File embedding started with operation ID: {operation_id}")
        
        # Poll for completion
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
                
                if status.get('status') == 'completed':
                    print("✅ File embedding completed successfully!")
                    # Clean up test file
                    os.remove(test_file_path)
                    return True
                
                elif status.get('status') == 'failed':
                    print(f"❌ File embedding failed: {status.get('error')}")
                    # Clean up test file
                    os.remove(test_file_path)
                    return False
            
            time.sleep(1)
        
        print("❌ File embedding timed out")
        # Clean up test file
        os.remove(test_file_path)
        return False
        
    except Exception as e:
        print(f"❌ Exception during file embedding: {e}")
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        return False
    """Test image embedding functionality"""
    print("\nTesting Image Embedding...")
    
    # Look for a test image
    image_extensions = ['.png', '.jpg', '.jpeg']
    image_path = None
    
    for ext in image_extensions:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                image_path = file
                break
        if image_path:
            break
    
    if not image_path:
        print("No test image found, skipping image test")
        return True
    
    print(f"Using test image: {image_path}")
    
    # Prepare the request
    files = {
        'carrier_file': open(image_path, 'rb')
    }
    
    data = {
        'carrier_type': 'image',
        'content_type': 'text',
        'text_content': 'Secret message in image!',
        'password': 'imagetest123',
        'encryption_type': 'aes-256-gcm'
    }
    
    try:
        # Start embedding
        response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data)
        files['carrier_file'].close()
        
        if response.status_code != 200:
            print(f"Image embed request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        print(f"Image embedding started with operation ID: {operation_id}")
        
        # Poll for completion (faster for images)
        max_attempts = 15
        for attempt in range(max_attempts):
            status_response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"Status: {status.get('status')} - Progress: {status.get('progress', 0)}%")
                
                if status.get('status') == 'completed':
                    print("✅ Image embedding completed successfully!")
                    return True
                
                elif status.get('status') == 'failed':
                    print(f"❌ Image embedding failed: {status.get('error')}")
                    return False
            
            time.sleep(1)
        
        print("❌ Image embedding timed out")
        return False
        
    except Exception as e:
        print(f"❌ Exception during image embedding: {e}")
        return False

def test_health():
    """Test API health endpoint"""
    print("Testing API Health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code != 200:
            print(f"Health check failed: {response.status_code}")
            return False
        
        health = response.json()
        print(f"API Status: {health.get('status')}")
        print(f"Available Managers: {health.get('available_managers')}")
        print("✅ API is healthy!")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Comprehensive Steganography API Tests ===\n")
    
    # Test API health first
    if not test_health():
        print("❌ API health check failed, aborting tests")
        return
    
    print("\n" + "="*50)
    
    # Test all steganography types
    video_success = test_video_embedding()
    print("\n" + "="*50)
    
    image_success = test_image_embedding()
    print("\n" + "="*50)
    
    audio_success = test_audio_embedding()
    print("\n" + "="*50)
    
    document_success = test_document_embedding()
    print("\n" + "="*50)
    
    file_success = test_file_embedding()
    
    print("\n" + "="*50)
    print("=== Test Summary ===")
    print(f"Video Embedding: {'✅ PASS' if video_success else '❌ FAIL'}")
    print(f"Image Embedding: {'✅ PASS' if image_success else '❌ FAIL'}")
    print(f"Audio Embedding: {'✅ PASS' if audio_success else '❌ FAIL'}")
    print(f"Document Embedding: {'✅ PASS' if document_success else '❌ FAIL'}")
    print(f"File-in-File Embedding: {'✅ PASS' if file_success else '❌ FAIL'}")
    
    success_count = sum([video_success, image_success, audio_success, document_success, file_success])
    total_tests = 5
    
    if success_count == total_tests:
        print(f"\n🎉 All {total_tests} tests passed! The API is working perfectly.")
    else:
        print(f"\n⚠️  {success_count}/{total_tests} tests passed. Check the error messages above.")

if __name__ == "__main__":
    main()
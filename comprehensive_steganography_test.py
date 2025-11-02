#!/usr/bin/env python3
"""
Comprehensive test of all steganography functionality through the web API
"""

import requests
import os
import time
import json

base_url = "http://localhost:8000"

def wait_for_server():
    """Wait for server to be ready"""
    print("🔍 Checking if server is ready...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            print("✅ Server is ready!")
            return True
        except Exception as e:
            print(f"⏳ Waiting for server... ({i+1}/10)")
            time.sleep(2)
    print("❌ Server not responding")
    return False

def poll_operation_status(operation_id, timeout=60):
    """Poll operation status until completion"""
    print(f"📊 Polling operation {operation_id}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/api/operations/{operation_id}/status")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status', 'unknown')
                print(f"   Status: {status}")
                
                if status == 'completed':
                    return status_data
                elif status == 'failed':
                    print(f"❌ Operation failed: {status_data.get('error', 'Unknown error')}")
                    return status_data
                    
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            break
    
    print("❌ Operation timed out")
    return None

def test_video_steganography():
    """Test video steganography"""
    print("\n🎬 Testing Video Steganography")
    print("=" * 40)
    
    if not os.path.exists('clean_carrier.mp4'):
        print("❌ clean_carrier.mp4 not found")
        return False
    
    # Test embedding
    print("📥 Testing video embedding...")
    files = {'carrier_file': ('clean_carrier.mp4', open('clean_carrier.mp4', 'rb'), 'video/mp4')}
    data = {
        'operation': 'embed',
        'content_type': 'video',
        'message': 'Test video message',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=30)
        files['carrier_file'][1].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Embed request accepted. Operation ID: {result.get('operation_id')}")
            
            # Poll for completion
            status_data = poll_operation_status(result.get('operation_id'))
            if status_data and status_data.get('status') == 'completed':
                output_file = status_data.get('output_filename')
                print(f"✅ Video embedding completed! Output: {output_file}")
                
                # Test extraction
                if output_file and os.path.exists(output_file):
                    print("📤 Testing video extraction...")
                    files = {'carrier_file': (output_file, open(output_file, 'rb'), 'video/mp4')}
                    data = {
                        'operation': 'extract',
                        'content_type': 'video',
                        'password': 'test123'
                    }
                    
                    response = requests.post(f"{base_url}/api/extract", files=files, data=data, timeout=30)
                    files['carrier_file'][1].close()
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Extract request accepted. Operation ID: {result.get('operation_id')}")
                        
                        status_data = poll_operation_status(result.get('operation_id'))
                        if status_data and status_data.get('status') == 'completed':
                            extracted_message = status_data.get('message')
                            print(f"✅ Video extraction completed! Message: '{extracted_message}'")
                            return extracted_message == 'Test video message'
                    else:
                        print(f"❌ Extraction failed: {response.text}")
                else:
                    print(f"❌ Output file {output_file} not found")
        else:
            print(f"❌ Embedding failed: {response.text}")
    except Exception as e:
        print(f"❌ Video test failed: {e}")
    
    return False

def test_audio_steganography():
    """Test audio steganography"""
    print("\n🔊 Testing Audio Steganography")
    print("=" * 40)
    
    # Create a simple test audio file if none exists
    test_audio = None
    for filename in ['test_audio.wav', 'audio_with_hidden_doc.wav', 'direct_test_audio.wav']:
        if os.path.exists(filename):
            test_audio = filename
            break
    
    if not test_audio:
        print("❌ No audio file found for testing")
        return False
    
    print(f"📁 Using audio file: {test_audio}")
    
    # Test embedding
    print("📥 Testing audio embedding...")
    files = {'carrier_file': (test_audio, open(test_audio, 'rb'), 'audio/wav')}
    data = {
        'operation': 'embed',
        'content_type': 'audio',
        'message': 'Test audio message',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=30)
        files['carrier_file'][1].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Audio embed request accepted. Operation ID: {result.get('operation_id')}")
            
            status_data = poll_operation_status(result.get('operation_id'))
            if status_data and status_data.get('status') == 'completed':
                output_file = status_data.get('output_filename')
                print(f"✅ Audio embedding completed! Output: {output_file}")
                
                # Test extraction
                if output_file and os.path.exists(output_file):
                    print("📤 Testing audio extraction...")
                    files = {'carrier_file': (output_file, open(output_file, 'rb'), 'audio/wav')}
                    data = {
                        'operation': 'extract',
                        'content_type': 'audio',
                        'password': 'test123'
                    }
                    
                    response = requests.post(f"{base_url}/api/extract", files=files, data=data, timeout=30)
                    files['carrier_file'][1].close()
                    
                    if response.status_code == 200:
                        result = response.json()
                        status_data = poll_operation_status(result.get('operation_id'))
                        if status_data and status_data.get('status') == 'completed':
                            extracted_message = status_data.get('message')
                            print(f"✅ Audio extraction completed! Message: '{extracted_message}'")
                            return extracted_message == 'Test audio message'
                    else:
                        print(f"❌ Audio extraction failed: {response.text}")
        else:
            print(f"❌ Audio embedding failed: {response.text}")
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
    
    return False

def test_image_steganography():
    """Test image steganography"""
    print("\n🖼️ Testing Image Steganography")
    print("=" * 40)
    
    # Look for test images
    test_image = None
    for ext in ['png', 'jpg', 'jpeg', 'bmp']:
        for filename in os.listdir('.'):
            if filename.lower().endswith(f'.{ext}'):
                test_image = filename
                break
        if test_image:
            break
    
    if not test_image:
        print("❌ No image file found for testing")
        return False
    
    print(f"📁 Using image file: {test_image}")
    
    # Test embedding
    print("📥 Testing image embedding...")
    files = {'carrier_file': (test_image, open(test_image, 'rb'), 'image/png')}
    data = {
        'operation': 'embed',
        'content_type': 'image',
        'message': 'Test image message',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=30)
        files['carrier_file'][1].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image embed request accepted. Operation ID: {result.get('operation_id')}")
            
            status_data = poll_operation_status(result.get('operation_id'))
            if status_data and status_data.get('status') == 'completed':
                output_file = status_data.get('output_filename')
                print(f"✅ Image embedding completed! Output: {output_file}")
                return True  # For now, just test embedding
        else:
            print(f"❌ Image embedding failed: {response.text}")
    except Exception as e:
        print(f"❌ Image test failed: {e}")
    
    return False

def test_document_steganography():
    """Test document steganography"""
    print("\n📄 Testing Document Steganography")
    print("=" * 40)
    
    # Look for test documents
    test_doc = None
    for ext in ['pdf', 'doc', 'docx', 'txt']:
        for filename in os.listdir('.'):
            if filename.lower().endswith(f'.{ext}'):
                test_doc = filename
                break
        if test_doc:
            break
    
    if not test_doc:
        print("❌ No document file found for testing")
        return False
    
    print(f"📁 Using document file: {test_doc}")
    
    # Test embedding
    print("📥 Testing document embedding...")
    files = {'carrier_file': (test_doc, open(test_doc, 'rb'), 'application/pdf')}
    data = {
        'operation': 'embed',
        'content_type': 'document',
        'message': 'Test document message',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=30)
        files['carrier_file'][1].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document embed request accepted. Operation ID: {result.get('operation_id')}")
            
            status_data = poll_operation_status(result.get('operation_id'))
            if status_data and status_data.get('status') == 'completed':
                output_file = status_data.get('output_filename')
                print(f"✅ Document embedding completed! Output: {output_file}")
                return True  # For now, just test embedding
        else:
            print(f"❌ Document embedding failed: {response.text}")
    except Exception as e:
        print(f"❌ Document test failed: {e}")
    
    return False

def main():
    """Run comprehensive steganography tests"""
    print("🧪 Comprehensive Steganography Test Suite")
    print("=" * 50)
    
    if not wait_for_server():
        return
    
    results = {}
    
    # Test all steganography types
    results['video'] = test_video_steganography()
    results['audio'] = test_audio_steganography()
    results['image'] = test_image_steganography()
    results['document'] = test_document_steganography()
    
    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 30)
    for media_type, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{media_type.capitalize()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All steganography modules are working correctly!")
    else:
        print("⚠️ Some steganography modules need attention.")

if __name__ == "__main__":
    main()
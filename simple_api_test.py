#!/usr/bin/env python3
"""
Simple API test that doesn't import enhanced_app to avoid shutting down the server
"""

import requests
import os
import time

def test_server_health():
    """Test if server is responding"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_video_embedding():
    """Test video steganography embedding"""
    print("🎬 Testing Video Embedding...")
    
    if not os.path.exists('clean_carrier.mp4'):
        print("❌ clean_carrier.mp4 not found")
        return False
    
    files = {'carrier_file': ('clean_carrier.mp4', open('clean_carrier.mp4', 'rb'), 'video/mp4')}
    data = {
        'content_type': 'text',
        'text_content': 'Hello Video Test!',
        'password': 'test123'
    }
    
    try:
        response = requests.post("http://localhost:8000/api/embed", files=files, data=data, timeout=30)
        files['carrier_file'][1].close()
        
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Video embedding accepted!")
            print(f"Operation ID: {result.get('operation_id')}")
            print(f"Output file: {result.get('output_filename')}")
            return True
        else:
            print(f"❌ Video embedding failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_audio_embedding():
    """Test audio steganography embedding"""
    print("\n🔊 Testing Audio Embedding...")
    
    # Find an audio file
    audio_file = None
    for filename in ['audio_with_hidden_doc.wav', 'direct_test_audio.wav', 'test_audio.wav']:
        if os.path.exists(filename):
            audio_file = filename
            break
    
    if not audio_file:
        print("❌ No audio file found")
        return False
    
    print(f"Using audio file: {audio_file}")
    
    files = {'carrier_file': (audio_file, open(audio_file, 'rb'), 'audio/wav')}
    data = {
        'content_type': 'text', 
        'text_content': 'Hello Audio Test!',
        'password': 'test123'
    }
    
    try:
        response = requests.post("http://localhost:8000/api/embed", files=files, data=data, timeout=30)
        files['carrier_file'][1].close()
        
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Audio embedding accepted!")
            print(f"Operation ID: {result.get('operation_id')}")
            print(f"Output file: {result.get('output_filename')}")
            return True
        else:
            print(f"❌ Audio embedding failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_document_embedding():
    """Test document steganography embedding"""
    print("\n📄 Testing Document Embedding...")
    
    # Find a document file
    doc_file = None
    for filename in ['direct_test_document.doc', 'test.txt', 'README.md']:
        if os.path.exists(filename):
            doc_file = filename
            break
    
    if not doc_file:
        print("❌ No document file found")
        return False
    
    print(f"Using document file: {doc_file}")
    
    files = {'carrier_file': (doc_file, open(doc_file, 'rb'), 'application/octet-stream')}
    data = {
        'content_type': 'text',
        'text_content': 'Hello Document Test!',
        'password': 'test123'
    }
    
    try:
        response = requests.post("http://localhost:8000/api/embed", files=files, data=data, timeout=30)
        files['carrier_file'][1].close()
        
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document embedding accepted!")
            print(f"Operation ID: {result.get('operation_id')}")
            print(f"Output file: {result.get('output_filename')}")
            return True
        else:
            print(f"❌ Document embedding failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Simple Steganography API Test")
    print("=" * 40)
    
    # Check server health
    if not test_server_health():
        print("❌ Server is not responding")
        return
    
    print("✅ Server is healthy")
    
    # Test each steganography type
    results = []
    results.append(("Video", test_video_embedding()))
    results.append(("Audio", test_audio_embedding())) 
    results.append(("Document", test_document_embedding()))
    
    # Summary
    print("\n📊 Test Results:")
    print("=" * 20)
    for test_type, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_type}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
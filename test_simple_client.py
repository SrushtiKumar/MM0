#!/usr/bin/env python3
"""
Test client for the simple test server
"""

import requests
import os

def test_simple_server():
    base_url = "http://localhost:8001"
    
    # Test health
    print("🏥 Testing server health...")
    response = requests.get(f"{base_url}/api/health")
    print(f"Health Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    
    # Test video embedding
    print("\n🎬 Testing video endpoint...")
    if os.path.exists('clean_carrier.mp4'):
        files = {'carrier_file': ('clean_carrier.mp4', open('clean_carrier.mp4', 'rb'), 'video/mp4')}
        data = {
            'content_type': 'text',
            'text_content': 'Test message',
            'password': 'test123'
        }
        
        response = requests.post(f"{base_url}/api/test-embed", files=files, data=data)
        files['carrier_file'][1].close()
        
        print(f"Video Test Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    else:
        print("❌ clean_carrier.mp4 not found")
    
    # Test audio embedding
    print("\n🔊 Testing audio endpoint...")
    audio_file = None
    for filename in ['audio_with_hidden_doc.wav', 'direct_test_audio.wav']:
        if os.path.exists(filename):
            audio_file = filename
            break
    
    if audio_file:
        files = {'carrier_file': (audio_file, open(audio_file, 'rb'), 'audio/wav')}
        data = {
            'content_type': 'text',
            'text_content': 'Test audio message',
            'password': 'test123'
        }
        
        response = requests.post(f"{base_url}/api/test-embed", files=files, data=data)
        files['carrier_file'][1].close()
        
        print(f"Audio Test Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    else:
        print("❌ No audio file found")

if __name__ == "__main__":
    print("🧪 Testing Simple Steganography Server")
    print("=" * 40)
    test_simple_server()
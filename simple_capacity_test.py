#!/usr/bin/env python3
"""
Simple test to check audio capacity and image embedding
"""

import requests

# Test audio capacity
print("🎵 Testing Audio Capacity")
audio_file = "direct_test_audio.wav"

with open(audio_file, 'rb') as f:
    files = {'carrier_file': (audio_file, f, 'audio/wav')}
    data = {'password': 'test123', 'content_type': 'file', 'carrier_type': 'audio'}
    
    # Create tiny test file
    with open('tiny_test.txt', 'w') as tf:
        tf.write('hi')
    
    with open('tiny_test.txt', 'rb') as tf:
        files['content_file'] = ('tiny_test.txt', tf, 'text/plain')
        
        response = requests.post("http://localhost:8000/api/embed", data=data, files=files)
        print(f"Audio embed response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")

print("\n🖼️ Testing Image Capacity")            
image_file = "debug_embedded.png"

with open(image_file, 'rb') as f:
    files = {'carrier_file': (image_file, f, 'image/png')}
    data = {'password': 'test123', 'content_type': 'file', 'carrier_type': 'image'}
    
    with open('tiny_test.txt', 'rb') as tf:
        files['content_file'] = ('tiny_test.txt', tf, 'text/plain')
        
        response = requests.post("http://localhost:8000/api/embed", data=data, files=files)
        print(f"Image embed response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
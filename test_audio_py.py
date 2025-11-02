#!/usr/bin/env python3
"""
Test audio capacity and see if our metadata fix works
"""

import requests
import time

def test_audio_python_file():
    """Test embedding Python file in audio with new metadata format"""
    
    print("🎵 Testing Audio Python File Embedding")
    
    # Create test Python file
    py_content = "print('Hello from Python!')"
    with open('test_py_file.py', 'w') as f:
        f.write(py_content)
    
    audio_file = "direct_test_audio.wav"
    
    # Embed
    with open(audio_file, 'rb') as audio_f, open('test_py_file.py', 'rb') as py_f:
        data = {
            'password': 'test123',
            'content_type': 'file', 
            'carrier_type': 'audio'
        }
        files = {
            'carrier_file': (audio_file, audio_f),
            'content_file': ('test_py_file.py', py_f)
        }
        
        response = requests.post("http://localhost:8000/api/embed", data=data, files=files)
        print(f"Embed response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            operation_id = result['operation_id']
            print(f"Operation ID: {operation_id}")
            
            # Wait and check status
            for i in range(10):
                time.sleep(1)
                status_resp = requests.get(f"http://localhost:8000/api/operations/{operation_id}/status")
                if status_resp.status_code == 200:
                    status = status_resp.json()
                    print(f"Status: {status['status']}")
                    if status['status'] == 'completed':
                        print("✅ Embedding completed!")
                        break
                    elif status['status'] == 'failed':
                        error = status.get('error', 'Unknown error')
                        print(f"❌ Embedding failed: {error}")
                        break
        else:
            print(f"❌ Request failed: {response.text}")

if __name__ == "__main__":
    test_audio_python_file()
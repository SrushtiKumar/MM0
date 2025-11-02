#!/usr/bin/env python3
"""
Quick test for audio steganography only
"""

import requests
import time

SERVER_URL = "http://localhost:8000"

def test_audio_only():
    print("=== Testing Audio Steganography ===")
    
    audio_path = "C:\\Users\\Administrator\\Documents\\Git\\vF\\direct_test_audio.wav"
    secret_text = "Hi!"
    password = "test123"
    
    # Test embedding
    with open(audio_path, 'rb') as f:
        files = {'carrier_file': ('test.wav', f, 'audio/wav')}
        data = {
            'text_content': secret_text,
            'content_type': 'text',
            'password': password
        }
        
        response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
        print(f"Embed response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return
            
        result = response.json()
        operation_id = result.get('operation_id')
        print(f"Operation ID: {operation_id}")
        
        # Wait for completion
        while True:
            status_response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status')
                error = status_data.get('error')
                
                print(f"Status: {status}")
                if error:
                    print(f"Error: {error}")
                
                if status == 'completed':
                    print("✅ Audio embedding completed!")
                    break
                elif status == 'failed':
                    print("❌ Audio embedding failed!")
                    return
                    
            time.sleep(2)

if __name__ == "__main__":
    test_audio_only()
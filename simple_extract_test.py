#!/usr/bin/env python3
"""Simple test for the extract endpoint"""

import requests
import time

def test_extract():
    try:
        print("Testing /api/extract endpoint...")
        
        # Create a simple test file
        with open('simple_test.txt', 'w') as f:
            f.write("test content")
        
        # Test the extract endpoint
        with open('debug_video_with_mp3.mp4', 'rb') as f:
            files = {'stego_file': f}
            data = {
                'password': 'test123',
                'output_format': 'file'
            }
            
            response = requests.post('http://localhost:8000/api/extract', files=files, data=data, timeout=30)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return True
            
    except Exception as e:
        print(f"Extract test failed: {e}")
        return False

if __name__ == "__main__":
    test_extract()
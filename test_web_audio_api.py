#!/usr/bin/env python3
"""
Test audio password via web API
"""

import requests
import json

print("Testing audio with wrong password via web API...")

with open('debug_stego.wav', 'rb') as f:
    files = {'container_file': ('test.wav', f, 'audio/wav')}
    data = {'request_data': json.dumps({'password': 'WRONG_PASSWORD'})}
    r = requests.post('http://localhost:8000/api/extract', files=files, data=data)

print(f'Response: {r.status_code} - {r.json()}')

# Check job status
if r.status_code == 200:
    job_id = r.json()['job_id']
    print(f"Job ID: {job_id}")
    
    # Wait and check status
    import time
    while True:
        status_r = requests.get(f'http://localhost:8000/api/job/{job_id}')
        status = status_r.json()
        print(f"Status: {status}")
        
        if status['status'] in ['completed', 'failed']:
            break
        time.sleep(1)
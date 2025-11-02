#!/usr/bin/env python3

import requests
from PIL import Image
import numpy as np
import os

# Create test PNG
print("Creating test PNG...")
img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype='uint8'), 'RGB')
img.save('temp_test.png', 'PNG')
print("✅ Test PNG created")

# Create test text  
print("Creating test text file...")
with open('temp_test.txt', 'w') as f:
    f.write('Secret message test!')
print("✅ Test text file created")

# Test API
print("Testing API embedding...")
try:
    with open('temp_test.png', 'rb') as pf, open('temp_test.txt', 'rb') as tf:
        response = requests.post('http://localhost:8000/api/embed', 
            files={
                'carrier_file': pf, 
                'content_file': tf
            },
            data={
                'content_type': 'document',
                'password': 'test123'
            })
    
    if response.status_code == 200:
        print("✅ API embedding successful")
        
        # Parse the JSON response to get operation ID
        response_data = response.json()
        operation_id = response_data.get('operation_id')
        print(f"� Operation ID: {operation_id}")
        
        # Wait a moment for processing
        import time
        time.sleep(2)
        
        # Download the actual result file
        print("� Downloading processed image...")
        download_response = requests.get(f'http://localhost:8000/api/operations/{operation_id}/download')
        
        if download_response.status_code == 200:
            print("✅ Download successful")
            
            with open('output_test.png', 'wb') as f:
                f.write(download_response.content)
            
            # Try to open the result - this is the critical test!
            print("🧪 Testing if processed PNG can be opened...")
            try:
                result_img = Image.open('output_test.png')
                print('🎉 SUCCESS: PNG can be opened after steganography!')
                print(f'📐 Size: {result_img.size}, Mode: {result_img.mode}')
                print("✅ IMAGE CORRUPTION IS FIXED!")
            except Exception as img_error:
                print(f'❌ PNG is corrupted: {img_error}')
        else:
            print(f'❌ Download failed: {download_response.status_code} - {download_response.text}')
    else:
        print(f'❌ API Error: {response.status_code} - {response.text}')
        
except Exception as e:
    print(f'❌ Test failed: {e}')

# Cleanup
print("Cleaning up...")
for f in ['temp_test.png', 'temp_test.txt', 'output_test.png']:
    try: 
        os.remove(f)
    except: 
        pass

print("Test completed!")
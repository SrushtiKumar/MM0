import requests
import time
import os

SERVER_URL = 'http://localhost:8000'

def wait_for_operation(operation_id):
    for i in range(30):
        response = requests.get(f'{SERVER_URL}/api/operations/{operation_id}/status')
        if response.status_code == 200:
            status = response.json()
            if status['status'] == 'completed':
                return True
            elif status['status'] == 'failed':
                print(f'Operation failed: {status.get("error", "Unknown error")}')
                return False
        time.sleep(1)
    return False

# Test document steganography
doc_path = 'large_test_document.doc'
if not os.path.exists(doc_path):
    print(f'Document file {doc_path} not found')
    exit(1)

print(f'Testing document: {doc_path} (size: {os.path.getsize(doc_path)} bytes)')

# Step 1: Embed
secret_data = 'Hi!'
with open(doc_path, 'rb') as f:
    files = {'carrier_file': ('test_document.doc', f, 'application/msword')}
    data = {
        'text_content': secret_data,
        'content_type': 'text',
        'password': 'test123'
    }
    
    response = requests.post(f'{SERVER_URL}/api/embed', files=files, data=data)
    print(f'Embed response status: {response.status_code}')
    
    if response.status_code != 200:
        print(f'Embed failed: {response.text}')
        exit(1)
        
    embed_result = response.json()
    embed_operation_id = embed_result.get('operation_id')
    print(f'Embed operation ID: {embed_operation_id}')

if wait_for_operation(embed_operation_id):
    print('✅ Document embedding successful')
else:
    print('❌ Document embedding failed')
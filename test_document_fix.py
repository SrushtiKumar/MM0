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
doc_path = 'large_test_document.txt'
secret_data = 'Hi!'

print(f'Testing document: {doc_path}')

# Embed
with open(doc_path, 'rb') as f:
    files = {'carrier_file': ('test_document.txt', f, 'text/plain')}
    data = {
        'text_content': secret_data,
        'content_type': 'text',
        'password': 'test123'
    }
    
    response = requests.post(f'{SERVER_URL}/api/embed', files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        if wait_for_operation(result['operation_id']):
            print('✅ Document embedding successful')
            
            # Download embedded file
            download_response = requests.get(f'{SERVER_URL}/api/operations/{result["operation_id"]}/download')
            if download_response.status_code == 200:
                with open('test_embedded_doc.txt', 'wb') as f:
                    f.write(download_response.content)
                print('📄 Embedded file downloaded')
                
                # Extract
                with open('test_embedded_doc.txt', 'rb') as f:
                    files = {'stego_file': ('embedded_doc.txt', f, 'text/plain')}
                    data = {'password': 'test123', 'output_format': 'auto'}
                    
                    extract_response = requests.post(f'{SERVER_URL}/api/extract', files=files, data=data)
                    if extract_response.status_code == 200:
                        extract_result = extract_response.json()
                        if wait_for_operation(extract_result['operation_id']):
                            # Download extracted content
                            download_response = requests.get(f'{SERVER_URL}/api/operations/{extract_result["operation_id"]}/download')
                            if download_response.status_code == 200:
                                extracted_content = download_response.content.decode('utf-8')
                                print(f'Extracted: "{extracted_content}"')
                                if extracted_content == secret_data:
                                    print('✅ Document steganography PASSED')
                                else:
                                    print('❌ Content mismatch')
                            else:
                                print('❌ Extract download failed')
                        else:
                            print('❌ Extract operation failed')
                    else:
                        print(f'❌ Extract request failed: {extract_response.text}')
            else:
                print('❌ Embed download failed')
        else:
            print('❌ Embed operation failed')
    else:
        print(f'❌ Embed request failed: {response.text}')
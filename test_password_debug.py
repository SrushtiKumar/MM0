"""
Debug password mismatch issue between embed and extract
"""

import requests
import time
import os
import json

def test_password_debugging():
    """Test with explicit password debugging"""
    
    print("🔍 DEBUGGING PASSWORD MISMATCH ISSUE")
    print("=" * 50)
    
    test_image = "copyright_demo_file.png"
    test_password = "DebugPassword123!"
    test_data = {"test": "simple text data"}
    
    # Step 1: Embed with explicit password logging
    print(f"\n1️⃣ EMBEDDING with password: '{test_password}'")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'carrier_file': (test_image, f, 'image/png')}
            
            data = {
                'content_type': 'text',
                'text_content': json.dumps(test_data),
                'password': test_password,
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image'
            }
            
            print(f"Embed request data: {data}")
            embed_response = requests.post("http://localhost:8000/api/embed", files=files, data=data)
            
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code}")
            print(f"Error: {embed_response.text}")
            return False
            
        embed_result = embed_response.json()
        operation_id = embed_result.get('operation_id')
        print(f"✅ Embed started: {operation_id}")
        
        # Wait for completion
        embedded_file = None
        for attempt in range(10):
            time.sleep(1)
            
            status_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/status")
            status_data = status_response.json()
            
            if status_data.get('status') == 'completed':
                embedded_file = status_data.get('result', {}).get('output_file')
                print(f"✅ Embed completed: {embedded_file}")
                break
            elif status_data.get('status') == 'failed':
                print(f"❌ Embed failed: {status_data.get('error')}")
                return False
                
        if not embedded_file or not os.path.exists(embedded_file):
            print("❌ Embedded file not created")
            return False
        
        # Step 2: Extract with same password
        print(f"\n2️⃣ EXTRACTING with same password: '{test_password}'")
        
        with open(embedded_file, 'rb') as f:
            files = {'stego_file': (os.path.basename(embedded_file), f)}
            
            extract_data = {
                'password': test_password,
                'output_format': 'text'
            }
            
            print(f"Extract request data: {extract_data}")
            extract_response = requests.post("http://localhost:8000/api/extract", files=files, data=extract_data)
            
        if extract_response.status_code != 200:
            print(f"❌ Extract request failed: {extract_response.status_code}")
            print(f"Error: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_operation_id = extract_result.get('operation_id')
        print(f"✅ Extract started: {extract_operation_id}")
        
        # Monitor extraction
        for attempt in range(10):
            time.sleep(1)
            
            status_response = requests.get(f"http://localhost:8000/api/operations/{extract_operation_id}/status")
            status_data = status_response.json()
            current_status = status_data.get('status')
            
            print(f"  [{attempt + 1:2d}s] Status: {current_status}")
            
            if current_status == 'completed':
                result_data = status_data.get('result', {})
                extracted_text = result_data.get('text_content', '')
                
                print(f"✅ EXTRACTION SUCCESS!")
                print(f"📝 Extracted: {extracted_text}")
                
                # Verify content
                try:
                    extracted_data = json.loads(extracted_text)
                    if extracted_data.get('test') == test_data['test']:
                        print("✅ DATA VERIFIED CORRECTLY!")
                        return True
                    else:
                        print("❌ Data mismatch")
                        return False
                except json.JSONDecodeError:
                    print("❌ Not valid JSON")
                    return False
                    
            elif current_status == 'failed':
                error = status_data.get('error', 'Unknown error')
                print(f"❌ Extract failed: {error}")
                return False
        
        print("❌ Extract timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_password_debugging()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 PASSWORD TEST: SUCCESS!")
        print("✅ Password handling works correctly")
    else:
        print("💥 PASSWORD TEST: FAILED") 
        print("❌ Password or encryption issues remain")
    print("=" * 50)
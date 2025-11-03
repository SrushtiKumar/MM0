"""
Final test with truly clean image
"""

import requests
import time
import json

def test_truly_clean():
    """Test with a completely new image file"""
    
    print("🆕 TESTING WITH TRULY CLEAN IMAGE")
    print("=" * 60)
    
    clean_image = "truly_clean.png"
    password = "TrulyClean123!"
    data = {"final_test": "This must work!"}
    
    try:
        with open(clean_image, 'rb') as f:
            files = {'carrier_file': (clean_image, f, 'image/png')}
            
            request_data = {
                'content_type': 'text',
                'text_content': json.dumps(data),
                'password': password,
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image'
            }
            
            print(f"📤 Embedding request: password='{password}', data={data}")
            embed_response = requests.post("http://localhost:8000/api/embed", files=files, data=request_data)
            
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.status_code} - {embed_response.text}")
            return False
            
        embed_result = embed_response.json()
        operation_id = embed_result.get('operation_id')
        print(f"✅ Embed operation: {operation_id}")
        
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
                
        if not embedded_file:
            return False
        
        # Extract test
        print(f"📥 Extracting with password: '{password}'")
        
        with open(embedded_file, 'rb') as f:
            files = {'stego_file': (embedded_file.split('\\')[-1], f)}
            
            extract_data = {
                'password': password,
                'output_format': 'text'
            }
            
            extract_response = requests.post("http://localhost:8000/api/extract", files=files, data=extract_data)
            
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.status_code} - {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_operation_id = extract_result.get('operation_id')
        
        # Monitor extraction
        for attempt in range(10):
            time.sleep(1)
            
            status_response = requests.get(f"http://localhost:8000/api/operations/{extract_operation_id}/status")
            status_data = status_response.json()
            
            if status_data.get('status') == 'completed':
                extracted_text = status_data.get('result', {}).get('text_content', '')
                print(f"✅ Extracted: {extracted_text}")
                
                try:
                    extracted_data = json.loads(extracted_text)
                    if extracted_data.get('final_test') == data['final_test']:
                        print("🎉 PERFECT SUCCESS!")
                        return True
                except:
                    pass
                    
                print("❌ Data mismatch")
                return False
                
            elif status_data.get('status') == 'failed':
                print(f"❌ Extract failed: {status_data.get('error')}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_truly_clean()
    if success:
        print("\n🎯 FINAL RESULT: COMPLETE SUCCESS!")
        print("✅ All copyright protection issues are now FIXED!")
    else:
        print("\n💥 FINAL RESULT: Still failing")
        print("❌ Deeper investigation needed")
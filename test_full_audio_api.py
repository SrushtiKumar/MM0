"""
Test the enhanced_app.py API endpoint for audio steganography
"""
import requests
import json
import time

def test_audio_steganography_api():
    print("=== TESTING AUDIO STEGANOGRAPHY API ===")
    
    # API endpoint
    url = "http://localhost:8000/api/embed"
    
    # Prepare the test data using multipart/form-data
    files = {
        'carrier_file': ('enhanced_audio_test.wav', open('enhanced_audio_test.wav', 'rb'), 'audio/wav')
    }
    
    data = {
        'content_type': 'text',
        'text_content': 'Secret message via API - audio steganography test!',
        'password': 'test123',
        'carrier_type': 'audio',  # Explicitly specify audio
        'encryption_type': 'aes-256-gcm'
    }
    
    try:
        print("🔍 Sending request to /api/embed...")
        print(f"   - Carrier: enhanced_audio_test.wav")
        print(f"   - Content: {data['text_content']}")
        print(f"   - Password: {data['password']}")
        print(f"   - Carrier Type: {data['carrier_type']}")
        
        response = requests.post(url, files=files, data=data)
        
        print(f"\\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                operation_id = result.get('operation_id')
                print(f"\\n⏳ Operation ID: {operation_id}")
                
                # Check status until completion
                status_url = f"http://localhost:8000/api/operations/{operation_id}/status"
                
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    status_response = requests.get(status_url)
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        status = status_result.get('status')
                        message = status_result.get('message', '')
                        progress = status_result.get('progress', 0)
                        
                        print(f"   Status: {status} ({progress}%) - {message}")
                        
                        if status == 'completed':
                            print("\\n🎉 AUDIO STEGANOGRAPHY API TEST PASSED!")
                            
                            # Get output details
                            output_file = status_result.get('output_file')
                            details = status_result.get('details', {})
                            
                            print(f"   ✅ Output file: {output_file}")
                            print(f"   ✅ Details: {json.dumps(details, indent=4)}")
                            
                            # Test extraction
                            test_extraction(output_file, data['password'], data['text_content'])
                            
                            return True
                            
                        elif status == 'failed':
                            error_msg = status_result.get('error', 'Unknown error')
                            print(f"\\n❌ Operation failed: {error_msg}")
                            return False
                
                print("\\n⏰ Operation timed out")
                return False
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ API returned success=False: {error_msg}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        files['carrier_file'][1].close()

def test_extraction(output_file, password, expected_content):
    """Test extraction from the generated file"""
    print(f"\\n🔍 Testing extraction from {output_file}...")
    
    url = "http://localhost:8000/api/extract"
    
    try:
        files = {
            'carrier_file': (output_file, open(output_file, 'rb'), 'audio/wav')
        }
        
        data = {
            'password': password,
            'carrier_type': 'audio'
        }
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                operation_id = result.get('operation_id')
                
                # Wait for extraction to complete
                status_url = f"http://localhost:8000/api/operations/{operation_id}/status"
                
                for i in range(15):  # Wait up to 15 seconds
                    time.sleep(1)
                    status_response = requests.get(status_url)
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        status = status_result.get('status')
                        
                        if status == 'completed':
                            extracted_content = status_result.get('extracted_content')
                            print(f"   🔍 Extracted: '{extracted_content}'")
                            
                            if extracted_content == expected_content:
                                print("   ✅ EXTRACTION TEST PASSED!")
                            else:
                                print(f"   ❌ Content mismatch!")
                                print(f"      Expected: '{expected_content}'")
                                print(f"      Got: '{extracted_content}'")
                            break
                            
                        elif status == 'failed':
                            print(f"   ❌ Extraction failed: {status_result.get('error')}")
                            break
                else:
                    print("   ⏰ Extraction timed out")
            else:
                print(f"   ❌ Extraction API error: {result.get('error')}")
        else:
            print(f"   ❌ Extraction HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Extraction exception: {e}")
    finally:
        if 'files' in locals():
            files['carrier_file'][1].close()

if __name__ == "__main__":
    test_audio_steganography_api()
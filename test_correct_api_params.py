"""
Updated comprehensive steganography test with correct API parameters
"""

import requests
import os
import time

API_URL = "http://localhost:8000/api"

def test_steganography_with_correct_params():
    """Test all steganography types with correct API parameters"""
    print("🧪 COMPREHENSIVE TEST WITH CORRECT API PARAMETERS")
    print("=" * 60)
    
    test_cases = [
        {
            'type': 'image',
            'file': 'copyright_demo_file.png',
            'message': 'Corrected image steganography test'
        },
        {
            'type': 'audio', 
            'file': 'test_audio.wav',
            'message': 'Corrected audio steganography test'
        },
        {
            'type': 'video',
            'file': 'test_video.mp4',
            'message': 'Corrected video steganography test'
        },
        {
            'type': 'document',
            'file': 'simple_test.pdf', 
            'message': 'Corrected document steganography test'
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        carrier_type = test_case['type']
        test_file = test_case['file']
        message = test_case['message']
        
        print(f"\n🔍 Testing {carrier_type.upper()}...")
        
        if not os.path.exists(test_file):
            print(f"⚠️ File {test_file} not found - SKIPPING")
            results[carrier_type] = 'skipped'
            continue
        
        try:
            # Use correct API parameters
            with open(test_file, 'rb') as f:
                files = {'carrier_file': (test_file, f)}
                
                # Correct parameters as expected by the API
                data = {
                    'carrier_type': carrier_type,  # NOT content_type
                    'content_type': 'text',        # This specifies text vs file
                    'text_content': message,       # NOT message
                    'password': f'{carrier_type}123!',
                    'encryption_type': 'aes-256-gcm'
                }
                
                print(f"📤 Embedding with correct params...")
                response = requests.post(f"{API_URL}/embed", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get('operation_id')
                print(f"✅ Embed accepted: {operation_id}")
                
                # Poll with shorter timeout and more frequent checks
                print("⏳ Checking completion...")
                for attempt in range(10):  # 10 seconds max
                    time.sleep(1)
                    
                    try:
                        status_response = requests.get(f"{API_URL}/operations/{operation_id}/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            current_status = status_data.get('status')
                            
                            if current_status == 'completed':
                                print(f"✅ {carrier_type.title()} PASSED!")
                                results[carrier_type] = 'success'
                                break
                            elif current_status == 'failed':
                                error = status_data.get('error', 'Unknown error')
                                print(f"❌ {carrier_type.title()} failed: {error}")
                                results[carrier_type] = 'failed'
                                break
                        else:
                            print(f"❌ Status check failed: {status_response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ Status check error: {e}")
                        
                if carrier_type not in results:
                    print(f"⏰ {carrier_type.title()} timed out")
                    results[carrier_type] = 'timeout'
                    
            else:
                print(f"❌ Embed request failed: {response.status_code}")
                print(f"Error: {response.text}")
                results[carrier_type] = 'request_failed'
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            results[carrier_type] = 'error'
    
    # Final results
    print(f"\n📊 RESULTS SUMMARY")
    print("=" * 30)
    
    success_count = 0
    total_count = 0
    
    for carrier_type, result in results.items():
        if result == 'success':
            print(f"✅ {carrier_type.title()}: SUCCESS")
            success_count += 1
        elif result == 'skipped':
            print(f"⚠️ {carrier_type.title()}: SKIPPED")
        else:
            print(f"❌ {carrier_type.title()}: {result.upper()}")
        
        if result != 'skipped':
            total_count += 1
    
    print(f"\n📈 SCORE: {success_count}/{total_count} tests passed")
    
    if success_count == total_count and total_count > 0:
        print("🎉 ALL TESTS PASSED WITH CORRECT PARAMETERS!")
        return True
    else:
        print("⚠️ Some tests failed - check parameter compatibility")
        return False

if __name__ == "__main__":
    success = test_steganography_with_correct_params()
    print(f"\n{'✅ COMPREHENSIVE TEST: PASSED' if success else '❌ COMPREHENSIVE TEST: FAILED'}")
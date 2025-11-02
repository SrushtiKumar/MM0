"""
Test the audio steganography API endpoint
"""
import requests
import json

def test_audio_api():
    print("=== TESTING AUDIO STEGANOGRAPHY API ===")
    
    # API endpoint
    url = "http://localhost:8000/hide-audio"
    
    # Prepare the test data
    files = {
        'file': ('enhanced_audio_test.wav', open('enhanced_audio_test.wav', 'rb'), 'audio/wav')
    }
    
    data = {
        'content': 'Secret audio message via API!',
        'password': 'test123'
    }
    
    try:
        print("Sending request to API...")
        response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ AUDIO API TEST PASSED!")
                print(f"Output file: {result.get('output_file')}")
                print(f"Details: {result.get('details', {})}")
            else:
                print(f"❌ API returned success=False: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        files['file'][1].close()

if __name__ == "__main__":
    test_audio_api()
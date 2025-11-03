"""
Quick test to verify steganography manager initialization is fixed
"""

import requests
import os

API_URL = "http://localhost:8000/api"
TEST_IMAGE = "copyright_demo_file.png"

def test_quick_embedding():
    """Test that embedding now works without initialization errors"""
    print("🧪 Testing steganography manager initialization fix...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Test file {TEST_IMAGE} not found")
        return False
    
    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'carrier_file': (TEST_IMAGE, f, 'image/png')}
            
            data = {
                'content_type': 'text',
                'text_content': 'Quick initialization test',
                'password': 'TestInit123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image'
            }
            
            print("📤 Sending embed request...")
            response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        print(f"📨 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            operation_id = result.get('operation_id')
            print(f"✅ Embedding initiated successfully! Operation ID: {operation_id}")
            
            # Quick status check
            import time
            time.sleep(2)
            
            status_response = requests.get(f"{API_URL}/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                print(f"📊 Status after 2 seconds: {current_status}")
                
                if current_status == 'completed':
                    print("🎉 Operation completed quickly!")
                    return True
                elif current_status == 'processing':
                    print("⏳ Operation is processing (better than before)")
                    return True
                else:
                    print(f"⚠️ Unexpected status: {current_status}")
                    return False
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
        else:
            print(f"❌ Embedding failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_quick_embedding()
    print(f"\n{'✅ INITIALIZATION FIX: SUCCESS' if success else '❌ INITIALIZATION FIX: FAILED'}")
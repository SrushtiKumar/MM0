"""
Frontend Copyright Page UI Test Script
This will simulate user interactions to test if the copyright page UI is functioning properly
"""

import requests
import json
import os
import time
from pathlib import Path

# Test configuration  
FRONTEND_URL = "http://localhost:8080"
API_URL = "http://localhost:8080/api"  # Through frontend proxy
TEST_IMAGE = "copyright_demo_file.png"

def test_frontend_api_connection():
    """Test if the frontend can successfully call the API through the proxy"""
    print("🔗 Testing frontend API connection...")
    
    try:
        # Test supported formats endpoint through frontend proxy
        response = requests.get(f"{API_URL}/supported-formats")
        
        if response.status_code == 200:
            formats = response.json()
            print("✅ Frontend API connection successful!")
            print("📋 Formats received through proxy:")
            
            # Verify format structure
            required_types = ['image', 'video', 'audio', 'document']
            for fmt_type in required_types:
                if fmt_type in formats:
                    carrier_formats = formats[fmt_type].get('carrier_formats', [])
                    print(f"  {fmt_type}: {len(carrier_formats)} formats ({', '.join(carrier_formats[:3])}...)")
                else:
                    print(f"  ❌ Missing {fmt_type} formats")
                    return False
            return True
        else:
            print(f"❌ Frontend API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing frontend API: {e}")
        return False

def test_copyright_embed_via_frontend():
    """Test copyright embedding through the frontend API proxy"""
    print("\n🧪 Testing copyright embedding via frontend...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Test image {TEST_IMAGE} not found")
        return False
        
    try:
        # Prepare copyright data
        copyright_data = {
            "author_name": "UI Test Author",
            "copyright_alias": "UIT_2024", 
            "timestamp": "2024-11-03T14:00:00Z"
        }
        
        # Prepare request exactly as the frontend would
        with open(TEST_IMAGE, 'rb') as f:
            files = {
                'carrier_file': (TEST_IMAGE, f, 'image/png')
            }
            
            data = {
                'content_type': 'text',
                'text_content': json.dumps(copyright_data),
                'password': 'UITest123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image',
                'project_name': 'Frontend UI Test'
            }
            
            print("📤 Sending embed request through frontend proxy...")
            response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        print(f"📨 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Copyright embedding via frontend successful!")
            print(f"🆔 Operation ID: {result.get('operation_id')}")
            return True, result.get('operation_id')
        else:
            print(f"❌ Frontend embedding failed: {response.status_code}")
            print(f"Error response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error during frontend embedding: {e}")
        return False, None

def check_operation_via_frontend(operation_id):
    """Check operation status through frontend proxy"""
    print(f"\n📊 Checking operation status via frontend: {operation_id}")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_URL}/operations/{operation_id}/status")
            
            if response.status_code == 200:
                status = response.json()
                current_status = status.get('status', 'unknown')
                progress = status.get('progress', 0)
                
                print(f"🔄 Attempt {attempt + 1}: Status = {current_status}, Progress = {progress}%")
                
                if current_status == 'completed':
                    print("✅ Operation completed successfully via frontend!")
                    result = status.get('result', {})
                    print(f"📁 Output file: {result.get('output_filename', 'N/A')}")
                    return True, result
                elif current_status == 'failed':
                    print(f"❌ Operation failed: {status.get('error', 'Unknown error')}")
                    return False, status
                    
                time.sleep(1)  # Wait 1 second before next check
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            time.sleep(1)
            
    print("⏱️ Operation timed out")
    return False, None

def main():
    """Run complete frontend UI test suite"""
    print("🚀 FRONTEND COPYRIGHT PAGE UI TESTS")
    print("=" * 50)
    
    # Test 1: Frontend API Connection
    api_ok = test_frontend_api_connection()
    
    if not api_ok:
        print("\n💥 CRITICAL: Frontend cannot connect to API")
        print("❌ This explains why the copyright page shows 'supported formats not loaded' error")
        return
    
    print("\n✅ Frontend API connection is working properly")
    
    # Test 2: Copyright Embedding via Frontend  
    embed_ok, operation_id = test_copyright_embed_via_frontend()
    
    if embed_ok and operation_id:
        # Test 3: Operation Status via Frontend
        status_ok, result = check_operation_via_frontend(operation_id)
        
        if status_ok:
            print("\n🎉 ALL FRONTEND TESTS PASSED!")
            print("✅ API Connection: Working")  
            print("✅ Copyright Embedding: Working")
            print("✅ Operation Tracking: Working")
            print("\n📢 The copyright page should be fully functional now!")
        else:
            print("\n⚠️ Embedding succeeded but operation tracking failed")
    else:
        print("\n💥 Frontend embedding failed")
        
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
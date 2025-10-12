"""
API Test Script for Enhanced Steganography Application
Tests all major API endpoints to ensure functionality
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_FILES_DIR = Path("test_files")

def create_test_files():
    """Create test files for API testing"""
    TEST_FILES_DIR.mkdir(exist_ok=True)
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open(TEST_FILES_DIR / "test_image.png", "wb") as f:
        f.write(test_image_data)
    
    # Create a test text file
    with open(TEST_FILES_DIR / "test_message.txt", "w") as f:
        f.write("This is a secret message for testing steganography!")
    
    print("✅ Test files created")

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Available managers: {data['available_managers']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_supported_formats():
    """Test the supported formats endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/supported-formats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Supported formats retrieved")
            for media_type, formats in data.items():
                print(f"   {media_type}: {formats['carrier_formats']}")
            return True
        else:
            print(f"❌ Supported formats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Supported formats error: {e}")
        return False

def test_password_generation():
    """Test password generation endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/generate-password?length=16&include_symbols=true", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Password generation works")
            print(f"   Generated password: {data['password']}")
            print(f"   Strength: {data['strength']}")
            return True
        else:
            print(f"❌ Password generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Password generation error: {e}")
        return False

def test_embed_operation():
    """Test the embed operation endpoint"""
    try:
        # Prepare files
        with open(TEST_FILES_DIR / "test_image.png", "rb") as carrier_file:
            files = {
                'carrier_file': ('test_image.png', carrier_file, 'image/png')
            }
            data = {
                'carrier_type': 'image',
                'content_type': 'text',
                'text_content': 'Secret test message',
                'password': 'TestPassword123!',
                'encryption_type': 'aes-256-gcm'
            }
            
            response = requests.post(f"{API_BASE_URL}/embed", files=files, data=data, timeout=10)
            
        if response.status_code == 200:
            result = response.json()
            print("✅ Embed operation started")
            print(f"   Operation ID: {result['operation_id']}")
            return result['operation_id']
        else:
            print(f"❌ Embed operation failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Embed operation error: {e}")
        return None

def test_operation_status(operation_id):
    """Test operation status endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/operations/{operation_id}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Operation status retrieved")
            print(f"   Status: {data['status']}")
            print(f"   Progress: {data.get('progress', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            return data
        else:
            print(f"❌ Operation status failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Operation status error: {e}")
        return None

def test_list_operations():
    """Test list operations endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/operations?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Operations list retrieved")
            print(f"   Total operations: {len(data['operations'])}")
            return True
        else:
            print(f"❌ Operations list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Operations list error: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🧪 Starting Enhanced Steganography API Tests")
    print("=" * 50)
    
    # Create test files
    create_test_files()
    
    # Test basic endpoints
    tests = [
        ("Health Check", test_health_check),
        ("Supported Formats", test_supported_formats),
        ("Password Generation", test_password_generation),
        ("List Operations", test_list_operations),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        results[test_name] = test_func()
    
    # Test embed operation (more complex)
    print(f"\n🔍 Testing Embed Operation...")
    operation_id = test_embed_operation()
    if operation_id:
        results["Embed Operation"] = True
        
        # Wait a bit and check status
        print(f"\n🔍 Testing Operation Status...")
        time.sleep(2)
        status_result = test_operation_status(operation_id)
        results["Operation Status"] = status_result is not None
    else:
        results["Embed Operation"] = False
        results["Operation Status"] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend server and dependencies.")
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(TEST_FILES_DIR)
        print("\n🧹 Test files cleaned up")
    except:
        pass
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
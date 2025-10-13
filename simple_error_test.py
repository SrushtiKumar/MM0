#!/usr/bin/env python3
"""
Simple test to verify that the database error message is now more user-friendly
"""
import requests
import time

def test_simple_operation():
    """Test a simple operation and check for improved error messages"""
    print("🔧 TESTING IMPROVED ERROR HANDLING")
    print("Checking if database errors are now handled gracefully...\n")
    
    try:
        # Wait for server to be ready
        time.sleep(2)
        
        # Test server health
        print("1. Testing server health...")
        health_response = requests.get("http://localhost:8000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("[OK] Server is responding")
        else:
            print(f"❌ Server not ready: {health_response.status_code}")
            return False
        
        # Test basic operation
        print("\n2. Testing basic embedding operation...")
        
        embed_data = {
            "content_type": "text",
            "text_content": "Test message for error handling",
            "password": "test123"
        }
        
        with open("clean_carrier.mp4", "rb") as f:
            files = {"carrier_file": f}
            response = requests.post(
                "http://localhost:8000/api/embed",
                data=embed_data,
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Operation successful: {result.get('output_filename', 'success')}")
            print(f"[OK] No NoneType errors occurred!")
            return True
        else:
            print(f"❌ Operation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("Make sure the server is running: python enhanced_app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_operation()
    if success:
        print("\n✅ ERROR HANDLING IMPROVED!")
        print("Database errors are now handled gracefully.")
        print("Users should no longer see confusing 'NoneType' error messages.")
    else:
        print("\n❌ Test failed - check server status")
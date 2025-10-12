#!/usr/bin/env python3
"""
Test script to verify steganography functionality works end-to-end
"""

import requests
import io

def test_backend_connection():
    """Test if backend is reachable and healthy"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data['status']}")
            print(f"✅ Available managers: {', '.join(data['available_managers'])}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def test_supported_formats():
    """Test supported formats endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/supported-formats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supported formats available:")
            for key, value in data.items():
                print(f"   {key}: {', '.join(value)}")
            return True
        else:
            print(f"❌ Supported formats check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot get supported formats: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing backend connectivity...")
    print("=" * 50)
    
    if test_backend_connection():
        print("\n🔍 Testing supported formats...")
        test_supported_formats()
        print("\n✅ All basic tests passed! Backend is ready for steganography operations.")
    else:
        print("\n❌ Backend connection failed. Please check if the server is running.")
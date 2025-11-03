#!/usr/bin/env python3
"""
Test script to verify copyright page functionality
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000/api"

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"✅ API Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Health failed: {e}")
        return False

def test_supported_formats():
    """Test supported formats endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/supported-formats")
        print(f"✅ Supported Formats: {response.status_code}")
        if response.status_code == 200:
            formats = response.json()
            print(f"   Image formats: {formats.get('image', [])}")
            print(f"   Audio formats: {formats.get('audio', [])}")
            print(f"   Video formats: {formats.get('video', [])}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Supported Formats failed: {e}")
        return False

def main():
    print("🔍 Testing Copyright Page API Endpoints...")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("❌ API is not running or not accessible")
        return
    
    # Test supported formats
    if not test_supported_formats():
        print("❌ Supported formats endpoint failed")
        return
    
    print("\n✅ All API endpoints are working correctly!")
    print("✅ Copyright page should be functional")
    print("\n📝 Manual test checklist:")
    print("  1. Visit http://localhost:8080/copyright")
    print("  2. Check that 3 tabs are visible: Embed, Extract, Project Settings")
    print("  3. Test password generation and visibility toggle")
    print("  4. Verify encryption type is not shown to user")
    print("  5. Test copyright information embedding and extraction")

if __name__ == "__main__":
    main()
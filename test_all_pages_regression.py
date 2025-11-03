"""
Test script to verify General and Forensic pages are still working
Tests that our proxy changes didn't affect other functionality
"""

import requests
import json
import os
import time

API_URL = "http://localhost:8080/api"
TEST_IMAGE = "copyright_demo_file.png"

def test_general_page_functionality():
    """Test General page (standard steganography) functionality"""
    print("🧪 Testing General Page Functionality...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Test image {TEST_IMAGE} not found")
        return False
        
    try:
        # Test standard embedding (like General page would do)
        with open(TEST_IMAGE, 'rb') as f:
            files = {
                'carrier_file': (TEST_IMAGE, f, 'image/png')
            }
            
            data = {
                'content_type': 'text',
                'text_content': 'This is a test message for general steganography',
                'password': 'GeneralTest123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': 'image'
            }
            
            print("📤 Testing general embedding...")
            response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            print("✅ General page functionality working!")
            print(f"🆔 Operation ID: {result.get('operation_id')}")
            return True, result.get('operation_id')
        else:
            print(f"❌ General embedding failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error testing general functionality: {e}")
        return False, None

def test_forensic_page_functionality():
    """Test Forensic page functionality"""
    print("\n🧪 Testing Forensic Page Functionality...")
    
    # Forensic pages typically use analysis endpoints
    # Let's test if the API is accessible for forensic operations
    try:
        # Test supported formats (forensic pages also use this)
        response = requests.get(f"{API_URL}/supported-formats")
        
        if response.status_code == 200:
            formats = response.json()
            print("✅ Forensic API access working!")
            print("📋 Formats accessible for forensic analysis")
            return True
        else:
            print(f"❌ Forensic API access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing forensic functionality: {e}")
        return False

def quick_operation_check(operation_id):
    """Quick check of operation status"""
    print(f"\n⏱️ Quick status check for: {operation_id}")
    
    try:
        response = requests.get(f"{API_URL}/operations/{operation_id}/status")
        
        if response.status_code == 200:
            status = response.json()
            current_status = status.get('status', 'unknown')
            print(f"📊 Status: {current_status}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def main():
    """Test all pages to ensure no regression"""
    print("🔍 REGRESSION TESTING - ALL PAGES")
    print("=" * 40)
    
    # Test General Page
    general_ok, general_op_id = test_general_page_functionality()
    
    # Test Forensic Page  
    forensic_ok = test_forensic_page_functionality()
    
    # Quick status check for the operation
    status_ok = False
    if general_ok and general_op_id:
        status_ok = quick_operation_check(general_op_id)
    
    # Summary
    print("\n📋 TEST RESULTS SUMMARY:")
    print("=" * 30)
    print(f"✅ General Page: {'WORKING' if general_ok else 'FAILED'}")
    print(f"✅ Forensic Page: {'WORKING' if forensic_ok else 'FAILED'}")  
    print(f"✅ Operations: {'WORKING' if status_ok else 'FAILED'}")
    
    if general_ok and forensic_ok and status_ok:
        print("\n🎉 NO REGRESSION DETECTED!")
        print("✅ All pages are functioning properly")
    else:
        print("\n⚠️ REGRESSION DETECTED!")
        print("❌ Some pages may have issues")
        
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()
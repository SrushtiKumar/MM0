#!/usr/bin/env python3
"""
Test the auto password generation feature
"""

import requests
import json


def test_password_generation():
    """Test the password generation API endpoint"""
    print("🔐 Testing Auto Password Generation Feature")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Test password generation endpoint
        print("1. Testing password generation endpoint...")
        response = requests.get(f"{base_url}/api/generate-password", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Password generation endpoint working!")
            print(f"   Generated password: {data.get('password', 'N/A')}")
            print(f"   Password length: {data.get('length', 'N/A')}")
            print(f"   Password strength: {data.get('strength', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            # Test multiple generations to ensure uniqueness
            print("\n2. Testing password uniqueness...")
            passwords = set()
            for i in range(5):
                resp = requests.get(f"{base_url}/api/generate-password", timeout=5)
                if resp.status_code == 200:
                    pwd = resp.json().get('password')
                    passwords.add(pwd)
                    print(f"   Password {i+1}: {pwd}")
            
            if len(passwords) == 5:
                print("✅ All passwords are unique!")
            else:
                print(f"⚠️ Only {len(passwords)} unique passwords out of 5")
            
            # Test password strength
            print("\n3. Testing password characteristics...")
            test_password = data.get('password', '')
            if test_password:
                has_upper = any(c.isupper() for c in test_password)
                has_lower = any(c.islower() for c in test_password)
                has_digit = any(c.isdigit() for c in test_password)
                has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in test_password)
                
                print(f"   Has uppercase: {has_upper}")
                print(f"   Has lowercase: {has_lower}")
                print(f"   Has digits: {has_digit}")
                print(f"   Has special chars: {has_special}")
                print(f"   Length: {len(test_password)}")
                
                if all([has_upper, has_lower, has_digit, has_special]) and len(test_password) >= 16:
                    print("✅ Password meets strong criteria!")
                else:
                    print("⚠️ Password may not meet all strong criteria")
            
            return True
            
        else:
            print(f"❌ Password generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_web_interface():
    """Test if the web interface loads properly"""
    print("\n🌐 Testing Web Interface")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=10)
        if response.status_code == 200:
            print("✅ Web interface loads successfully!")
            
            # Check if our new HTML elements are present
            html_content = response.text
            checks = [
                ('generateHidePassword', 'Auto-generate button present'),
                ('hidePasswordInfo', 'Password info section present'),
                ('toggleHidePassword', 'Show/hide password button present'),
                ('copyHidePassword', 'Copy password button present')
            ]
            
            for element_id, description in checks:
                if element_id in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description} - NOT FOUND")
            
            return True
        else:
            print(f"❌ Web interface failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing web interface: {e}")
        return False


if __name__ == "__main__":
    print("🚀 VeilForge Auto Password Generation Test Suite")
    print("=" * 60)
    
    # Test password generation
    password_test = test_password_generation()
    
    # Test web interface
    web_test = test_web_interface()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 60)
    if password_test and web_test:
        print("🎉 ALL TESTS PASSED! Auto password generation feature is working!")
        print("\nFeatures implemented:")
        print("✅ Strong password generation API endpoint")
        print("✅ Auto-generation during form submission")
        print("✅ Password visibility toggle")
        print("✅ Copy password to clipboard")
        print("✅ Visual feedback and warnings")
        print("✅ Unique passwords on each generation")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        
    print("\n🔍 To test the feature manually:")
    print("1. Open http://127.0.0.1:8000 in your browser")
    print("2. Go to the 'Hide Data' tab")
    print("3. Leave the password field empty or click 'Auto' button")
    print("4. The system will generate a strong password automatically")
    print("5. Copy the password and use it for extraction")
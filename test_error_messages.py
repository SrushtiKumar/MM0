"""
Test User-Friendly Error Messages
Creates scenarios that will definitely trigger errors to test message translation
"""
import requests
import json
import os
from PIL import Image

def test_error_messages():
    print("🔧 TESTING USER-FRIENDLY ERROR MESSAGES")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Create a very small image and try to embed large content
    print("\n1. Testing capacity error message...")
    try:
        # Create tiny 10x10 pixel image
        tiny_img = Image.new('RGB', (10, 10), color='red')
        tiny_img.save('tiny_test.png')
        
        # Create large content that definitely won't fit
        large_content = "X" * 50000  # 50KB
        with open("large_content.txt", "w") as f:
            f.write(large_content)
        
        with open("tiny_test.png", "rb") as img, open("large_content.txt", "rb") as content:
            response = requests.post(f"{base_url}/api/embed", files={
                "carrier_file": img,
                "content_file": content
            }, data={
                "carrier_type": "image",
                "content_type": "file",
                "password": "test123"
            })
        
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('detail', 'Unknown error')
            print(f"Error message received: {error_msg}")
            
            # Check if message is user-friendly
            friendly_phrases = [
                'too small to hide this much data',
                'not enough space',
                'file is too large',
                'reduce the file size',
                'choose a larger carrier'
            ]
            
            if any(phrase in error_msg.lower() for phrase in friendly_phrases):
                print("✅ USER-FRIENDLY CAPACITY ERROR MESSAGE!")
            else:
                print(f"❌ Technical error message: {error_msg}")
        else:
            print("❌ Expected error but operation succeeded")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 2: Test wrong password error
    print("\n2. Testing wrong password error...")
    try:
        # First embed something
        with open("test_image.png", "rb") as img:
            with open("test_python_file.py", "rb") as py_file:
                embed_response = requests.post(f"{base_url}/api/embed", files={
                    "carrier_file": img,
                    "content_file": py_file
                }, data={
                    "carrier_type": "image", 
                    "content_type": "file",
                    "password": "correct_password"
                })
        
        if embed_response.status_code == 200:
            result = embed_response.json()
            stego_file = result.get('output_file')
            
            if stego_file and os.path.exists(stego_file):
                # Try to extract with wrong password
                with open(stego_file, "rb") as f:
                    extract_response = requests.post(f"{base_url}/api/extract", files={
                        "stego_file": f
                    }, data={
                        "carrier_type": "image",
                        "password": "wrong_password"
                    })
                
                if extract_response.status_code != 200:
                    error_data = extract_response.json()
                    error_msg = error_data.get('detail', 'Unknown error')
                    print(f"Password error message: {error_msg}")
                    
                    friendly_phrases = [
                        'incorrect password',
                        'wrong password',
                        'password is incorrect',
                        'check your password'
                    ]
                    
                    if any(phrase in error_msg.lower() for phrase in friendly_phrases):
                        print("✅ USER-FRIENDLY PASSWORD ERROR MESSAGE!")
                    else:
                        print(f"❌ Technical error message: {error_msg}")
                else:
                    print("❌ Expected password error but extraction succeeded")
    except Exception as e:
        print(f"❌ Password test error: {e}")
    
    # Test 3: Test unsupported file format  
    print("\n3. Testing unsupported format error...")
    try:
        # Create a fake unsupported file
        with open("fake_unsupported.xyz", "w") as f:
            f.write("This is an unsupported file format")
        
        with open("test_image.png", "rb") as img, open("fake_unsupported.xyz", "rb") as unsupported:
            response = requests.post(f"{base_url}/api/embed", files={
                "carrier_file": unsupported,  # Use unsupported as carrier
                "content_file": img
            }, data={
                "carrier_type": "unsupported_format",
                "content_type": "file",
                "password": "test123"
            })
        
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('detail', 'Unknown error')
            print(f"Format error message: {error_msg}")
            
            friendly_phrases = [
                'file format not supported',
                'unsupported format',
                'format is not supported',
                'please use a supported format'
            ]
            
            if any(phrase in error_msg.lower() for phrase in friendly_phrases):
                print("✅ USER-FRIENDLY FORMAT ERROR MESSAGE!")
            else:
                print(f"❌ Technical error message: {error_msg}")
        else:
            print("❌ Expected format error but operation succeeded")
            
    except Exception as e:
        print(f"❌ Format test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 ERROR MESSAGE TEST COMPLETE")
    print("All error messages should be user-friendly and actionable")
    print("=" * 50)

if __name__ == "__main__":
    test_error_messages()
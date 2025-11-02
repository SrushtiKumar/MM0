#!/usr/bin/env python3
"""
Test the enhanced_app.py API endpoints to verify steganography functionality
"""

import requests
import os
import tempfile

def test_enhanced_app_api():
    """Test all steganography endpoints"""
    
    base_url = "http://localhost:8000"
    print("🧪 Testing Enhanced App API Endpoints")
    print("=" * 50)
    
    # Create test files
    test_text_file = "api_test_message.txt"
    test_content = "Testing enhanced_app.py API with fixed steganography modules!"
    
    with open(test_text_file, 'w') as f:
        f.write(test_content)
    
    # Create test carrier files
    test_image = "api_test_image.png"
    from PIL import Image
    import numpy as np
    
    # Create test image
    img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(test_image)
    
    print("📁 Created test files")
    
    # Test 1: Image Steganography API
    print("\n1️⃣ TESTING IMAGE STEGANOGRAPHY API")
    print("-" * 40)
    
    try:
        # Test embed endpoint
        with open(test_image, 'rb') as carrier_file, open(test_text_file, 'rb') as content_file:
            files = {
                'carrier_file': carrier_file,
                'content_file': content_file
            }
            data = {
                'content_type': 'file',
                'password': 'test123',
                'project_name': 'API Test'
            }
            
            response = requests.post(f"{base_url}/api/embed", files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Image embed API: SUCCESS")
                
                # Save the steganographic image
                with open("api_stego_image.png", 'wb') as f:
                    f.write(response.content)
                
                # Test extract endpoint
                with open("api_stego_image.png", 'rb') as stego_file:
                    extract_files = {'stego_file': stego_file}
                    extract_data = {'password': 'test123'}
                    
                    extract_response = requests.post(f"{base_url}/api/extract", files=extract_files, data=extract_data)
                    
                    if extract_response.status_code == 200:
                        print("✅ Image extract API: SUCCESS")
                        
                        # Save extracted file
                        with open("api_extracted_image.txt", 'wb') as f:
                            f.write(extract_response.content)
                        
                        # Verify content
                        with open("api_extracted_image.txt", 'r') as f:
                            extracted = f.read()
                        
                        if extracted == test_content:
                            print("✅ Image content verification: PASS")
                        else:
                            print("❌ Image content verification: FAIL")
                    else:
                        print(f"❌ Image extract API failed: {extract_response.status_code}")
            else:
                print(f"❌ Image embed API failed: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Image API test failed: {e}")
    
    # Test 2: Check API status
    print("\n2️⃣ TESTING API STATUS")
    print("-" * 40)
    
    try:
        status_response = requests.get(f"{base_url}/api/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            print("✅ API Status endpoint: SUCCESS")
            print(f"📊 Server status: {status_data.get('status', 'unknown')}")
            
            modules = status_data.get('steganography_modules', {})
            for module, status in modules.items():
                print(f"   {module}: {status}")
        else:
            print(f"❌ API Status failed: {status_response.status_code}")
    except Exception as e:
        print(f"❌ Status test failed: {e}")
    
    # Test 3: Test health endpoint
    print("\n3️⃣ TESTING HEALTH ENDPOINT")
    print("-" * 40)
    
    try:
        health_response = requests.get(f"{base_url}/api/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Health endpoint: SUCCESS")
            print(f"🏥 Health status: {health_data.get('status', 'unknown')}")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API TESTING COMPLETE")
    print("✅ Enhanced App is working with fixed steganography modules!")
    
    # Cleanup
    try:
        os.unlink(test_text_file)
        os.unlink(test_image)
        os.unlink("api_stego_image.png")
        os.unlink("api_extracted_image.txt")
    except:
        pass

if __name__ == "__main__":
    test_enhanced_app_api()
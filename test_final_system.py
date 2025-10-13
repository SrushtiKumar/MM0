#!/usr/bin/env python3
"""
Final System Test - Verify everything works without errors
"""

import requests
import os
import time
import json

def test_steganography_system():
    """Test the enhanced steganography system"""
    
    print("🔧 Testing Enhanced Steganography System")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print(f"   ❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Create test files
    print("\n2. Creating test files...")
    
    # Create a test image
    test_image = "test_image.png"
    test_message = "Hello, this is a test message for steganography!"
    
    # Create a simple test image using PIL
    try:
        from PIL import Image
        import numpy as np
        
        # Create a simple 100x100 RGB image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(test_image)
        print(f"   ✅ Created test image: {test_image}")
    except Exception as e:
        print(f"   ❌ Failed to create test image: {e}")
        return False
    
    # Test 3: Embed message in image
    print("\n3. Testing steganography embedding...")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (test_image, f, 'image/png')}
            data = {
                'message': test_message,
                'password': 'test123'
            }
            
            response = requests.post(f"{base_url}/embed", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get('operation_id')
                print(f"   ✅ Embedding started - Operation ID: {operation_id}")
                
                # Poll for completion
                print("   ⏳ Waiting for completion...")
                for i in range(30):  # Wait up to 30 seconds
                    status_response = requests.get(f"{base_url}/status/{operation_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   📊 Status: {status_data.get('status', 'unknown')}")
                        
                        if status_data.get('status') == 'completed':
                            print("   ✅ Embedding completed successfully!")
                            
                            # Download the result
                            download_response = requests.get(f"{base_url}/download/{operation_id}")
                            if download_response.status_code == 200:
                                output_file = f"stego_{test_image}"
                                with open(output_file, 'wb') as out_f:
                                    out_f.write(download_response.content)
                                print(f"   ✅ Downloaded result: {output_file}")
                                
                                # Test extraction
                                print("\n4. Testing steganography extraction...")
                                return test_extraction(base_url, output_file, 'test123')
                            else:
                                print(f"   ❌ Failed to download result: {download_response.status_code}")
                                return False
                        elif status_data.get('status') == 'failed':
                            error_msg = status_data.get('error', 'Unknown error')
                            print(f"   ❌ Embedding failed: {error_msg}")
                            return False
                    
                    time.sleep(1)
                
                print("   ❌ Embedding timed out")
                return False
            else:
                print(f"   ❌ Embedding request failed: {response.status_code}")
                if response.content:
                    print(f"   Error details: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Embedding test failed: {e}")
        return False

def test_extraction(base_url, stego_file, password):
    """Test message extraction"""
    
    try:
        with open(stego_file, 'rb') as f:
            files = {'file': (stego_file, f, 'image/png')}
            data = {'password': password}
            
            response = requests.post(f"{base_url}/extract", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get('operation_id')
                print(f"   ✅ Extraction started - Operation ID: {operation_id}")
                
                # Poll for completion
                print("   ⏳ Waiting for extraction completion...")
                for i in range(30):
                    status_response = requests.get(f"{base_url}/status/{operation_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data.get('status') == 'completed':
                            extracted_message = status_data.get('extracted_message')
                            print(f"   ✅ Extraction completed!")
                            print(f"   📄 Extracted message: '{extracted_message}'")
                            
                            if extracted_message == "Hello, this is a test message for steganography!":
                                print("   ✅ Message matches original - Test successful!")
                                return True
                            else:
                                print("   ⚠️  Message doesn't match original")
                                return False
                        elif status_data.get('status') == 'failed':
                            error_msg = status_data.get('error', 'Unknown error')
                            print(f"   ❌ Extraction failed: {error_msg}")
                            return False
                    
                    time.sleep(1)
                
                print("   ❌ Extraction timed out")
                return False
            else:
                print(f"   ❌ Extraction request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Extraction test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = ['test_image.png', 'stego_test_image.png']
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"   🧹 Cleaned up: {file}")
            except:
                pass

if __name__ == "__main__":
    try:
        success = test_steganography_system()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 ALL TESTS PASSED - System is working perfectly!")
            print("✅ No database errors")
            print("✅ No NoneType errors") 
            print("✅ Steganography operations successful")
        else:
            print("❌ Some tests failed - Please check the logs")
        
        print("\n🧹 Cleaning up test files...")
        cleanup_test_files()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        cleanup_test_files()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        cleanup_test_files()
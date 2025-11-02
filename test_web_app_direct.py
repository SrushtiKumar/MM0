#!/usr/bin/env python3
"""
Direct test of the web application API to reproduce the exact issue
"""

import requests
import os
import time

def test_video_steganography_api():
    """Test the video steganography API endpoint"""
    
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    print("🔍 Checking if server is ready...")
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            print("✅ Server is ready!")
            break
        except Exception as e:
            print(f"⏳ Waiting for server... ({i+1}/5)")
            time.sleep(2)
    else:
        print("❌ Server not responding")
        return
    
    # Test with a clean carrier video
    test_video = "clean_carrier.mp4"
    if not os.path.exists(test_video):
        print(f"❌ Test video {test_video} not found")
        return
        
    print(f"\n🎬 Testing with {test_video}")
    
    # Test embedding
    print("\n📥 Testing EMBEDDING...")
    
    files = {
        'carrier_file': ('clean_carrier.mp4', open(test_video, 'rb'), 'video/mp4')
    }
    
    data = {
        'content_type': 'text',
        'text_content': 'Hello, this is a test message for video steganography!',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ EMBEDDING SUCCESS!")
            print(f"Result: {result}")
            
            # Save the output file
            if 'output_filename' in result:
                output_filename = result['output_filename']
                print(f"📁 Output file: {output_filename}")
                
                # Now test extraction
                print("\n📤 Testing EXTRACTION...")
                
                if os.path.exists(output_filename):
                    files = {
                        'stego_file': (output_filename, open(output_filename, 'rb'), 'video/mp4')
                    }
                    
                    data = {
                        'password': 'testpass123'
                    }
                    
                    response = requests.post(f"{base_url}/api/extract", files=files, data=data, timeout=30)
                    print(f"Extraction Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print("✅ EXTRACTION SUCCESS!")
                        print(f"Extracted message: {result.get('message', 'No message found')}")
                    else:
                        print("❌ EXTRACTION FAILED!")
                        print(f"Error: {response.text}")
                else:
                    print(f"❌ Output file {output_filename} not found")
            else:
                print("❌ No output filename in response")
        else:
            print("❌ EMBEDDING FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    finally:
        # Close any open files
        try:
            files['carrier_file'][1].close()
        except:
            pass

def test_with_larger_video():
    """Test with a larger video file that might be causing issues"""
    
    base_url = "http://localhost:8000"
    
    # Try with enhanced_web_test_video.mp4
    test_video = "enhanced_web_test_video.mp4"
    if not os.path.exists(test_video):
        print(f"❌ Test video {test_video} not found")
        return
        
    print(f"\n🎬 Testing with larger video: {test_video}")
    
    # Get video info first
    import cv2
    cap = cv2.VideoCapture(test_video)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    print(f"📊 Video info: {frames} frames, {fps} fps, {width}x{height}")
    
    # Test embedding
    print("\n📥 Testing EMBEDDING with larger video...")
    
    files = {
        'carrier_file': (test_video, open(test_video, 'rb'), 'video/mp4')
    }
    
    data = {
        'content_type': 'text',
        'text_content': 'Test message in larger video file.',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ EMBEDDING SUCCESS with larger video!")
            print(f"Result: {result}")
            
            # Test extraction
            if 'output_filename' in result:
                output_filename = result['output_filename']
                print(f"📁 Output file: {output_filename}")
                
                print("\n📤 Testing EXTRACTION from larger video...")
                
                if os.path.exists(output_filename):
                    files = {
                        'stego_file': (output_filename, open(output_filename, 'rb'), 'video/mp4')
                    }
                    
                    data = {
                        'password': 'testpass123'
                    }
                    
                    response = requests.post(f"{base_url}/api/extract", files=files, data=data, timeout=60)
                    print(f"Extraction Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print("✅ EXTRACTION SUCCESS from larger video!")
                        print(f"Extracted message: {result.get('message', 'No message found')}")
                    else:
                        print("❌ EXTRACTION FAILED from larger video!")
                        print(f"Error: {response.text}")
        else:
            print("❌ EMBEDDING FAILED with larger video!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed with larger video: {e}")
    finally:
        try:
            files['carrier_file'][1].close()
        except:
            pass

if __name__ == "__main__":
    print("🧪 Direct Web Application API Test")
    print("=" * 50)
    
    # Test with small video first
    test_video_steganography_api()
    
    # Test with larger video
    test_with_larger_video()
    
    print("\n🏁 Test completed!")
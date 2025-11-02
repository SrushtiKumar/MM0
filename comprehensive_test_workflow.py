#!/usr/bin/env python3
"""
Comprehensive test that reproduces the exact issue by testing the API with proper async handling
"""

import requests
import os
import time
import json

def poll_operation_status(base_url, operation_id, timeout=60):
    """Poll the operation status until completion or timeout"""
    
    start_time = time.time()
    print(f"⏳ Polling operation {operation_id}...")
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/api/operations/{operation_id}/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status', 'unknown')
                progress = status_data.get('progress', 0)
                message = status_data.get('message', '')
                
                print(f"   Status: {status} ({progress}%) - {message}")
                
                if status == 'completed':
                    print("✅ Operation completed successfully!")
                    return True, status_data
                elif status == 'failed' or status == 'error':
                    print(f"❌ Operation failed: {message}")
                    return False, status_data
                    
            time.sleep(2)  # Poll every 2 seconds
            
        except Exception as e:
            print(f"   Error polling status: {e}")
            time.sleep(2)
    
    print("⌛ Operation timed out")
    return False, None

def test_video_steganography_complete():
    """Test the complete video steganography workflow"""
    
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    print("🔍 Checking if server is ready...")
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except Exception as e:
            print(f"⏳ Waiting for server... ({i+1}/5)")
            time.sleep(2)
    else:
        print("❌ Server not responding")
        return False
    
    # Test with clean carrier video
    test_video = "clean_carrier.mp4"
    if not os.path.exists(test_video):
        print(f"❌ Test video {test_video} not found")
        return False
        
    print(f"\n🎬 Testing complete workflow with {test_video}")
    
    # Get video info
    import cv2
    cap = cv2.VideoCapture(test_video)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    print(f"📊 Video info: {frames} frames, {fps} fps, {width}x{height}")
    
    # Test embedding
    print(f"\n📥 Step 1: EMBEDDING message...")
    
    files = {
        'carrier_file': ('clean_carrier.mp4', open(test_video, 'rb'), 'video/mp4')
    }
    
    data = {
        'content_type': 'text',
        'text_content': 'Hello, this is a test message to verify video steganography is working correctly!',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ EMBEDDING request accepted!")
            operation_id = result.get('operation_id')
            expected_filename = result.get('output_filename')
            
            print(f"📋 Operation ID: {operation_id}")
            print(f"📁 Expected output: {expected_filename}")
            
            # Poll for completion
            success, status_data = poll_operation_status(base_url, operation_id)
            
            if success and expected_filename and os.path.exists(expected_filename):
                print(f"📁 Output file created: {expected_filename}")
                file_size = os.path.getsize(expected_filename)
                print(f"📏 File size: {file_size} bytes")
                
                # Now test extraction
                print(f"\n📤 Step 2: EXTRACTING message...")
                
                extract_files = {
                    'stego_file': (expected_filename, open(expected_filename, 'rb'), 'video/mp4')
                }
                
                extract_data = {
                    'password': 'testpass123'
                }
                
                response = requests.post(f"{base_url}/api/extract", files=extract_files, data=extract_data, timeout=30)
                print(f"Extraction Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    extract_result = response.json()
                    extract_operation_id = extract_result.get('operation_id')
                    
                    print(f"✅ EXTRACTION request accepted!")
                    print(f"📋 Extract Operation ID: {extract_operation_id}")
                    
                    # Poll for extraction completion
                    extract_success, extract_status_data = poll_operation_status(base_url, extract_operation_id)
                    
                    if extract_success:
                        # Check the final result
                        if 'data' in extract_status_data and extract_status_data['data']:
                            extracted_message = extract_status_data['data']
                            print(f"🎉 EXTRACTION SUCCESS!")
                            print(f"📝 Original message: {data['text_content']}")
                            print(f"📝 Extracted message: {extracted_message}")
                            
                            if extracted_message == data['text_content']:
                                print("✅ Messages match perfectly! Video steganography is working!")
                                return True
                            else:
                                print("❌ Messages don't match!")
                                return False
                        else:
                            print("❌ No extracted data found")
                            print(f"Status data: {json.dumps(extract_status_data, indent=2)}")
                            return False
                    else:
                        print("❌ Extraction failed!")
                        return False
                else:
                    print("❌ EXTRACTION request failed!")
                    print(f"Error: {response.text}")
                    return False
            else:
                print("❌ Embedding failed or output file not created!")
                if status_data:
                    print(f"Status data: {json.dumps(status_data, indent=2)}")
                return False
        else:
            print("❌ EMBEDDING request failed!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    finally:
        # Close any open files
        try:
            files['carrier_file'][1].close()
        except:
            pass
        try:
            extract_files['stego_file'][1].close()
        except:
            pass

def test_large_video_workflow():
    """Test with a larger video to see if it fails"""
    
    base_url = "http://localhost:8000"
    
    # Try with a larger video
    test_video = "enhanced_web_test_video.mp4"  # This was failing before
    if not os.path.exists(test_video):
        print(f"❌ Test video {test_video} not found")
        return False
        
    print(f"\n🎬 Testing with larger video: {test_video}")
    
    # Get video info
    import cv2
    cap = cv2.VideoCapture(test_video)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) 
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    print(f"📊 Video info: {frames} frames, {fps} fps, {width}x{height}")
    
    # Test embedding
    print(f"\n📥 Step 1: EMBEDDING in larger video...")
    
    files = {
        'carrier_file': (test_video, open(test_video, 'rb'), 'video/mp4')
    }
    
    data = {
        'content_type': 'text',
        'text_content': 'Testing with larger video file to see if extraction fails.',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/embed", files=files, data=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            operation_id = result.get('operation_id')
            expected_filename = result.get('output_filename')
            
            print(f"📋 Operation ID: {operation_id}")
            print(f"📁 Expected output: {expected_filename}")
            
            # Poll for completion
            success, status_data = poll_operation_status(base_url, operation_id)
            
            if success and expected_filename and os.path.exists(expected_filename):
                print(f"📁 Output file created: {expected_filename}")
                
                # Test extraction
                print(f"\n📤 Step 2: EXTRACTING from larger video...")
                
                extract_files = {
                    'stego_file': (expected_filename, open(expected_filename, 'rb'), 'video/mp4')
                }
                
                extract_data = {
                    'password': 'testpass123'
                }
                
                response = requests.post(f"{base_url}/api/extract", files=extract_files, data=extract_data, timeout=60)
                
                if response.status_code == 200:
                    extract_result = response.json()
                    extract_operation_id = extract_result.get('operation_id')
                    
                    print(f"✅ EXTRACTION request accepted!")
                    
                    # Poll for extraction completion
                    extract_success, extract_status_data = poll_operation_status(base_url, extract_operation_id, timeout=120)
                    
                    if extract_success:
                        if 'data' in extract_status_data and extract_status_data['data']:
                            extracted_message = extract_status_data['data']
                            print(f"🎉 LARGE VIDEO EXTRACTION SUCCESS!")
                            print(f"📝 Extracted: {extracted_message}")
                            return True
                        else:
                            print("❌ No extracted data from large video")
                            return False
                    else:
                        print("❌ Large video extraction failed!")
                        if extract_status_data:
                            error_msg = extract_status_data.get('message', 'Unknown error')
                            print(f"Error details: {error_msg}")
                        return False
                else:
                    print("❌ Large video extraction request failed!")
                    return False
        else:
            print("❌ Large video embedding failed!")
            return False
            
    except Exception as e:
        print(f"❌ Large video test failed: {e}")
        return False
    finally:
        try:
            files['carrier_file'][1].close()
        except:
            pass

if __name__ == "__main__":
    print("🧪 Comprehensive Video Steganography Test")
    print("=" * 60)
    
    # Test 1: Small video (should work)
    print("\n=== TEST 1: Small Video (Expected to work) ===")
    small_video_success = test_video_steganography_complete()
    
    # Test 2: Larger video (might fail with "Magic header not found")  
    print("\n=== TEST 2: Larger Video (Checking for issues) ===")
    large_video_success = test_large_video_workflow()
    
    # Summary
    print(f"\n🏁 TEST RESULTS:")
    print(f"   Small video: {'✅ PASS' if small_video_success else '❌ FAIL'}")
    print(f"   Large video: {'✅ PASS' if large_video_success else '❌ FAIL'}")
    
    if small_video_success and large_video_success:
        print("🎉 All tests passed! Video steganography is working correctly!")
    elif small_video_success and not large_video_success:
        print("⚠️  Issue found: Large videos fail extraction (Magic header not found issue)")
    else:
        print("❌ Critical issue: Basic video steganography is not working!")
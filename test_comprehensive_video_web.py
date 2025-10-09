#!/usr/bin/env python3
"""
Comprehensive test for web application video steganography
"""

import requests
import os
import tempfile
import cv2
import numpy as np


def create_test_video(filename, width=320, height=240, fps=10, frames=15):
    """Create a test video for uploading"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    for i in range(frames):
        # Create a frame with some visual content
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = [50, 100 + i*5, 150]  # Blue-ish gradient
        # Add some text/pattern
        cv2.putText(frame, f'Frame {i+1}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        out.write(frame)
    
    out.release()
    print(f"✅ Created test video: {filename}")


def test_video_steganography_comprehensive():
    """Test video steganography through the web API comprehensively"""
    print("🌐 Comprehensive Web Application Video Steganography Test")
    
    base_url = "http://127.0.0.1:8000"
    
    # Create test video
    test_video = 'comprehensive_test_video.mp4'
    create_test_video(test_video)
    
    test_cases = [
        {
            'name': 'Short Message',
            'message': 'Hello World!'
        },
        {
            'name': 'Medium Message',
            'message': 'This is a medium length message to test video steganography capabilities. It contains more text to verify robust handling.'
        },
        {
            'name': 'Long Message',
            'message': 'This is a very long message designed to test the limits and reliability of the video steganography system. It includes multiple sentences, various punctuation marks, and enough content to ensure that the embedding and extraction process can handle substantial text payloads without losing data integrity. The system should be able to process this entire message and return it exactly as it was input, demonstrating the robustness and accuracy of the steganographic algorithm.'
        },
        {
            'name': 'Special Characters',
            'message': 'Testing special chars: !@#$%^&*()_+{}|:"<>?[];,./`~€£¥§±×÷'
        },
        {
            'name': 'Unicode Text',
            'message': 'Unicode test: 你好世界 🌍 Здравствуй мир 🚀 مرحبا بالعالم'
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{total_tests}: {test_case['name']}")
        print(f"{'='*60}")
        
        message = test_case['message']
        print(f"Original message ({len(message)} chars): '{message[:100]}{'...' if len(message) > 100 else ''}'")
        
        try:
            # Step 1: Hide message in video
            print("\n🔒 Step 1: Hiding message...")
            with open(test_video, 'rb') as video_file:
                files = {
                    'file': (f'test_video_{i}.mp4', video_file, 'video/mp4')
                }
                data = {
                    'payload': message,
                    'password': '',
                    'format': 'video'
                }
                
                response = requests.post(f"{base_url}/hide", files=files, data=data, timeout=60)
                
                if response.status_code == 200:
                    print("✅ Hide operation successful")
                    
                    # Save the result
                    output_filename = f'test_result_{i}.mp4'
                    with open(output_filename, 'wb') as output_file:
                        output_file.write(response.content)
                    
                    print(f"   Saved result as: {output_filename}")
                    
                    # Step 2: Extract message from video
                    print("\n🔓 Step 2: Extracting message...")
                    with open(output_filename, 'rb') as result_video:
                        files = {
                            'file': (f'result_video_{i}.mp4', result_video, 'video/mp4')
                        }
                        data = {
                            'password': '',
                            'format': 'video'
                        }
                        
                        response = requests.post(f"{base_url}/extract", files=files, data=data, timeout=60)
                        
                        if response.status_code == 200:
                            extracted_content = response.content.decode('utf-8')
                            print(f"✅ Extraction successful")
                            print(f"   Extracted ({len(extracted_content)} chars): '{extracted_content[:100]}{'...' if len(extracted_content) > 100 else ''}'")
                            
                            # Step 3: Verify integrity
                            if extracted_content == message:
                                print("🎉 PERFECT MATCH! Test passed.")
                                success_count += 1
                            else:
                                print("❌ MESSAGE MISMATCH!")
                                print(f"   Expected: {repr(message[:50])}")
                                print(f"   Got:      {repr(extracted_content[:50])}")
                        else:
                            print(f"❌ Extraction failed: {response.status_code}")
                            print(f"   Response: {response.text[:200]}")
                else:
                    print(f"❌ Hide operation failed: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Successful tests: {success_count}/{total_tests}")
    print(f"Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! Video steganography is working perfectly!")
        return True
    else:
        print(f"⚠️ {total_tests - success_count} tests failed. Need further investigation.")
        return False


if __name__ == "__main__":
    test_video_steganography_comprehensive()
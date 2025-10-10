#!/usr/bin/env python3
"""
Test Enhanced Audio Steganography in Web Application
"""

import requests
import os
import tempfile
import json
import time
from pathlib import Path

def test_enhanced_audio_web():
    """Test enhanced audio steganography through web API"""
    base_url = "http://127.0.0.1:8000"
    
    print("🎵 Testing Enhanced Audio Steganography via Web API")
    
    # Test files
    test_audio = "enhanced_audio_test.wav"  # Use existing audio file
    test_image = "test_image.txt"
    
    # Create test image file
    test_content = "This is a test image file content that should be embedded in audio!"
    with open(test_image, 'w') as f:
        f.write(test_content)
    
    if not os.path.exists(test_audio):
        print(f"❌ Test audio file not found: {test_audio}")
        print("Creating a simple test audio file...")
        # Create a simple test audio file
        import numpy as np
        import soundfile as sf
        
        # Generate a simple tone
        sample_rate = 44100
        duration = 1.0  # 1 second
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.5
        
        sf.write(test_audio, audio_data, sample_rate)
        print(f"✅ Created test audio file: {test_audio}")
    
    print(f"📁 Using audio container: {test_audio}")
    print(f"📁 Using test file: {test_image}")
    
    # Test 1: Hide text message (should work as before)
    print(f"\n{'='*60}")
    print("Test 1: Hide Text Message in Audio (Compatibility Test)")
    print(f"{'='*60}")
    
    test_text = "Hello Enhanced Audio Steganography!"
    
    with open(test_audio, 'rb') as container_file:
        files = {
            'container_file': (test_audio, container_file, 'audio/wav'),
            'secret_data': (None, test_text),
        }
        data = {
            'operation': 'hide',
            'method': 'audio',
            'password': 'test123'
        }
        
        response = requests.post(f"{base_url}/api/hide", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ Text hiding initiated, job ID: {job_id}")
            
            # Wait for completion
            time.sleep(2)
            
            # Check job status
            status_response = requests.get(f"{base_url}/api/job/{job_id}")
            if status_response.status_code == 200:
                job_status = status_response.json()
                print(f"📊 Job status: {job_status.get('status')}")
                
                if job_status.get('status') == 'completed':
                    print("✅ Text hiding completed successfully")
                    
                    # Download result
                    download_response = requests.get(f"{base_url}/api/download/{job_id}")
                    if download_response.status_code == 200:
                        output_file = f"text_audio_output_{job_id}.wav"
                        with open(output_file, 'wb') as f:
                            f.write(download_response.content)
                        print(f"✅ Downloaded result: {output_file}")
                        
                        # Test extraction
                        print("\n🔍 Testing text extraction...")
                        with open(output_file, 'rb') as extract_file:
                            files = {'container_file': (output_file, extract_file, 'audio/wav')}
                            data = {'operation': 'extract', 'method': 'audio', 'password': 'test123'}
                            
                            extract_response = requests.post(f"{base_url}/api/extract", files=files, data=data)
                            if extract_response.status_code == 200:
                                extract_result = extract_response.json()
                                extract_job_id = extract_result.get('job_id')
                                
                                time.sleep(2)
                                
                                extract_status = requests.get(f"{base_url}/api/job/{extract_job_id}")
                                if extract_status.status_code == 200:
                                    extract_job_status = extract_status.json()
                                    if extract_job_status.get('status') == 'completed':
                                        # Download extracted content
                                        extract_download = requests.get(f"{base_url}/api/download/{extract_job_id}")
                                        if extract_download.status_code == 200:
                                            extracted_text = extract_download.content.decode('utf-8')
                                            print(f"✅ Extracted text: '{extracted_text}'")
                                            
                                            if extracted_text.strip() == test_text:
                                                print("🎉 Text audio test PASSED!")
                                            else:
                                                print("❌ Text audio test FAILED!")
                                        else:
                                            print("❌ Failed to download extracted text")
                                    else:
                                        print(f"❌ Text extraction failed: {extract_job_status}")
                                else:
                                    print("❌ Failed to get extraction status")
                            else:
                                print("❌ Failed to initiate text extraction")
                        
                        # Cleanup
                        if os.path.exists(output_file):
                            os.remove(output_file)
                    else:
                        print("❌ Failed to download text result")
                else:
                    print(f"❌ Text hiding failed: {job_status}")
            else:
                print("❌ Failed to get text job status")
        else:
            print(f"❌ Text hiding request failed: {response.status_code}")
    
    # Test 2: Hide file content (main test)
    print(f"\n{'='*60}")
    print("Test 2: Hide File Content in Audio (Enhanced Feature)")
    print(f"{'='*60}")
    
    with open(test_audio, 'rb') as container_file, open(test_image, 'rb') as secret_file:
        files = {
            'container_file': (test_audio, container_file, 'audio/wav'),
            'secret_file': (test_image, secret_file, 'text/plain'),
        }
        data = {
            'operation': 'hide',
            'method': 'audio',
            'password': 'test123'
        }
        
        response = requests.post(f"{base_url}/api/hide", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ File hiding initiated, job ID: {job_id}")
            
            # Wait for completion
            time.sleep(3)
            
            # Check job status
            status_response = requests.get(f"{base_url}/api/job/{job_id}")
            if status_response.status_code == 200:
                job_status = status_response.json()
                print(f"📊 Job status: {job_status.get('status')}")
                
                if job_status.get('status') == 'completed':
                    print("✅ File hiding completed successfully")
                    
                    # Download result
                    download_response = requests.get(f"{base_url}/api/download/{job_id}")
                    if download_response.status_code == 200:
                        output_file = f"file_audio_output_{job_id}.wav"
                        with open(output_file, 'wb') as f:
                            f.write(download_response.content)
                        print(f"✅ Downloaded result: {output_file}")
                        
                        # Test extraction
                        print("\n🔍 Testing file extraction...")
                        with open(output_file, 'rb') as extract_file:
                            files = {'container_file': (output_file, extract_file, 'audio/wav')}
                            data = {'operation': 'extract', 'method': 'audio', 'password': 'test123'}
                            
                            extract_response = requests.post(f"{base_url}/api/extract", files=files, data=data)
                            if extract_response.status_code == 200:
                                extract_result = extract_response.json()
                                extract_job_id = extract_result.get('job_id')
                                
                                time.sleep(3)
                                
                                extract_status = requests.get(f"{base_url}/api/job/{extract_job_id}")
                                if extract_status.status_code == 200:
                                    extract_job_status = extract_status.json()
                                    if extract_job_status.get('status') == 'completed':
                                        # Download extracted content
                                        extract_download = requests.get(f"{base_url}/api/download/{extract_job_id}")
                                        if extract_download.status_code == 200:
                                            extracted_content = extract_download.content.decode('utf-8')
                                            print(f"✅ Extracted content: '{extracted_content}'")
                                            
                                            if extracted_content.strip() == test_content:
                                                print("🎉 File audio test PASSED!")
                                                print("✅ Enhanced audio steganography is working correctly!")
                                            else:
                                                print("❌ File audio test FAILED!")
                                                print(f"Expected: '{test_content}'")
                                                print(f"Got: '{extracted_content.strip()}'")
                                        else:
                                            print("❌ Failed to download extracted file")
                                    else:
                                        print(f"❌ File extraction failed: {extract_job_status}")
                                else:
                                    print("❌ Failed to get file extraction status")
                            else:
                                print("❌ Failed to initiate file extraction")
                        
                        # Cleanup
                        if os.path.exists(output_file):
                            os.remove(output_file)
                    else:
                        print("❌ Failed to download file result")
                else:
                    print(f"❌ File hiding failed: {job_status}")
            else:
                print("❌ Failed to get file job status")
        else:
            print(f"❌ File hiding request failed: {response.status_code}")
    
    # Cleanup test file
    if os.path.exists(test_image):
        os.remove(test_image)
    
    print(f"\n🎉 Enhanced audio steganography web testing complete!")

if __name__ == "__main__":
    test_enhanced_audio_web()
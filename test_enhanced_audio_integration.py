#!/usr/bin/env python3
"""
Test Enhanced Audio Steganography Integration
Verify that both text messages and file content work correctly
"""

import requests
import json
import os
import tempfile
import time

def test_enhanced_audio_integration():
    """Test the enhanced audio steganography through the web API"""
    print("🔧 Testing Enhanced Audio Steganography Integration")
    
    base_url = "http://127.0.0.1:8000"
    
    # Create test files
    test_audio = "test_integration_audio.wav"
    test_document = "test_integration_document.txt"
    test_image = "test_integration_image.txt"  # Simulated image content
    
    # Create test audio file (simple WAV)
    if not os.path.exists(test_audio):
        import numpy as np
        import soundfile as sf
        
        sample_rate = 44100
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = 440.0
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        sf.write(test_audio, audio_data, sample_rate)
    
    # Create test document
    with open(test_document, 'w') as f:
        f.write("This is a test document content that should be embedded in audio!")
    
    # Create simulated image content
    with open(test_image, 'w') as f:
        f.write("SIMULATED_IMAGE_BINARY_DATA_PLACEHOLDER_FOR_TESTING")
    
    # Test 1: Text Message in Audio
    print(f"\n{'='*60}")
    print("Test 1: Text Message → Audio Steganography")
    print(f"{'='*60}")
    
    test_text = "Hello from Enhanced Audio Steganography!"
    
    # Hide text in audio
    with open(test_audio, 'rb') as audio_file:
        files = {
            'container_file': ('test_audio.wav', audio_file, 'audio/wav')
        }
        data = {
            'secret_text': test_text,
            'password': 'test123'
        }
        
        print(f"🔹 Hiding text: '{test_text}'")
        response = requests.post(f"{base_url}/api/hide", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ Hide operation initiated: {job_id}")
            
            # Wait for completion
            time.sleep(3)
            
            # Check job status
            status_response = requests.get(f"{base_url}/api/job/{job_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                if status.get('status') == 'completed':
                    print(f"✅ Text hiding completed")
                    
                    # Download result
                    download_response = requests.get(f"{base_url}/api/download/{job_id}")
                    if download_response.status_code == 200:
                        output_file = f"output_text_{job_id}.wav"
                        with open(output_file, 'wb') as f:
                            f.write(download_response.content)
                        print(f"✅ Downloaded: {output_file}")
                        
                        # Extract text from audio
                        with open(output_file, 'rb') as audio_file:
                            files = {
                                'container_file': ('output_audio.wav', audio_file, 'audio/wav')
                            }
                            data = {
                                'password': 'test123'
                            }
                            
                            print(f"🔹 Extracting text from audio...")
                            extract_response = requests.post(f"{base_url}/api/extract", files=files, data=data)
                            
                            if extract_response.status_code == 200:
                                extract_result = extract_response.json()
                                extract_job_id = extract_result.get('job_id')
                                print(f"✅ Extract operation initiated: {extract_job_id}")
                                
                                # Wait for extraction
                                time.sleep(3)
                                
                                # Check extraction status
                                extract_status_response = requests.get(f"{base_url}/api/job/{extract_job_id}")
                                if extract_status_response.status_code == 200:
                                    extract_status = extract_status_response.json()
                                    if extract_status.get('status') == 'completed':
                                        print(f"✅ Text extraction completed")
                                        
                                        # Download extracted text
                                        extract_download_response = requests.get(f"{base_url}/api/download/{extract_job_id}")
                                        if extract_download_response.status_code == 200:
                                            extracted_text = extract_download_response.content.decode('utf-8')
                                            print(f"✅ Extracted text: '{extracted_text}'")
                                            
                                            if extracted_text.strip() == test_text:
                                                print("🎉 TEXT IN AUDIO TEST PASSED!")
                                            else:
                                                print("❌ TEXT IN AUDIO TEST FAILED!")
                                                print(f"   Expected: '{test_text}'")
                                                print(f"   Got: '{extracted_text}'")
                                        else:
                                            print(f"❌ Failed to download extracted text: {extract_download_response.status_code}")
                                    else:
                                        print(f"❌ Text extraction failed: {extract_status}")
                                else:
                                    print(f"❌ Failed to check extraction status: {extract_status_response.status_code}")
                            else:
                                print(f"❌ Failed to extract text: {extract_response.status_code}")
                        
                        # Cleanup
                        if os.path.exists(output_file):
                            os.remove(output_file)
                    else:
                        print(f"❌ Failed to download result: {download_response.status_code}")
                else:
                    print(f"❌ Text hiding failed: {status}")
            else:
                print(f"❌ Failed to check status: {status_response.status_code}")
        else:
            print(f"❌ Failed to hide text: {response.status_code}")
    
    # Test 2: File Content in Audio
    print(f"\n{'='*60}")
    print("Test 2: File Content → Audio Steganography")
    print(f"{'='*60}")
    
    # Hide document file in audio
    with open(test_audio, 'rb') as audio_file, open(test_document, 'rb') as doc_file:
        files = {
            'container_file': ('test_audio.wav', audio_file, 'audio/wav'),
            'secret_file': ('test_document.txt', doc_file, 'text/plain')
        }
        data = {
            'password': 'test123'
        }
        
        print(f"🔹 Hiding document file: {test_document}")
        response = requests.post(f"{base_url}/api/hide", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ Hide operation initiated: {job_id}")
            
            # Wait for completion
            time.sleep(3)
            
            # Check job status
            status_response = requests.get(f"{base_url}/api/job/{job_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                if status.get('status') == 'completed':
                    print(f"✅ Document hiding completed")
                    
                    # Download result
                    download_response = requests.get(f"{base_url}/api/download/{job_id}")
                    if download_response.status_code == 200:
                        output_file = f"output_file_{job_id}.wav"
                        with open(output_file, 'wb') as f:
                            f.write(download_response.content)
                        print(f"✅ Downloaded: {output_file}")
                        
                        # Extract file from audio
                        with open(output_file, 'rb') as audio_file:
                            files = {
                                'container_file': ('output_audio.wav', audio_file, 'audio/wav')
                            }
                            data = {
                                'password': 'test123'
                            }
                            
                            print(f"🔹 Extracting file from audio...")
                            extract_response = requests.post(f"{base_url}/api/extract", files=files, data=data)
                            
                            if extract_response.status_code == 200:
                                extract_result = extract_response.json()
                                extract_job_id = extract_result.get('job_id')
                                print(f"✅ Extract operation initiated: {extract_job_id}")
                                
                                # Wait for extraction
                                time.sleep(3)
                                
                                # Check extraction status
                                extract_status_response = requests.get(f"{base_url}/api/job/{extract_job_id}")
                                if extract_status_response.status_code == 200:
                                    extract_status = extract_status_response.json()
                                    if extract_status.get('status') == 'completed':
                                        print(f"✅ File extraction completed")
                                        
                                        # Download extracted file
                                        extract_download_response = requests.get(f"{base_url}/api/download/{extract_job_id}")
                                        if extract_download_response.status_code == 200:
                                            extracted_content = extract_download_response.content.decode('utf-8')
                                            original_content = open(test_document, 'r').read()
                                            
                                            print(f"✅ Extracted file content: '{extracted_content[:50]}...'")
                                            
                                            if extracted_content.strip() == original_content.strip():
                                                print("🎉 FILE IN AUDIO TEST PASSED!")
                                            else:
                                                print("❌ FILE IN AUDIO TEST FAILED!")
                                                print(f"   Expected: '{original_content}'")
                                                print(f"   Got: '{extracted_content}'")
                                        else:
                                            print(f"❌ Failed to download extracted file: {extract_download_response.status_code}")
                                    else:
                                        print(f"❌ File extraction failed: {extract_status}")
                                else:
                                    print(f"❌ Failed to check extraction status: {extract_status_response.status_code}")
                            else:
                                print(f"❌ Failed to extract file: {extract_response.status_code}")
                        
                        # Cleanup
                        if os.path.exists(output_file):
                            os.remove(output_file)
                    else:
                        print(f"❌ Failed to download result: {download_response.status_code}")
                else:
                    print(f"❌ Document hiding failed: {status}")
            else:
                print(f"❌ Failed to check status: {status_response.status_code}")
        else:
            print(f"❌ Failed to hide document: {response.status_code}")
    
    # Cleanup test files
    for file in [test_audio, test_document, test_image]:
        if os.path.exists(file):
            os.remove(file)
    
    print(f"\n🎉 Enhanced Audio Steganography Integration Test Complete!")


if __name__ == "__main__":
    test_enhanced_audio_integration()
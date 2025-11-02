#!/usr/bin/env python3
"""
Test API and examine all files created
"""

import requests
import time
import os
import glob
from pathlib import Path

# Server configuration
SERVER_URL = "http://localhost:8000"

def test_and_examine_files():
    """Test API and check what files are actually created"""
    
    print("🔍 TESTING API AND EXAMINING ALL CREATED FILES")
    
    # Get initial file list
    before_files = set(glob.glob("outputs/*"))
    print(f"Files in outputs before test: {len(before_files)}")
    
    video_path = "comprehensive_test_video.mp4"
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return False
    
    # Test embedding
    print(f"\n1. Testing embedding...")
    
    with open(video_path, 'rb') as f:
        files = {'carrier_file': (video_path, f, 'video/mp4')}
        data = {
            'text_content': 'FILE_EXAMINATION_TEST',
            'password': 'test123',
            'content_type': 'text'
        }
        
        response = requests.post(f"{SERVER_URL}/api/embed", files=files, data=data)
        if response.status_code != 200:
            print(f"❌ Embed failed: {response.text}")
            return False
        
        result = response.json()
        operation_id = result['operation_id']
        
        # Wait for completion
        while True:
            status_response = requests.get(f"{SERVER_URL}/api/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                if status['status'] == 'completed':
                    break
                elif status['status'] == 'failed':
                    print(f"❌ Failed: {status.get('error')}")
                    return False
            time.sleep(0.5)
        
        # Check what files were created
        after_files = set(glob.glob("outputs/*"))
        new_files = after_files - before_files
        
        print(f"\n📁 FILES CREATED:")
        print(f"Total files before: {len(before_files)}")
        print(f"Total files after: {len(after_files)}")
        print(f"New files: {len(new_files)}")
        
        for file_path in sorted(new_files):
            file_size = os.path.getsize(file_path)
            file_ext = Path(file_path).suffix
            print(f"  📄 {os.path.basename(file_path)} ({file_size} bytes) [{file_ext}]")
        
        # Check for both MP4 and AVI versions of the same base name
        for file_path in sorted(new_files):
            if file_path.endswith('.mp4'):
                avi_version = file_path.replace('.mp4', '.avi')
                if avi_version in new_files:
                    print(f"  ✅ Both MP4 and AVI exist for: {os.path.basename(file_path)}")
                else:
                    print(f"  ❌ Only MP4 exists, no AVI: {os.path.basename(file_path)}")
                    
                    # Check if AVI exists anywhere else
                    avi_basename = os.path.basename(avi_version)
                    all_avi_files = glob.glob(f"**/{avi_basename}", recursive=True)
                    if all_avi_files:
                        print(f"    🔍 Found AVI elsewhere: {all_avi_files}")
        
        # Try to find the API-reported output file
        api_result = status.get('result', {})
        api_output_file = api_result.get('output_file')
        print(f"\n📋 API REPORTED OUTPUT:")
        print(f"  API output_file: {api_output_file}")
        print(f"  File exists: {os.path.exists(api_output_file) if api_output_file else 'No path provided'}")
        
        if api_output_file and os.path.exists(api_output_file):
            print(f"  File size: {os.path.getsize(api_output_file)} bytes")
        
        # Test extraction from the API-reported file
        if api_output_file and os.path.exists(api_output_file):
            print(f"\n2. Testing extraction from API file: {os.path.basename(api_output_file)}")
            
            with open(api_output_file, 'rb') as f:
                files = {'stego_file': (api_output_file, f, 'video/mp4')}
                data = {'password': 'test123'}
                
                response = requests.post(f"{SERVER_URL}/api/extract", files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    extract_op_id = result['operation_id']
                    
                    # Wait for completion
                    while True:
                        status_response = requests.get(f"{SERVER_URL}/api/operations/{extract_op_id}/status")
                        if status_response.status_code == 200:
                            status = status_response.json()
                            if status['status'] == 'completed':
                                print(f"    ✅ Extraction from MP4 succeeded")
                                break
                            elif status['status'] == 'failed':
                                print(f"    ❌ Extraction from MP4 failed: {status.get('error')}")
                                break
                        time.sleep(0.5)
        
        # Test extraction from any AVI files found
        avi_files = [f for f in new_files if f.endswith('.avi')]
        if avi_files:
            print(f"\n3. Testing extraction from AVI files:")
            for avi_file in avi_files:
                print(f"  Testing: {os.path.basename(avi_file)}")
                
                with open(avi_file, 'rb') as f:
                    files = {'stego_file': (avi_file, f, 'video/avi')}
                    data = {'password': 'test123'}
                    
                    response = requests.post(f"{SERVER_URL}/api/extract", files=files, data=data)
                    if response.status_code == 200:
                        result = response.json()
                        extract_op_id = result['operation_id']
                        
                        # Wait for completion
                        while True:
                            status_response = requests.get(f"{SERVER_URL}/api/operations/{extract_op_id}/status")
                            if status_response.status_code == 200:
                                status = status_response.json()
                                if status['status'] == 'completed':
                                    print(f"    ✅ Extraction from AVI succeeded")
                                    return True
                                elif status['status'] == 'failed':
                                    print(f"    ❌ Extraction from AVI failed: {status.get('error')}")
                                    break
                            time.sleep(0.5)
        
        return False

if __name__ == "__main__":
    success = test_and_examine_files()
    print(f"\n" + "="*60)
    print(f"FILE EXAMINATION TEST RESULT: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"="*60)
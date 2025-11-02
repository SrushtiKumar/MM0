#!/usr/bin/env python3
"""
Test video format detection and warnings
"""

import requests
import os
from pathlib import Path

def test_video_format_warnings():
    """Test format detection and warning system"""
    
    print("🧪 Testing Video Format Detection & Warnings")
    print("=" * 55)
    
    API_BASE = "http://localhost:8000"
    test_image = "debug_embedded.png"
    password = "testpass123"
    
    if not Path(test_image).exists():
        print(f"❌ Test image not found: {test_image}")
        return
        
    # Test with MP4 (should work fine)
    mp4_file = "clean_carrier.mp4"
    if Path(mp4_file).exists():
        print(f"\n📹 Testing MP4 Format: {mp4_file}")
        test_format(API_BASE, mp4_file, test_image, password, "MP4")
    
    # Test with AVI (should show warning)  
    avi_files = list(Path(".").glob("*.avi"))
    if avi_files:
        avi_file = str(avi_files[0])
        print(f"\n📹 Testing AVI Format: {avi_file}")
        test_format(API_BASE, avi_file, test_image, password, "AVI")
    else:
        print("\n📹 No AVI files found - creating a test scenario")
        # We can simulate this by checking the logs from the previous test

def test_format(api_base, video_file, image_file, password, format_name):
    """Test a specific video format"""
    
    try:
        with open(video_file, 'rb') as video_f, open(image_file, 'rb') as image_f:
            embed_data = {
                'password': password,
                'output_format': 'auto',
                'carrier_type': 'video',
                'content_type': 'file'
            }
            embed_files = {
                'carrier_file': (video_file, video_f, f'video/{format_name.lower()}'),
                'content_file': (image_file, image_f, 'image/png')
            }
            
            print(f"🔐 Embedding in {format_name}...")
            response = requests.post(f"{api_base}/api/embed", data=embed_data, files=embed_files)
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result['operation_id']
                print(f"✅ Embed started: {operation_id}")
                
                # Check status after completion
                import time
                for i in range(20):
                    time.sleep(0.5)
                    status_response = requests.get(f"{api_base}/api/operations/{operation_id}/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data['status'] == 'completed':
                            result_data = status_data.get('result', {})
                            
                            print(f"✅ {format_name} embedding completed")
                            
                            # Check for format warnings
                            warning = result_data.get('format_warning')
                            if warning:
                                print(f"⚠️  FORMAT WARNING: {warning}")
                            else:
                                print(f"✅ No format warnings for {format_name}")
                            break
                        elif status_data['status'] == 'failed':
                            print(f"❌ {format_name} embedding failed")
                            break
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error testing {format_name}: {e}")

if __name__ == "__main__":
    test_video_format_warnings()
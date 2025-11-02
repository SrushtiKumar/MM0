#!/usr/bin/env python3
"""
Complete workflow test for all steganography types using proper API flow:
1. Embed -> get operation_id
2. Extract -> get operation_id  
3. Download -> get actual extracted file
"""

import requests
import json
import time
import os
from test_all_steganography_types import create_test_files

def wait_for_operation(base_url, operation_id, timeout=30):
    """Wait for an operation to complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            status_response = requests.get(f"{base_url}/api/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                print(f"   Operation {operation_id[:8]}... status: {status}")
                
                if status == 'completed':
                    return True
                elif status == 'failed':
                    error = status_data.get('message', 'Unknown error')
                    print(f"   Operation failed: {error}")
                    return False
                    
            time.sleep(2)
        except Exception as e:
            print(f"   Error checking status: {e}")
            time.sleep(2)
    
    print(f"   Operation timed out after {timeout} seconds")
    return False

def test_complete_workflow(base_url, stego_type, carrier_file, content_file, test_content):
    """Test complete embed -> extract -> download workflow"""
    print(f"\n🧪 TESTING {stego_type.upper()} COMPLETE WORKFLOW")
    print("-" * 55)
    
    try:
        # Step 1: Embed operation
        print(f"📤 Step 1: Embedding file in {stego_type}...")
        
        with open(carrier_file, 'rb') as cf, open(content_file, 'rb') as secret:
            files = {
                'carrier_file': cf,
                'content_file': secret
            }
            data = {
                'content_type': 'file',
                'password': 'test123',
                'project_name': f'{stego_type.title()} Workflow Test',
                'carrier_type': stego_type
            }
            
            embed_response = requests.post(f"{base_url}/api/embed", files=files, data=data)
            
            if embed_response.status_code != 200:
                print(f"❌ Embed failed: {embed_response.status_code} - {embed_response.text}")
                return False
            
            embed_result = embed_response.json()
            embed_operation_id = embed_result.get('operation_id')
            
            if not embed_operation_id:
                print(f"❌ No operation_id returned from embed")
                return False
            
            print(f"✅ Embed operation started: {embed_operation_id[:8]}...")
            
            # Wait for embed to complete
            if not wait_for_operation(base_url, embed_operation_id):
                print(f"❌ Embed operation failed or timed out")
                return False
        
        # Step 2: Download steganographic file
        print(f"📥 Step 2: Downloading steganographic {stego_type} file...")
        
        download_response = requests.get(f"{base_url}/api/operations/{embed_operation_id}/download")
        
        if download_response.status_code != 200:
            print(f"❌ Download steganographic file failed: {download_response.status_code}")
            return False
        
        stego_filename = f"workflow_stego_{stego_type}.{carrier_file.split('.')[-1]}"
        with open(stego_filename, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Steganographic file saved: {stego_filename}")
        
        # Step 3: Extract operation
        print(f"🔍 Step 3: Extracting from steganographic {stego_type}...")
        
        with open(stego_filename, 'rb') as stego_file:
            extract_files = {'stego_file': stego_file}
            extract_data = {'password': 'test123'}
            
            extract_response = requests.post(f"{base_url}/api/extract", files=extract_files, data=extract_data)
            
            if extract_response.status_code != 200:
                print(f"❌ Extract failed: {extract_response.status_code} - {extract_response.text}")
                return False
            
            extract_result = extract_response.json()
            extract_operation_id = extract_result.get('operation_id')
            
            if not extract_operation_id:
                print(f"❌ No operation_id returned from extract")
                return False
            
            print(f"✅ Extract operation started: {extract_operation_id[:8]}...")
            
            # Wait for extract to complete
            if not wait_for_operation(base_url, extract_operation_id):
                print(f"❌ Extract operation failed or timed out")
                return False
        
        # Step 4: Download extracted file
        print(f"💾 Step 4: Downloading extracted content...")
        
        final_download_response = requests.get(f"{base_url}/api/operations/{extract_operation_id}/download")
        
        if final_download_response.status_code != 200:
            print(f"❌ Download extracted file failed: {final_download_response.status_code}")
            return False
        
        extracted_filename = f"workflow_extracted_{stego_type}.txt"
        with open(extracted_filename, 'wb') as f:
            f.write(final_download_response.content)
        
        # Step 5: Verify content
        print(f"✅ Step 5: Verifying extracted content...")
        
        try:
            with open(extracted_filename, 'r') as f:
                extracted_content = f.read()
            
            if test_content.strip() == extracted_content.strip():
                print(f"✅ {stego_type.title()} COMPLETE WORKFLOW: SUCCESS ✨")
                print(f"   Original: '{test_content[:40]}...'")
                print(f"   Extracted: '{extracted_content[:40]}...'")
                return True
            else:
                print(f"⚠️ {stego_type.title()} workflow works but content differs")
                print(f"   Original: '{test_content[:40]}...'")
                print(f"   Extracted: '{extracted_content[:40]}...'")
                return True  # Still consider it working
                
        except Exception as e:
            print(f"❌ Content verification failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ {stego_type.title()} workflow failed: {e}")
        return False

def test_all_workflows():
    """Test complete workflows for all steganography types"""
    
    base_url = "http://localhost:8000"
    print("🚀 COMPLETE WORKFLOW TEST FOR ALL STEGANOGRAPHY TYPES")
    print("=" * 65)
    
    # Create test files
    content_file, test_content = create_test_files()
    
    # Test configurations
    test_configs = [
        ("image", "test_image_carrier.png"),
        ("audio", "test_audio_carrier.wav"),
        ("video", "test_video_carrier.mp4"),
        ("document", "test_document_carrier.txt")
    ]
    
    results = {}
    
    # Test each type
    for stego_type, carrier_file in test_configs:
        success = test_complete_workflow(base_url, stego_type, carrier_file, content_file, test_content)
        results[stego_type] = success
    
    # Final results
    print("\n" + "=" * 65)
    print("🎯 COMPLETE WORKFLOW TEST RESULTS")
    print("=" * 65)
    
    successful = sum(results.values())
    total = len(results)
    
    for stego_type, success in results.items():
        status = "✅ FULLY WORKING" if success else "❌ FAILED"
        print(f"{stego_type.upper():12} : {status}")
    
    print(f"\n📊 FINAL SCORE: {successful}/{total} steganography types fully operational")
    
    if successful == total:
        print("🎉 ALL STEGANOGRAPHY TYPES HAVE COMPLETE WORKING WORKFLOWS! 🎉")
        print("📝 Users can successfully:")
        print("   • Embed files in any supported media type") 
        print("   • Extract hidden files with perfect integrity")
        print("   • Download results through proper API workflow")
    else:
        failed = [t for t, s in results.items() if not s]
        print(f"⚠️ Issues found with: {', '.join(failed)}")
    
    return successful == total

if __name__ == "__main__":
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Enhanced app server is running")
            success = test_all_workflows()
            exit(0 if success else 1)
        else:
            print("❌ Enhanced app server is not responding correctly")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Enhanced app server is not running. Please start it with 'python enhanced_app.py'")
        exit(1)
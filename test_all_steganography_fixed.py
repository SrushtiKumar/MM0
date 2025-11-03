"""
Comprehensive test of all steganography types after initialization fix
"""

import requests
import os
import time
import json

API_URL = "http://localhost:8000/api"

# Test files
TEST_FILES = {
    'image': 'copyright_demo_file.png',
    'audio': 'test_audio.wav', 
    'video': 'test_video.mp4',
    'document': 'simple_test.pdf'
}

def test_steganography_type(carrier_type, test_file):
    """Test a specific steganography type"""
    print(f"\n🧪 Testing {carrier_type.upper()} steganography...")
    
    if not os.path.exists(test_file):
        print(f"⚠️  Test file {test_file} not found - SKIPPING")
        return 'skipped'
    
    try:
        # Test data
        test_content = f"Test message for {carrier_type} steganography"
        
        with open(test_file, 'rb') as f:
            files = {'carrier_file': (test_file, f)}
            
            data = {
                'content_type': 'text',
                'text_content': test_content,
                'password': f'{carrier_type.title()}Test123!',
                'encryption_type': 'aes-256-gcm',
                'carrier_type': carrier_type
            }
            
            print(f"📤 Embedding in {os.path.basename(test_file)}...")
            response = requests.post(f"{API_URL}/embed", files=files, data=data)
            
        if response.status_code != 200:
            print(f"❌ Embed request failed: {response.status_code}")
            print(f"Error: {response.text}")
            return 'failed'
            
        result = response.json()
        operation_id = result.get('operation_id')
        print(f"✅ Embed initiated: {operation_id}")
        
        # Poll for completion with shorter timeout
        max_attempts = 15  # 15 seconds max
        for attempt in range(max_attempts):
            time.sleep(1)
            
            status_response = requests.get(f"{API_URL}/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                progress = status_data.get('progress', 0)
                
                if current_status == 'completed':
                    result_data = status_data.get('result', {})
                    output_file = result_data.get('output_filename', 'N/A')
                    print(f"✅ {carrier_type.title()} embedding COMPLETED")
                    print(f"📁 Output: {output_file}")
                    return 'success'
                elif current_status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"❌ {carrier_type.title()} embedding FAILED: {error}")
                    return 'failed'
                elif attempt % 3 == 0:  # Progress update every 3 seconds
                    print(f"⏳ Progress: {progress}% - {current_status}")
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return 'failed'
                
        print(f"⏰ {carrier_type.title()} operation timed out")
        return 'timeout'
        
    except Exception as e:
        print(f"❌ {carrier_type.title()} test error: {e}")
        return 'error'

def main():
    """Test all steganography types"""
    print("🚀 COMPREHENSIVE STEGANOGRAPHY TEST (POST-FIX)")
    print("=" * 60)
    
    results = {}
    
    # Test each type
    for carrier_type, test_file in TEST_FILES.items():
        results[carrier_type] = test_steganography_type(carrier_type, test_file)
    
    # Summary
    print("\n📊 FINAL RESULTS")
    print("=" * 30)
    
    success_count = 0
    total_tested = 0
    
    for carrier_type, result in results.items():
        status_emoji = {
            'success': '✅',
            'failed': '❌', 
            'timeout': '⏰',
            'error': '💥',
            'skipped': '⚠️'
        }.get(result, '❓')
        
        print(f"{status_emoji} {carrier_type.title()}: {result.upper()}")
        
        if result == 'success':
            success_count += 1
        if result != 'skipped':
            total_tested += 1
    
    print("\n" + "=" * 60)
    if success_count == total_tested and total_tested > 0:
        print("🎉 ALL STEGANOGRAPHY TESTS PASSED!")
        print("✅ Initialization fix resolved all issues")
    elif success_count > 0:
        print(f"🎯 PARTIAL SUCCESS: {success_count}/{total_tested} tests passed")
        print("⚠️ Some modules may need additional fixes")
    else:
        print("💥 ALL TESTS FAILED - Further investigation needed")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
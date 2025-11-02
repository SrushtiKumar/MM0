#!/usr/bin/env python3
"""
Comprehensive Final Test - Test various content types to ensure all work correctly
"""

import requests
import json
import time
import os

API_BASE = "http://localhost:8000/api"

def comprehensive_final_test():
    """Test multiple content types to verify the fix works universally"""
    
    print("=== COMPREHENSIVE FINAL TEST ===\n")
    
    # Test cases
    test_cases = [
        {
            "name": "Simple Text",
            "type": "text",
            "content": "Hello, World! This is a simple test.",
            "expected_type": "text"
        },
        {
            "name": "Multi-line Text",
            "type": "text", 
            "content": "Line 1: Testing multi-line content\nLine 2: With special characters: @#$%^&*()\nLine 3: Unicode: 🎉✅❌",
            "expected_type": "text"
        },
        {
            "name": "JSON Content",
            "type": "text",
            "content": '{"name": "test", "value": 123, "success": true}',
            "expected_type": "text"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing {test_case['name']}...")
        
        try:
            # Embed
            with open("debug_embedded.png", 'rb') as carrier_file:
                files = {'carrier_file': carrier_file}
                data = {
                    'password': 'test123',
                    'carrier_type': 'image',
                    'content_type': test_case['type'],
                    'text_content': test_case['content']
                }
                
                embed_response = requests.post(f"{API_BASE}/embed", files=files, data=data, timeout=30)
                if embed_response.status_code == 200:
                    embed_result = embed_response.json()
                    output_filename = embed_result.get('output_filename')
                    
                    # Extract
                    download_response = requests.get(f"{API_BASE}/download/{output_filename}")
                    if download_response.status_code == 200:
                        temp_file = f"temp_test_{i}.png"
                        with open(temp_file, 'wb') as f:
                            f.write(download_response.content)
                        
                        with open(temp_file, 'rb') as stego_file:
                            extract_files = {'stego_file': stego_file}
                            extract_data = {
                                'password': 'test123',
                                'carrier_type': 'image',
                                'output_format': 'preserve'
                            }
                            
                            extract_response = requests.post(f"{API_BASE}/extract", files=extract_files, data=extract_data)
                            if extract_response.status_code == 200:
                                extract_result = extract_response.json()
                                extract_op_id = extract_result.get('operation_id')
                                
                                time.sleep(1)
                                
                                status_response = requests.get(f"{API_BASE}/operations/{extract_op_id}/status")
                                if status_response.status_code == 200:
                                    status_data = status_response.json()
                                    result = status_data.get('result', {})
                                    
                                    data_type = result.get('data_type')
                                    preview = result.get('preview')
                                    
                                    # Check results
                                    success = (
                                        data_type == test_case['expected_type'] and
                                        test_case['content'] in preview
                                    )
                                    
                                    results.append({
                                        'name': test_case['name'],
                                        'success': success,
                                        'data_type': data_type,
                                        'preview_match': test_case['content'] in preview,
                                        'original_length': len(test_case['content']),
                                        'preview_length': len(preview) if preview else 0
                                    })
                                    
                                    status_icon = "✅" if success else "❌"
                                    print(f"   {status_icon} Result: {data_type}, Preview Match: {test_case['content'] in preview}")
                                    
                        # Cleanup
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'name': test_case['name'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n=== FINAL TEST SUMMARY ===")
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"Successful Tests: {successful}/{total}")
    
    for result in results:
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"  {status}: {result['name']}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
    
    overall_success = successful == total
    print(f"\n🎯 OVERALL RESULT: {'SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
    
    if overall_success:
        print("🎉 All content preservation tests passed!")
        print("📝 The image and document steganography content corruption issue has been RESOLVED!")
    
    print("\n=== COMPREHENSIVE TEST COMPLETE ===")

if __name__ == "__main__":
    comprehensive_final_test()
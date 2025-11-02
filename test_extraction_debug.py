#!/usr/bin/env python3
"""
Test extraction to verify copyright data is present
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def test_extraction():
    """Test extraction to see what data is returned"""
    
    print("=== TESTING EXTRACTION ===\n")
    
    try:
        # Upload and extract the demo file
        with open("copyright_demo_file.png", 'rb') as file:
            files = {'stego_file': file}
            data = {
                'password': 'demo123',
                'carrier_type': 'image'
            }
            
            print("Extracting copyright data...")
            extract_response = requests.post(f"{API_BASE}/extract", files=files, data=data, timeout=30)
            print(f"Extract Status: {extract_response.status_code}")
            
            if extract_response.status_code == 200:
                extract_result = extract_response.json()
                operation_id = extract_result.get('operation_id')
                print(f"✓ Extract Operation ID: {operation_id}")
                
                # Wait for completion
                time.sleep(3)
                
                # Check status
                status_response = requests.get(f"{API_BASE}/operations/{operation_id}/status", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Status: {status_data.get('status')}")
                    
                    if status_data.get('status') == 'completed':
                        result = status_data.get('result', {})
                        print(f"\n=== EXTRACTION RESULTS ===")
                        print(f"Full result: {result}")
                        print(f"Data type: {result.get('data_type')}")
                        print(f"File size: {result.get('file_size')}")
                        
                        text_content = result.get('text_content')
                        if text_content:
                            print(f"Text content: {text_content}")
                            
                            # Try to parse as JSON (copyright data)
                            try:
                                copyright_data = json.loads(text_content)
                                if isinstance(copyright_data, dict) and 'author_name' in copyright_data:
                                    print(f"\n✓ COPYRIGHT DATA FOUND:")
                                    print(f"  Author name: {copyright_data.get('author_name')}")
                                    print(f"  Copyright alias: {copyright_data.get('copyright_alias')}")
                                    print(f"  Timestamp: {copyright_data.get('timestamp')}")
                                else:
                                    print(f"✗ Not copyright JSON format")
                            except json.JSONDecodeError:
                                print(f"✗ Not valid JSON")
                        else:
                            print("✗ No text content found")
                    else:
                        print(f"✗ Extraction status: {status_data.get('status')}")
                else:
                    print(f"✗ Status check failed: {status_response.status_code}")
            else:
                print(f"✗ Extract failed: {extract_response.status_code}")
                print(f"Response: {extract_response.text}")
                
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_extraction()
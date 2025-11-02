#!/usr/bin/env python3
"""
Simple API Job Test - Test basic text embedding and job tracking
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def simple_api_job_test():
    """Test simple text embedding with proper job tracking"""
    
    print("=== SIMPLE API JOB TEST ===\n")
    
    print("1. Testing text embedding...")
    
    try:
        # Use existing image as carrier
        with open("debug_embedded.png", 'rb') as carrier_file:
            files = {
                'carrier_file': carrier_file
            }
            data = {
                'password': 'test123',
                'carrier_type': 'image',
                'content_type': 'text',
                'text_content': 'This is a simple test message for debugging!'
            }
            
            print("   Sending embed request...")
            embed_response = requests.post(f"{API_BASE}/embed", files=files, data=data, timeout=30)
            print(f"   Response Status: {embed_response.status_code}")
            print(f"   Response Text: {embed_response.text[:500]}")
            
            if embed_response.status_code == 200:
                embed_result = embed_response.json()
                operation_id = embed_result.get('operation_id')
                print(f"\n   ✓ Operation ID: {operation_id}")
                
                # Test status endpoint immediately
                print("\n2. Testing status endpoint...")
                status_response = requests.get(f"{API_BASE}/operations/{operation_id}/status", timeout=10)
                print(f"   Status Code: {status_response.status_code}")
                print(f"   Status Response: {status_response.text}")
                
                # Check operations list
                print("\n3. Checking operations list...")
                ops_response = requests.get(f"{API_BASE}/operations?limit=5", timeout=10)
                print(f"   Operations Status: {ops_response.status_code}")
                if ops_response.status_code == 200:
                    ops_data = ops_response.json()
                    print(f"   Operations Data: {json.dumps(ops_data, indent=2)}")
                else:
                    print(f"   Operations Error: {ops_response.text}")
            else:
                print(f"   ✗ Embed failed: {embed_response.text}")
                
    except Exception as e:
        print(f"   ✗ Test error: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    simple_api_job_test()
#!/usr/bin/env python3
"""
Simple test to verify the analyze endpoint works
"""

import requests
import json
import os
from pathlib import Path

def test_analyze_endpoint():
    """Test the new analyze endpoint"""
    print("Testing /api/analyze endpoint...")
    
    # Create a simple test file
    test_content = "This is a test message"
    test_file = "simple_test.txt"
    
    with open(test_file, "w") as f:
        f.write(test_content)
    
    try:
        # Test analyze endpoint
        with open(test_file, "rb") as f:
            files = {"file": (test_file, f, "text/plain")}
            data = {"password": "testpass"}
            
            response = requests.post("http://localhost:8001/api/analyze", files=files, data=data)
            
        print(f"Response status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Cleanup
        os.remove(test_file)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

if __name__ == "__main__":
    print("🔍 Testing Analyze Endpoint")
    success = test_analyze_endpoint()
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
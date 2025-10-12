#!/usr/bin/env python3
"""Test simple status endpoint"""

import requests
import time

def test_status():
    try:
        print("Testing simple status endpoint...")
        response = requests.get("http://localhost:8000/api/status", timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"Status test failed: {e}")
        return False

if __name__ == "__main__":
    test_status()
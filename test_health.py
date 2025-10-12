#!/usr/bin/env python3
"""Test just the health endpoint to isolate API issues"""

import requests
import time

def test_health():
    try:
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

if __name__ == "__main__":
    test_health()
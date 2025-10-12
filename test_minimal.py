#!/usr/bin/env python3
"""Test minimal backend"""

import requests

def test_minimal():
    try:
        print("Testing minimal backend...")
        response = requests.get("http://localhost:8001/api/status", timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_minimal()
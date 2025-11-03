#!/usr/bin/env python3
"""
Quick test script to test just the extraction part
"""
import requests
import json
import time
from pathlib import Path

API_BASE = "http://localhost:8000/api"

def test_extraction_only():
    print("🧪 Testing Forensic Extract Only")
    print("=" * 40)
    
    # Use existing evidence file
    test_dir = Path("test_files")
    evidence_files = list(test_dir.glob("evidence_*.png"))
    
    if not evidence_files:
        print("❌ No evidence files found. Run full test first.")
        return False
        
    evidence_file = evidence_files[0]
    print(f"📁 Using evidence file: {evidence_file}")
    
    # Test Forensic Extract
    print("\n📤 Testing Forensic Extract...")
    
    with open(evidence_file, "rb") as evidence:
        extract_data = {
            "password": "test123"
        }
        
        files = {
            "stego_file": ("evidence.png", evidence, "image/png")
        }
        
        extract_response = requests.post(f"{API_BASE}/forensic-extract", data=extract_data, files=files)
    
    if extract_response.status_code != 200:
        print(f"❌ Forensic extract failed: {extract_response.status_code}")
        print(f"Response: {extract_response.text}")
        return False
        
    extract_result = extract_response.json()
    extract_operation_id = extract_result.get("operation_id")
    print(f"✅ Forensic extract started: {extract_operation_id}")
    
    # Wait for extraction completion
    print("⏳ Waiting for extract completion...")
    for i in range(30):
        status_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/status")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"Status: {status.get('status')} - {status.get('message', '')}")
            
            if status.get("status") == "completed":
                print("✅ Extract completed!")
                
                # Check result details
                result = status.get("result", {})
                print(f"📊 Is forensic evidence: {result.get('is_forensic_evidence')}")
                if result.get("forensic_metadata"):
                    print(f"📊 Forensic metadata: {result.get('forensic_metadata')}")
                else:
                    print("⚠️  No forensic metadata found")
                break
            elif status.get("status") == "failed":
                print(f"❌ Extract failed: {status.get('error')}")
                return False
                
        time.sleep(1)
    
    return True

if __name__ == "__main__":
    test_extraction_only()
#!/usr/bin/env python3
"""
Test script to debug forensic evidence embedding and extraction
"""
import requests
import json
import os
import time
from pathlib import Path

API_BASE = "http://localhost:8000/api"

def test_forensic_workflow():
    print("🧪 Starting Forensic Evidence Test")
    print("=" * 50)
    
    # Create test files
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create a test carrier image (simple PNG)
    carrier_path = test_dir / "test_carrier.png"
    if not carrier_path.exists():
        # Create a simple 100x100 PNG for testing
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(carrier_path)
            print(f"✅ Created test carrier: {carrier_path}")
        except ImportError:
            print("⚠️  PIL not available, please provide a PNG file manually")
            return False
    
    # Create a test secret file (PDF-like content)
    secret_path = test_dir / "test_secret.pdf"
    with open(secret_path, "wb") as f:
        # Write PDF header to make it look like a real PDF
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
        f.write(b"Test PDF content for forensic evidence testing.")
    print(f"✅ Created test secret file: {secret_path}")
    
    # Test 1: Forensic Embed
    print("\n📤 Testing Forensic Embed...")
    
    with open(carrier_path, "rb") as carrier_file, open(secret_path, "rb") as secret_file:
        # Create forensic metadata as JSON string
        forensic_metadata = {
            "case_id": "TEST001",
            "embedded_owner": "Test User", 
            "timestamp": "2025-11-03T12:00:00",
            "description": "Test forensic evidence embedding",
            "name": "test_secret.pdf",
            "file_size": secret_path.stat().st_size,
            "file_type": "application/pdf",
            "carrier_name": "test_carrier.png",
            "created_by": "test_user@example.com"
        }
        
        embed_data = {
            "forensic_metadata": json.dumps(forensic_metadata),
            "password": "test123"
        }
        
        files = {
            "carrier_file": ("test_carrier.png", carrier_file, "image/png"),
            "content_file": ("test_secret.pdf", secret_file, "application/pdf")
        }
        
        response = requests.post(f"{API_BASE}/forensic-embed", data=embed_data, files=files)
        
    if response.status_code != 200:
        print(f"❌ Forensic embed failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
        
    embed_result = response.json()
    operation_id = embed_result.get("operation_id")
    print(f"✅ Forensic embed started: {operation_id}")
    
    # Wait for completion
    print("⏳ Waiting for embed completion...")
    for i in range(30):  # Wait up to 30 seconds
        status_response = requests.get(f"{API_BASE}/operations/{operation_id}/status")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"Status: {status.get('status')} - {status.get('message', '')}")
            
            if status.get("status") == "completed":
                print("✅ Embed completed successfully!")
                break
            elif status.get("status") == "failed":
                print(f"❌ Embed failed: {status.get('error')}")
                return False
                
        time.sleep(1)
    else:
        print("❌ Embed timed out")
        return False
    
    # Download the forensic evidence file
    print("\n📥 Downloading forensic evidence file...")
    download_response = requests.get(f"{API_BASE}/operations/{operation_id}/download")
    
    if download_response.status_code != 200:
        print(f"❌ Download failed: {download_response.status_code}")
        return False
        
    evidence_file = test_dir / f"evidence_{operation_id}.png"
    with open(evidence_file, "wb") as f:
        f.write(download_response.content)
    print(f"✅ Evidence file saved: {evidence_file}")
    
    # Test 2: Forensic Extract
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
    for i in range(30):  # Wait up to 30 seconds
        status_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/status")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"Status: {status.get('status')} - {status.get('message', '')}")
            
            if status.get("status") == "completed":
                print("✅ Extract completed successfully!")
                
                # Check if forensic metadata was found
                result = status.get("result", {})
                print(f"📊 Result keys: {list(result.keys())}")
                print(f"📊 Is forensic evidence: {result.get('is_forensic_evidence')}")
                if result.get("forensic_metadata"):
                    print(f"📊 Forensic metadata found: {result.get('forensic_metadata')}")
                else:
                    print("⚠️  No forensic metadata in result")
                break
            elif status.get("status") == "failed":
                print(f"❌ Extract failed: {status.get('error')}")
                return False
                
        time.sleep(1)
    else:
        print("❌ Extract timed out")
        return False
    
    # Try to download the extracted ZIP
    print("\n📥 Downloading extracted evidence package...")
    
    # Try forensic download endpoint first
    zip_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/download-forensic")
    if zip_response.status_code != 200:
        print(f"⚠️  Forensic download failed: {zip_response.status_code}, trying standard download")
        zip_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/download")
    
    if zip_response.status_code == 200:
        extracted_file = test_dir / f"extracted_{extract_operation_id}.zip"
        with open(extracted_file, "wb") as f:
            f.write(zip_response.content)
        print(f"✅ Extracted evidence saved: {extracted_file}")
        
        # Check ZIP contents
        try:
            import zipfile
            with zipfile.ZipFile(extracted_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"📦 ZIP contents: {file_list}")
                
                # Check if forensic_metadata.txt exists and read it
                if "forensic_metadata.txt" in file_list:
                    metadata_content = zip_ref.read("forensic_metadata.txt").decode('utf-8')
                    print(f"📄 Metadata content preview:\n{metadata_content[:500]}...")
                else:
                    print("⚠️  No forensic_metadata.txt found in ZIP")
                    
        except Exception as e:
            print(f"⚠️  Could not read ZIP: {e}")
    else:
        print(f"❌ Download failed: {zip_response.status_code}")
        return False
    
    print("\n🎉 Test completed!")
    return True

if __name__ == "__main__":
    try:
        success = test_forensic_workflow()
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Tests failed!")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
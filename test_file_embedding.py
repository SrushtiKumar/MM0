#!/usr/bin/env python3
"""
Test script to reproduce file embedding issues
"""

import requests
import time
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_py_file_embedding():
    """Test embedding .py files in different carriers"""
    
    print("🐍 Testing Python File Embedding")
    print("=" * 40)
    
    # Create a test Python file
    test_py_content = '''#!/usr/bin/env python3
"""
Test Python file for steganography
"""

def hello_world():
    print("Hello from hidden Python file!")
    return "Success"

if __name__ == "__main__":
    hello_world()
'''
    
    test_py_path = "test_hidden.py"
    with open(test_py_path, 'w') as f:
        f.write(test_py_content)
    
    print(f"✅ Created test Python file: {test_py_path}")
    
    # Test with different carriers
    carriers = [
        ("debug_embedded.png", "image", "Image"),
        ("clean_carrier.mp4", "video", "Video"), 
        ("direct_test_audio.wav", "audio", "Audio")
    ]
    
    for carrier_file, carrier_type, carrier_name in carriers:
        if not Path(carrier_file).exists():
            print(f"⏭️ Skipping {carrier_name} - {carrier_file} not found")
            continue
            
        print(f"\n📁 Testing {carrier_name} ({carrier_file})...")
        
        try:
            with open(carrier_file, 'rb') as carrier_f, open(test_py_path, 'rb') as py_f:
                embed_data = {
                    'password': 'test123',
                    'content_type': 'file',
                    'carrier_type': carrier_type
                }
                embed_files = {
                    'carrier_file': (carrier_file, carrier_f),
                    'content_file': (test_py_path, py_f)
                }
                
                response = requests.post(f"{API_BASE}/api/embed", data=embed_data, files=embed_files)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {carrier_name} embedding started: {result['operation_id']}")
                else:
                    print(f"❌ {carrier_name} embedding failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Exception with {carrier_name}: {e}")

def test_doc_file_embedding():
    """Test embedding .doc/.docx files"""
    
    print("\n📄 Testing Document File Embedding")
    print("=" * 40)
    
    # Look for document files
    doc_files = []
    for ext in ['.doc', '.docx', '.pdf']:
        doc_files.extend(Path('.').glob(f'*{ext}'))
    
    if not doc_files:
        print("⏭️ No document files found for testing")
        return
        
    doc_file = str(doc_files[0])
    print(f"📄 Testing with document: {doc_file}")
    
    # Test embedding in image
    carrier_file = "debug_embedded.png"
    if Path(carrier_file).exists():
        try:
            with open(carrier_file, 'rb') as carrier_f, open(doc_file, 'rb') as doc_f:
                embed_data = {
                    'password': 'test123',
                    'content_type': 'file',
                    'carrier_type': 'image'
                }
                embed_files = {
                    'carrier_file': (carrier_file, carrier_f),
                    'content_file': (doc_file, doc_f)
                }
                
                response = requests.post(f"{API_BASE}/api/embed", data=embed_data, files=embed_files)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Document embedding started: {result['operation_id']}")
                else:
                    print(f"❌ Document embedding failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Exception with document: {e}")

if __name__ == "__main__":
    test_py_file_embedding()
    test_doc_file_embedding()
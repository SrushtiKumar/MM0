"""
Quick test to verify the forensic corruption fix
"""

import requests
import json
import time
import zipfile
import os

API_BASE = "http://localhost:8000/api"

def test_forensic_corruption_fix():
    """Test that the forensic file corruption is fixed"""
    
    print("🔧 Testing Forensic Corruption Fix")
    print("=" * 50)
    
    # Create test PDF content
    test_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000100 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
159
%%EOF"""
    
    # Simple carrier image
    carrier_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x64\x00\x00\x00\x64\x08\x06\x00\x00\x00p\xe2\x95!\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x0eIDATx\xdab\x00\x02\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Write test files
    with open('corruption_test.pdf', 'wb') as f:
        f.write(test_pdf)
    
    with open('corruption_carrier.png', 'wb') as f:
        f.write(carrier_png)
    
    try:
        print(f"📋 Original PDF size: {len(test_pdf)} bytes")
        print(f"📋 Original PDF starts with: {test_pdf[:20]}")
        
        # Step 1: Embed
        print("\n📤 Step 1: Embedding PDF...")
        
        forensic_meta = {
            'case_id': 'CORRUPTION-FIX-001',
            'investigator': 'Debug Agent',
            'location': 'Test Suite',
            'description': 'Testing corruption fix',
            'name': 'corruption_test.pdf',
            'file_size': len(test_pdf),
            'file_type': 'application/pdf'
        }
        
        embed_data = {
            'password': 'fixtest123',
            'forensic_metadata': json.dumps(forensic_meta)
        }
        
        files = {
            'carrier_file': ('corruption_carrier.png', open('corruption_carrier.png', 'rb')),
            'content_file': ('corruption_test.pdf', open('corruption_test.pdf', 'rb'))
        }
        
        embed_response = requests.post(f"{API_BASE}/forensic-embed", data=embed_data, files=files)
        
        files['carrier_file'][1].close()
        files['content_file'][1].close()
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.text}")
            return False
        
        embed_result = embed_response.json()
        embed_op_id = embed_result['operation_id']
        
        # Wait for embed
        print("⏳ Waiting for embed completion...")
        for _ in range(20):
            status = requests.get(f"{API_BASE}/status/{embed_op_id}").json()
            if status['status'] == 'completed':
                break
            elif status['status'] == 'failed':
                print(f"❌ Embed failed: {status.get('message')}")
                return False
            time.sleep(1)
        
        # Download stego file
        stego_response = requests.get(f"{API_BASE}/download/{embed_op_id}")
        with open('corruption_stego.png', 'wb') as f:
            f.write(stego_response.content)
        
        print("✅ Embed completed!")
        
        # Step 2: Extract  
        print("\n📥 Step 2: Extracting PDF...")
        
        extract_data = {
            'password': 'fixtest123',
            'output_format': 'forensic'
        }
        
        files = {
            'stego_file': ('corruption_stego.png', open('corruption_stego.png', 'rb'))
        }
        
        extract_response = requests.post(f"{API_BASE}/forensic-extract", data=extract_data, files=files)
        files['stego_file'][1].close()
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_op_id = extract_result['operation_id']
        
        # Wait for extract
        print("⏳ Waiting for extract completion...")
        for _ in range(20):
            status = requests.get(f"{API_BASE}/status/{extract_op_id}").json()
            print(f"  Status: {status['status']} - {status.get('message', '')}")
            if status['status'] == 'completed':
                break
            elif status['status'] == 'failed':
                print(f"❌ Extract failed: {status.get('message')}")
                return False
            time.sleep(1)
        
        # Download ZIP
        zip_response = requests.get(f"{API_BASE}/download/{extract_op_id}")
        with open('corruption_extracted.zip', 'wb') as f:
            f.write(zip_response.content)
        
        print("✅ Extract completed!")
        
        # Step 3: Verify integrity
        print("\n🔍 Step 3: Verifying file integrity...")
        
        with zipfile.ZipFile('corruption_extracted.zip', 'r') as zf:
            files_in_zip = zf.namelist()
            print(f"Files in ZIP: {files_in_zip}")
            
            # Find the PDF
            pdf_files = [f for f in files_in_zip if f.endswith('.pdf')]
            if not pdf_files:
                print("❌ No PDF found in ZIP!")
                return False
            
            pdf_name = pdf_files[0]
            extracted_pdf = zf.read(pdf_name)
            
            print(f"📋 Extracted PDF size: {len(extracted_pdf)} bytes")
            print(f"📋 Extracted PDF starts with: {extracted_pdf[:20]}")
            
            # Compare
            if extracted_pdf == test_pdf:
                print("🎉 ✅ SUCCESS! PDF integrity preserved - corruption FIXED!")
                return True
            else:
                print("❌ CORRUPTION: PDFs don't match")
                print(f"  Original hash: {hash(test_pdf)}")
                print(f"  Extracted hash: {hash(extracted_pdf)}")
                return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for f in ['corruption_test.pdf', 'corruption_carrier.png', 'corruption_stego.png', 'corruption_extracted.zip']:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

if __name__ == "__main__":
    success = test_forensic_corruption_fix()
    if success:
        print("\n🎯 CORRUPTION FIX VERIFIED!")
    else:
        print("\n❌ Corruption still exists - check debug logs")
        print("Look for '[FORENSIC EXTRACT DEBUG]' messages in server terminal")
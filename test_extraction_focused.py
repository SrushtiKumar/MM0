"""
Test extraction specifically - use the embedded file from the server logs
"""

import requests
import json
import time
import zipfile
import os

API_BASE = "http://localhost:8000/api"

def test_extraction_corruption():
    """Test extraction of the file that was just embedded"""
    
    print("🔍 Testing Extraction Corruption")
    print("=" * 50)
    
    # Since we saw successful embedding, let's test extraction with a fresh embed
    
    # Create test files
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT/F1 12 Tf 72 720 Td(Corruption Test)Tj ET
endstream endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref
297
%%EOF"""
    
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x14\xa3\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open('extract_test.pdf', 'wb') as f:
        f.write(pdf_content)
    with open('extract_carrier.png', 'wb') as f:
        f.write(png_data)
    
    try:
        print(f"📤 Step 1: Embedding test PDF ({len(pdf_content)} bytes)...")
        
        forensic_metadata = {
            'case_id': 'EXTRACT-TEST-001',
            'investigator': 'Extract Debugger',
            'location': 'Corruption Lab',
            'description': 'Testing extraction corruption fix',
            'name': 'extract_test.pdf',
            'file_size': len(pdf_content),
            'file_type': 'application/pdf'
        }
        
        embed_data = {
            'password': 'extract123',
            'encryption_type': 'AES',
            'forensic_metadata': json.dumps(forensic_metadata)
        }
        
        files = {
            'carrier_file': ('extract_carrier.png', open('extract_carrier.png', 'rb'), 'image/png'),
            'content_file': ('extract_test.pdf', open('extract_test.pdf', 'rb'), 'application/pdf')
        }
        
        embed_response = requests.post(f"{API_BASE}/forensic-embed", data=embed_data, files=files)
        files['carrier_file'][1].close()
        files['content_file'][1].close()
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.text}")
            return False
        
        embed_result = embed_response.json()
        operation_id = embed_result['operation_id']
        print(f"✅ Embed operation: {operation_id}")
        
        # Wait for embedding
        for i in range(15):
            try:
                status_response = requests.get(f"{API_BASE}/operations/{operation_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"  Embed: {status['status']} - {status.get('message', '')}")
                    if status['status'] == 'completed':
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Embed failed: {status.get('message', 'Unknown error')}")
                        return False
            except:
                pass
            time.sleep(1)
        
        # Get final status to get filename
        final_status_response = requests.get(f"{API_BASE}/operations/{operation_id}/status")
        if final_status_response.status_code == 200:
            final_status = final_status_response.json()
            filename = final_status.get('result', {}).get('filename', f"{operation_id}_output.png")
        else:
            filename = f"{operation_id}_output.png"  # fallback
        
        # Download embedded file
        download_response = requests.get(f"{API_BASE}/download/{filename}")
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
        
        with open('extract_stego.png', 'wb') as f:
            f.write(download_response.content)
        print("✅ Embedded file downloaded")
        
        # NOW TEST EXTRACTION - This is where corruption likely happens
        print(f"\n📥 Step 2: Extracting PDF (watch server logs for corruption indicators)...")
        
        extract_data = {
            'password': 'extract123',
            'output_format': 'forensic'
        }
        
        files = {
            'stego_file': ('extract_stego.png', open('extract_stego.png', 'rb'), 'image/png')
        }
        
        extract_response = requests.post(f"{API_BASE}/forensic-extract", data=extract_data, files=files)
        files['stego_file'][1].close()
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_operation_id = extract_result['operation_id']
        print(f"✅ Extract operation: {extract_operation_id}")
        
        # Wait for extraction
        for i in range(15):
            try:
                status_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"  Extract: {status['status']} - {status.get('message', '')}")
                    if status['status'] == 'completed':
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Extract failed: {status.get('message', 'Unknown error')}")
                        return False
            except:
                pass
            time.sleep(1)
        
        # Get final status to get ZIP filename
        final_extract_status_response = requests.get(f"{API_BASE}/operations/{extract_operation_id}/status")
        if final_extract_status_response.status_code == 200:
            final_extract_status = final_extract_status_response.json()
            zip_filename = final_extract_status.get('result', {}).get('filename', f"{extract_operation_id}_forensic_evidence_package.zip")
        else:
            zip_filename = f"{extract_operation_id}_forensic_evidence_package.zip"  # fallback
        
        # Download and analyze ZIP
        zip_response = requests.get(f"{API_BASE}/download/{zip_filename}")
        if zip_response.status_code != 200:
            print(f"❌ ZIP download failed: {zip_response.status_code}")
            return False
        
        with open('extracted_forensic.zip', 'wb') as f:
            f.write(zip_response.content)
        print("✅ Forensic ZIP downloaded")
        
        # ANALYZE CORRUPTION
        print(f"\n🔍 Step 3: Analyzing corruption...")
        
        with zipfile.ZipFile('extracted_forensic.zip', 'r') as zip_file:
            files_in_zip = zip_file.namelist()
            print(f"Files in ZIP: {files_in_zip}")
            
            pdf_files = [f for f in files_in_zip if f.endswith('.pdf')]
            if pdf_files:
                pdf_name = pdf_files[0]
                extracted_pdf = zip_file.read(pdf_name)
                
                print(f"\n📊 CORRUPTION ANALYSIS:")
                print(f"Original PDF size: {len(pdf_content)} bytes")
                print(f"Extracted PDF size: {len(extracted_pdf)} bytes")
                print(f"Original starts: {pdf_content[:20]}")
                print(f"Extracted starts: {extracted_pdf[:20]}")
                
                if extracted_pdf == pdf_content:
                    print("✅ NO CORRUPTION - Files match perfectly!")
                    return True
                else:
                    print("❌ CORRUPTION DETECTED:")
                    
                    # Find first difference
                    for i, (orig, extr) in enumerate(zip(pdf_content, extracted_pdf)):
                        if orig != extr:
                            print(f"   First difference at byte {i}: {orig} vs {extr}")
                            break
                    
                    # Check if it's a length issue
                    if len(extracted_pdf) != len(pdf_content):
                        print(f"   Length mismatch: {len(pdf_content)} vs {len(extracted_pdf)}")
                    
                    return False
            else:
                print("❌ No PDF found in ZIP")
                return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for f in ['extract_test.pdf', 'extract_carrier.png', 'extract_stego.png', 'extracted_forensic.zip']:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    print("🧪 FOCUSED EXTRACTION CORRUPTION TEST")
    print("Watch the server terminal for detailed debug output!")
    print("This will show exactly where corruption happens in extraction.\n")
    
    success = test_extraction_corruption()
    
    if success:
        print("\n🎉 SUCCESS: No corruption detected!")
    else:
        print("\n🔍 CORRUPTION FOUND: Check server debug logs for details")
        print("Look for:")
        print("- [FORENSIC EXTRACT DEBUG] messages")
        print("- Base64 decode errors")
        print("- Binary data mismatches")
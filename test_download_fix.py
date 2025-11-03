"""
Test the forensic download fix - verify PDF is not corrupted
"""

import requests
import json
import time
import zipfile
import os
import hashlib

API_BASE = "http://localhost:8000/api"

def test_forensic_download_fix():
    """Test that the forensic download now serves the correct ZIP with uncorrupted PDF"""
    
    print("🔧 Testing Forensic Download Fix")
    print("=" * 50)
    
    # Create a proper PDF for testing
    pdf_content = b"""%PDF-1.7

4 0 obj
(Identity)
endobj
5 0 obj
(Adobe)
endobj
8 0 obj
<<
/Filter /FlateDecode
/Length 265
>>
stream
x\x9c5\x8e\xc1\n\x830\x10D\xef\xfa\x15\x83wP\xdb\xed\xd5\xd0\xf6\x05\x9a\xe8\x0f\xd8E\x9b\x88\x8d\x89\xc5\xb2\xef\xdf8\xe9\xa6\x87\x81\x99<3\x8f\x9c\x13n\x8d\x0c\xa7\x83,\x8b\xdf\x83\x9e\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3\x83\xff\xe3
endstream
endobj
9 0 obj
<<
/Type /Page
/Parent 1 0 R
/MediaBox [0 0 612 792]
/Contents 8 0 R
>>
endobj
1 0 obj
<<
/Type /Pages
/Kids [9 0 R]
/Count 1
>>
endobj
2 0 obj
<<
/Type /Catalog
/Pages 1 0 R
>>
endobj
xref
0 10
0000000000 65535 f 
0000000562 00000 n 
0000000619 00000 n 
0000000000 65535 f 
0000000009 00000 n 
0000000031 00000 n 
0000000000 65535 f 
0000000000 65535 f 
0000000053 00000 n 
0000000386 00000 n 
trailer
<<
/Size 10
/Root 2 0 R
>>
startxref
668
%%EOF"""
    
    # Simple carrier PNG
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x14\xa3\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Write test files
    with open('download_fix_test.pdf', 'wb') as f:
        f.write(pdf_content)
    with open('download_fix_carrier.png', 'wb') as f:
        f.write(png_data)
    
    original_hash = hashlib.md5(pdf_content).hexdigest()
    print(f"📋 Original PDF: {len(pdf_content)} bytes, MD5: {original_hash}")
    
    try:
        # Step 1: Embed
        print("\n📤 Step 1: Embedding PDF...")
        
        forensic_metadata = {
            'case_id': 'DOWNLOAD-FIX-001',
            'investigator': 'Fix Tester',
            'location': 'Download Fix Lab',
            'description': 'Testing download corruption fix',
            'name': 'download_fix_test.pdf',
            'file_size': len(pdf_content),
            'file_type': 'application/pdf'
        }
        
        embed_data = {
            'password': 'downloadfix123',
            'forensic_metadata': json.dumps(forensic_metadata)
        }
        
        files = {
            'carrier_file': ('download_fix_carrier.png', open('download_fix_carrier.png', 'rb')),
            'content_file': ('download_fix_test.pdf', open('download_fix_test.pdf', 'rb'))
        }
        
        embed_response = requests.post(f"{API_BASE}/forensic-embed", data=embed_data, files=files)
        files['carrier_file'][1].close()
        files['content_file'][1].close()
        
        if embed_response.status_code != 200:
            print(f"❌ Embed failed: {embed_response.text}")
            return False
        
        embed_result = embed_response.json()
        embed_op_id = embed_result['operation_id']
        print(f"✅ Embed operation: {embed_op_id}")
        
        # Wait for embed
        for _ in range(15):
            try:
                status_response = requests.get(f"{API_BASE}/operations/{embed_op_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    if status['status'] == 'completed':
                        print("✅ Embed completed")
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Embed failed: {status.get('message')}")
                        return False
            except:
                pass
            time.sleep(1)
        
        # Download embedded file
        embed_final_status = requests.get(f"{API_BASE}/operations/{embed_op_id}/status").json()
        embed_filename = embed_final_status.get('result', {}).get('filename')
        
        embed_download = requests.get(f"{API_BASE}/download/{embed_filename}")
        with open('download_fix_stego.png', 'wb') as f:
            f.write(embed_download.content)
        print("✅ Embedded file downloaded")
        
        # Step 2: Extract
        print("\n📥 Step 2: Extracting with fixed download...")
        
        extract_data = {
            'password': 'downloadfix123',
            'output_format': 'forensic'
        }
        
        files = {
            'stego_file': ('download_fix_stego.png', open('download_fix_stego.png', 'rb'))
        }
        
        extract_response = requests.post(f"{API_BASE}/forensic-extract", data=extract_data, files=files)
        files['stego_file'][1].close()
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.text}")
            return False
        
        extract_result = extract_response.json()
        extract_op_id = extract_result['operation_id']
        print(f"✅ Extract operation: {extract_op_id}")
        
        # Wait for extract
        for _ in range(15):
            try:
                status_response = requests.get(f"{API_BASE}/operations/{extract_op_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    if status['status'] == 'completed':
                        print("✅ Extract completed")
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Extract failed: {status.get('message')}")
                        return False
            except:
                pass
            time.sleep(1)
        
        # Step 3: Test the FIXED download
        print("\n📥 Step 3: Testing fixed forensic download...")
        
        # Use the forensic download endpoint that we just fixed
        forensic_zip_response = requests.get(f"{API_BASE}/operations/{extract_op_id}/download-forensic")
        
        if forensic_zip_response.status_code != 200:
            print(f"❌ Forensic download failed: {forensic_zip_response.status_code}")
            return False
        
        # Save the ZIP
        with open('download_fixed_forensic.zip', 'wb') as f:
            f.write(forensic_zip_response.content)
        
        print("✅ Forensic ZIP downloaded with fixed endpoint")
        
        # Step 4: Verify the PDF inside is NOT corrupted
        print("\n🔍 Step 4: Verifying PDF integrity...")
        
        with zipfile.ZipFile('download_fixed_forensic.zip', 'r') as zf:
            files_in_zip = zf.namelist()
            print(f"Files in ZIP: {files_in_zip}")
            
            pdf_files = [f for f in files_in_zip if f.endswith('.pdf')]
            if not pdf_files:
                print("❌ No PDF found in ZIP!")
                return False
            
            pdf_name = pdf_files[0]
            extracted_pdf = zf.read(pdf_name)
            extracted_hash = hashlib.md5(extracted_pdf).hexdigest()
            
            print(f"📋 Extracted PDF: {len(extracted_pdf)} bytes, MD5: {extracted_hash}")
            
            if extracted_pdf == pdf_content:
                print("🎉 ✅ SUCCESS! PDF is PERFECT - Download fix works!")
                print(f"✅ Size match: {len(pdf_content)} == {len(extracted_pdf)}")
                print(f"✅ Hash match: {original_hash} == {extracted_hash}")
                
                # Try to save and check if it's openable
                with open('verified_fixed_pdf.pdf', 'wb') as f:
                    f.write(extracted_pdf)
                print("✅ PDF saved as 'verified_fixed_pdf.pdf' - try opening it!")
                
                return True
            else:
                print("❌ CORRUPTION: PDFs still don't match")
                print(f"  Size: {len(pdf_content)} vs {len(extracted_pdf)}")
                print(f"  Hash: {original_hash} vs {extracted_hash}")
                return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        cleanup_files = [
            'download_fix_test.pdf', 'download_fix_carrier.png', 
            'download_fix_stego.png', 'download_fixed_forensic.zip'
        ]
        for f in cleanup_files:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    print("🧪 FORENSIC DOWNLOAD CORRUPTION FIX TEST")
    print("This tests the fix for the download endpoint that was serving corrupted ZIPs\n")
    
    success = test_forensic_download_fix()
    
    if success:
        print("\n🎯 DOWNLOAD FIX VERIFIED!")
        print("The forensic download endpoint now serves uncorrupted PDF files!")
    else:
        print("\n❌ Download still corrupted - needs more investigation")
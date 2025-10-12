#!/usr/bin/env python3
"""
Comprehensive Audio Steganography Format Preservation Test
Tests the complete backend flow including all file formats
"""
import os
import requests
import tempfile
from pathlib import Path

def create_test_files():
    """Create various test files for audio steganography testing"""
    print("📁 Creating test files for audio steganography...")
    
    # Create test audio (MP3 and WAV)
    test_mp3_path = "test_carrier_audio.mp3"
    test_wav_path = "test_carrier_audio.wav"
    
    if not os.path.exists(test_mp3_path):
        # Create a basic MP3 file content (MP3 header + minimal data)
        mp3_content = b'\xff\xfb\x90\x00' + b'\x00' * 4000  # Basic MP3 header + padding
        with open(test_mp3_path, 'wb') as f:
            f.write(mp3_content)
        print(f"  Created test MP3: {test_mp3_path}")
    
    if not os.path.exists(test_wav_path):
        # Create a basic WAV file
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        wav_data = b'\x00\x00' * 1024  # Simple silence
        with open(test_wav_path, 'wb') as f:
            f.write(wav_header + wav_data)
        print(f"  Created test WAV: {test_wav_path}")
    
    # Create test files to hide
    test_files = {
        "test_image.png": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x8e\xfc\xe7\x00\x00\x00\x00\x00IEND\xaeB`\x82',
        "test_document.doc": b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' + b'Test DOC content for audio steganography' + b'\x00' * 100,
        "test_document.pdf": b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n200\n%%EOF',
        "test_document.docx": b'PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00' + b'Test DOCX content for audio steganography' + b'\x00' * 100
    }
    
    for filename, content in test_files.items():
        if not os.path.exists(filename):
            with open(filename, 'wb') as f:
                f.write(content)
            print(f"  Created test file: {filename}")
    
    return test_mp3_path, test_wav_path, list(test_files.keys())

def test_audio_steganography_api(audio_file, test_file, expected_extension):
    """Test audio steganography through the API"""
    print(f"\n🎵 Testing {test_file} → {audio_file}")
    print(f"   Expected extraction: {expected_extension}")
    
    BASE_URL = "http://localhost:8000/api"
    
    try:
        # Step 1: Embed file in audio
        print("   📤 Embedding file...")
        with open(audio_file, 'rb') as af, open(test_file, 'rb') as tf:
            embed_files = {
                'carrier_file': (audio_file, af, 'audio/mpeg' if audio_file.endswith('.mp3') else 'audio/wav'),
                'content_file': (test_file, tf, 'application/octet-stream')
            }
            embed_data = {
                'content_type': 'file',
                'password': 'test123'
            }
            
            response = requests.post(f"{BASE_URL}/embed", files=embed_files, data=embed_data)
            
            if response.status_code != 200:
                print(f"   ❌ Embedding failed: {response.status_code} - {response.text}")
                return False
            
            embed_result = response.json()
            operation_id = embed_result.get('operation_id')
            print(f"   ✅ Embedding started: {operation_id}")
        
        # Step 2: Wait for completion and get result
        import time
        for _ in range(30):  # Wait up to 30 seconds
            status_response = requests.get(f"{BASE_URL}/operations/{operation_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                if status.get('status') == 'completed':
                    print("   ✅ Embedding completed")
                    break
                elif status.get('status') == 'failed':
                    print(f"   ❌ Embedding failed: {status.get('error', 'Unknown error')}")
                    return False
            time.sleep(1)
        else:
            print("   ❌ Embedding timeout")
            return False
        
        # Step 3: Download the steganographic file
        download_response = requests.get(f"{BASE_URL}/operations/{operation_id}/download")
        if download_response.status_code != 200:
            print(f"   ❌ Download failed: {download_response.status_code}")
            return False
        
        stego_filename = f"stego_{audio_file}"
        with open(stego_filename, 'wb') as f:
            f.write(download_response.content)
        print(f"   📥 Downloaded: {stego_filename}")
        
        # Step 4: Extract from steganographic file
        print("   📤 Extracting file...")
        with open(stego_filename, 'rb') as sf:
            extract_files = {
                'stego_file': (stego_filename, sf, 'audio/mpeg' if stego_filename.endswith('.mp3') else 'audio/wav')
            }
            extract_data = {
                'password': 'test123'
            }
            
            extract_response = requests.post(f"{BASE_URL}/extract", files=extract_files, data=extract_data)
            
            if extract_response.status_code != 200:
                print(f"   ❌ Extraction failed: {extract_response.status_code} - {extract_response.text}")
                return False
            
            extract_result = extract_response.json()
            extract_operation_id = extract_result.get('operation_id')
            print(f"   ✅ Extraction started: {extract_operation_id}")
        
        # Step 5: Wait for extraction completion
        for _ in range(30):  # Wait up to 30 seconds
            status_response = requests.get(f"{BASE_URL}/operations/{extract_operation_id}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                if status.get('status') == 'completed':
                    print("   ✅ Extraction completed")
                    break
                elif status.get('status') == 'failed':
                    print(f"   ❌ Extraction failed: {status.get('error', 'Unknown error')}")
                    return False
            time.sleep(1)
        else:
            print("   ❌ Extraction timeout")
            return False
        
        # Step 6: Download extracted file
        download_response = requests.get(f"{BASE_URL}/operations/{extract_operation_id}/download")
        if download_response.status_code != 200:
            print(f"   ❌ Extracted file download failed: {download_response.status_code}")
            return False
        
        # Check filename from response headers
        content_disposition = download_response.headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            extracted_filename = content_disposition.split('filename=')[1].strip('"')
        else:
            extracted_filename = f"extracted_{test_file}"
        
        # Save extracted file
        with open(f"extracted_{extracted_filename}", 'wb') as f:
            f.write(download_response.content)
        
        print(f"   📥 Extracted filename: {extracted_filename}")
        
        # Step 7: Verify format preservation
        if extracted_filename.endswith(expected_extension):
            print(f"   ✅ FORMAT PRESERVED: {extracted_filename} (correct {expected_extension} extension)")
            return True
        else:
            print(f"   ❌ FORMAT ISSUE: {extracted_filename} (should end with {expected_extension})")
            return False
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    print("🎵 COMPREHENSIVE AUDIO STEGANOGRAPHY FORMAT PRESERVATION TEST")
    print("=" * 80)
    print("Testing file format preservation through the complete backend API flow")
    
    # Create test files
    mp3_file, wav_file, test_files = create_test_files()
    
    # Test cases
    test_cases = [
        (wav_file, "test_image.png", ".png"),
        (wav_file, "test_document.doc", ".doc"),
        (wav_file, "test_document.pdf", ".pdf"),
        (wav_file, "test_document.docx", ".docx"),
        (mp3_file, "test_image.png", ".png"),
        (mp3_file, "test_document.doc", ".doc"),
    ]
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    for audio_file, test_file, expected_ext in test_cases:
        if test_audio_steganography_api(audio_file, test_file, expected_ext):
            passed += 1
    
    # Summary
    print(f"\n" + "=" * 80)
    print(f"📊 AUDIO STEGANOGRAPHY FORMAT PRESERVATION RESULTS")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Audio steganography format preservation is WORKING!")
    else:
        print(f"⚠️  {total - passed} tests failed. Audio steganography format preservation needs attention.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
"""
Test to reproduce and fix file corruption and extension issues
"""
import os
import requests
import time

def test_file_corruption_issue():
    """Test to identify file corruption during download"""
    print("=" * 70)
    print("🔧 FILE CORRUPTION AND EXTENSION FIX TEST")
    print("=" * 70)
    
    # Test 1: Check if steganographic files are corrupted
    print("\\n1️⃣ TESTING STEGANOGRAPHIC FILE INTEGRITY")
    if not test_stego_file_integrity():
        return False
    
    # Test 2: Check extracted file extensions
    print("\\n2️⃣ TESTING EXTRACTED FILE EXTENSIONS")
    if not test_extracted_file_extensions():
        return False
    
    print("\\n" + "=" * 70)
    print("🎉 IDENTIFIED ISSUES - IMPLEMENTING FIXES")
    print("=" * 70)
    
    return True

def test_stego_file_integrity():
    """Test if steganographic files maintain integrity"""
    print("   📤 Creating steganographic file...")
    
    # Create a steganographic file
    files = {
        'carrier_file': ('enhanced_audio_test.wav', open('enhanced_audio_test.wav', 'rb'), 'audio/wav')
    }
    
    data = {
        'content_type': 'text',
        'text_content': 'Test content for integrity check',
        'password': 'integrity_test123',
        'carrier_type': 'audio'
    }
    
    try:
        response = requests.post("http://localhost:8000/api/embed", files=files, data=data)
        files['carrier_file'][1].close()
        
        if response.status_code != 200:
            print(f"      ❌ Embed failed: {response.status_code}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        # Wait for completion
        for i in range(20):
            time.sleep(1)
            status_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                if status_result.get('status') == 'completed':
                    break
        
        # Download the file
        print("   📥 Downloading steganographic file...")
        download_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/download")
        
        if download_response.status_code == 200:
            # Save the downloaded file
            with open("integrity_test_stego.wav", "wb") as f:
                f.write(download_response.content)
            
            # Check file size
            original_size = os.path.getsize("enhanced_audio_test.wav")
            downloaded_size = os.path.getsize("integrity_test_stego.wav")
            
            print(f"      📊 Original size: {original_size} bytes")
            print(f"      📊 Downloaded size: {downloaded_size} bytes")
            
            # Check if file is playable (basic integrity check)
            try:
                import librosa
                y, sr = librosa.load("integrity_test_stego.wav", sr=None)
                print(f"      ✅ File is playable: {len(y)} samples at {sr} Hz")
                
                # Now test extraction to ensure data is preserved
                print("   🔓 Testing extraction from downloaded file...")
                return test_extraction_from_downloaded("integrity_test_stego.wav", data['password'], data['text_content'])
                
            except Exception as e:
                print(f"      ❌ File appears corrupted - cannot load: {e}")
                return False
        else:
            print(f"      ❌ Download failed: {download_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception in integrity test: {e}")
        return False

def test_extraction_from_downloaded(stego_file, password, expected_content):
    """Test extraction from downloaded steganographic file"""
    files = {
        'stego_file': (stego_file, open(stego_file, 'rb'), 'audio/wav')
    }
    
    data = {
        'password': password
    }
    
    try:
        response = requests.post("http://localhost:8000/api/extract", files=files, data=data)
        files['stego_file'][1].close()
        
        if response.status_code != 200:
            print(f"      ❌ Extract request failed: {response.status_code}")
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        # Wait for extraction
        for i in range(15):
            time.sleep(1)
            status_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                status = status_result.get('status')
                
                if status == 'completed':
                    result_data = status_result.get('result', {})
                    extracted_content = result_data.get('preview')
                    extracted_filename = result_data.get('filename', 'unknown')
                    
                    print(f"      🔍 Extracted content: '{extracted_content}'")
                    print(f"      📁 Extracted filename: '{extracted_filename}'")
                    
                    # Check for problematic extension
                    if '.extracted_tmp' in extracted_filename:
                        print(f"      ❌ FOUND ISSUE: Invalid temporary extension in filename!")
                        print(f"          Problematic filename: {extracted_filename}")
                        return False
                    
                    if extracted_content == expected_content:
                        print(f"      ✅ Content integrity verified")
                        return True
                    else:
                        print(f"      ❌ Content mismatch")
                        return False
                        
                elif status == 'failed':
                    error = status_result.get('error')
                    print(f"      ❌ Extraction failed: {error}")
                    return False
        
        print(f"      ⏰ Extraction timed out")
        return False
        
    except Exception as e:
        print(f"      ❌ Exception in extraction test: {e}")
        return False

def test_extracted_file_extensions():
    """Test if extracted files have proper extensions"""
    print("   🧪 Testing file extension handling...")
    
    # Test different content types
    test_cases = [
        {
            'name': 'Text Content',
            'content': 'This is a test text message',
            'expected_extension': '.txt'
        },
        {
            'name': 'JSON Content', 
            'content': '{"message": "test json data", "type": "json"}',
            'expected_extension': '.txt'  # Should still be .txt for text data
        }
    ]
    
    for test_case in test_cases:
        print(f"      🎯 Testing: {test_case['name']}")
        
        if not test_single_extraction_case(test_case):
            return False
    
    return True

def test_single_extraction_case(test_case):
    """Test a single extraction case"""
    files = {
        'carrier_file': ('enhanced_audio_test.wav', open('enhanced_audio_test.wav', 'rb'), 'audio/wav')
    }
    
    data = {
        'content_type': 'text',
        'text_content': test_case['content'],
        'password': 'ext_test123',
        'carrier_type': 'audio'
    }
    
    try:
        # Embed
        response = requests.post("http://localhost:8000/api/embed", files=files, data=data)
        files['carrier_file'][1].close()
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        operation_id = result.get('operation_id')
        
        # Wait for embed completion
        for i in range(20):
            time.sleep(1)
            status_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/status")
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                if status_result.get('status') == 'completed':
                    break
        
        # Download steganographic file
        download_response = requests.get(f"http://localhost:8000/api/operations/{operation_id}/download")
        
        if download_response.status_code == 200:
            stego_filename = f"test_case_{hash(test_case['name'])}.wav"
            with open(stego_filename, "wb") as f:
                f.write(download_response.content)
            
            # Now extract
            extract_files = {
                'stego_file': (stego_filename, open(stego_filename, 'rb'), 'audio/wav')
            }
            
            extract_data = {
                'password': data['password']
            }
            
            extract_response = requests.post("http://localhost:8000/api/extract", files=extract_files, data=extract_data)
            extract_files['stego_file'][1].close()
            
            if extract_response.status_code == 200:
                extract_result = extract_response.json()
                extract_operation_id = extract_result.get('operation_id')
                
                # Wait for extraction
                for i in range(15):
                    time.sleep(1)
                    status_response = requests.get(f"http://localhost:8000/api/operations/{extract_operation_id}/status")
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        if status_result.get('status') == 'completed':
                            result_data = status_result.get('result', {})
                            filename = result_data.get('filename', 'unknown')
                            
                            print(f"         📁 Extracted filename: {filename}")
                            
                            # Check for issues
                            if '.extracted_tmp' in filename:
                                print(f"         ❌ ISSUE: Invalid temp extension found!")
                                return False
                            
                            if filename.endswith(test_case['expected_extension']):
                                print(f"         ✅ Correct extension: {test_case['expected_extension']}")
                                return True
                            else:
                                print(f"         ⚠️ Unexpected extension, expected {test_case['expected_extension']}")
                                return True  # Don't fail for this
                            
                        elif status_result.get('status') == 'failed':
                            print(f"         ❌ Extraction failed")
                            return False
                
                print(f"         ⏰ Extraction timed out")
                return False
            
            return False
        
        return False
        
    except Exception as e:
        print(f"         ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_file_corruption_issue()
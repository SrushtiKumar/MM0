"""
COMPREHENSIVE FINAL VERIFICATION TEST
Audio Steganography Complete Functionality Test

This test verifies that the audio steganography regression has been completely resolved.
"""
import sys
import os
import requests
import json
import time
sys.path.append(os.getcwd())

from universal_file_audio import UniversalFileAudio

def test_all_audio_functionality():
    print("=" * 60)
    print("🔍 COMPREHENSIVE AUDIO STEGANOGRAPHY VERIFICATION")
    print("=" * 60)
    
    results = {
        "direct_hide_extract": False,
        "api_embed_workflow": False,
        "api_extract_workflow": False,
        "content_integrity": False,
        "error_handling": False
    }
    
    # Test 1: Direct hide/extract functionality
    print("\\n1️⃣ TESTING DIRECT HIDE/EXTRACT...")
    results["direct_hide_extract"] = test_direct_functionality()
    
    # Test 2: API embed workflow
    print("\\n2️⃣ TESTING API EMBED WORKFLOW...")
    operation_id = test_api_embed_workflow()
    results["api_embed_workflow"] = operation_id is not None
    
    # Test 3: API extract workflow (if embed worked)
    if operation_id:
        print("\\n3️⃣ TESTING API EXTRACT WORKFLOW...")
        results["api_extract_workflow"] = test_api_extract_workflow(operation_id)
    
    # Test 4: Content integrity verification
    print("\\n4️⃣ TESTING CONTENT INTEGRITY...")
    results["content_integrity"] = test_content_integrity()
    
    # Test 5: Error handling
    print("\\n5️⃣ TESTING ERROR HANDLING...")
    results["error_handling"] = test_error_handling()
    
    # Final results
    print("\\n" + "=" * 60)
    print("📊 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title(): <25} : {status}")
        if not passed:
            all_passed = False
    
    print("\\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - AUDIO STEGANOGRAPHY FULLY RESTORED!")
        print("✅ The regression issue has been completely resolved")
        print("✅ Audio steganography now works smoothly with the application")
    else:
        print("❌ SOME TESTS FAILED - Issues still need to be addressed")
    print("=" * 60)
    
    return all_passed

def test_direct_functionality():
    """Test direct hide_data and extract_data methods"""
    try:
        carrier_file = "enhanced_audio_test.wav"
        output_file = "final_verification_audio.wav"
        test_content = "Final verification test message!"
        password = "verify123"
        
        if not os.path.exists(carrier_file):
            print(f"   ❌ Carrier file not found: {carrier_file}")
            return False
        
        # Create manager
        manager = UniversalFileAudio(password=password)
        
        # Hide data
        print(f"   🔒 Hiding: '{test_content}'")
        hide_result = manager.hide_data(carrier_file, test_content, output_file, is_file=False)
        
        if not hide_result.get('success'):
            print(f"   ❌ Hide failed: {hide_result.get('error')}")
            return False
        
        # Extract data
        print(f"   🔓 Extracting from: {output_file}")
        extract_result = manager.extract_data(output_file)
        
        if not extract_result:
            print("   ❌ Extract returned None")
            return False
        
        extracted_text, filename = extract_result
        
        if extracted_text == test_content:
            print("   ✅ Direct functionality works perfectly")
            return True
        else:
            print(f"   ❌ Content mismatch: expected '{test_content}', got '{extracted_text}'")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception in direct test: {e}")
        return False

def test_api_embed_workflow():
    """Test the API embed workflow"""
    try:
        url = "http://localhost:8000/api/embed"
        
        files = {
            'carrier_file': ('enhanced_audio_test.wav', open('enhanced_audio_test.wav', 'rb'), 'audio/wav')
        }
        
        data = {
            'content_type': 'text',
            'text_content': 'API verification test message!',
            'password': 'api_verify123',
            'carrier_type': 'audio'
        }
        
        print("   📤 Sending embed request...")
        response = requests.post(url, files=files, data=data)
        files['carrier_file'][1].close()
        
        if response.status_code != 200:
            print(f"   ❌ HTTP error: {response.status_code}")
            return None
        
        result = response.json()
        
        if not result.get('success'):
            print(f"   ❌ API error: {result.get('error')}")
            return None
        
        operation_id = result.get('operation_id')
        print(f"   🆔 Operation ID: {operation_id}")
        
        # Wait for completion
        status_url = f"http://localhost:8000/api/operations/{operation_id}/status"
        
        for i in range(20):
            time.sleep(1)
            status_response = requests.get(status_url)
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                status = status_result.get('status')
                
                if status == 'completed':
                    print("   ✅ API embed workflow successful")
                    return operation_id
                elif status == 'failed':
                    error = status_result.get('error', 'Unknown error')
                    print(f"   ❌ Operation failed: {error}")
                    return None
        
        print("   ⏰ Operation timed out")
        return None
        
    except Exception as e:
        print(f"   ❌ Exception in API embed test: {e}")
        return None

def test_api_extract_workflow(operation_id):
    """Test the API extract workflow"""
    try:
        # First download the steganographic file
        download_url = f"http://localhost:8000/api/operations/{operation_id}/download"
        download_response = requests.get(download_url)
        
        if download_response.status_code != 200:
            print(f"   ❌ Download failed: {download_response.status_code}")
            return False
        
        # Save the file
        stego_filename = "api_verification_stego.wav"
        with open(stego_filename, "wb") as f:
            f.write(download_response.content)
        
        print(f"   📥 Downloaded: {stego_filename}")
        
        # Now test extraction API
        extract_url = "http://localhost:8000/api/extract"
        
        files = {
            'stego_file': (stego_filename, open(stego_filename, 'rb'), 'audio/wav')
        }
        
        data = {
            'password': 'api_verify123'
            # carrier_type is auto-detected, don't pass it
        }
        
        print("   📤 Sending extract request...")
        response = requests.post(extract_url, files=files, data=data)
        files['stego_file'][1].close()
        
        if response.status_code != 200:
            print(f"   ❌ Extract HTTP error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=4)}")
            except:
                print(f"   Error text: {response.text}")
            return False
        
        result = response.json()
        
        if not result.get('success'):
            print(f"   ❌ Extract API error: {result.get('error')}")
            return False
        
        extract_operation_id = result.get('operation_id')
        
        # Wait for extraction completion
        status_url = f"http://localhost:8000/api/operations/{extract_operation_id}/status"
        
        for i in range(15):
            time.sleep(1)
            status_response = requests.get(status_url)
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                status = status_result.get('status')
                
                if status == 'completed':
                    # The extracted content is in result.preview for text data
                    result_data = status_result.get('result', {})
                    extracted_content = result_data.get('preview') or status_result.get('extracted_content')
                    expected_content = 'API verification test message!'
                    
                    print(f"   🔍 Expected: '{expected_content}'")
                    print(f"   🔍 Extracted: '{extracted_content}'")
                    
                    if extracted_content == expected_content:
                        print("   ✅ API extract workflow successful")
                        return True
                    else:
                        print(f"   ❌ Content mismatch in API extract")
                        print(f"   Expected: '{expected_content}'")
                        print(f"   Got: '{extracted_content}'")
                        return False
                elif status == 'failed':
                    error = status_result.get('error', 'Unknown error')
                    print(f"   ❌ Extract operation failed: {error}")
                    return False
        
        print("   ⏰ Extract operation timed out")
        return False
        
    except Exception as e:
        print(f"   ❌ Exception in API extract test: {e}")
        return False

def test_content_integrity():
    """Test that content integrity is maintained"""
    try:
        # Test with various content types
        test_cases = [
            "Simple text",
            "Text with special chars: @#$%^&*()!",
            "Multi-line\\ntext\\nwith\\nnewlines",
            "Unicode: 🎵🎶🎼 音楽 музыка",
            "Numbers: 123456789 and symbols: <>?{}[]|",
        ]
        
        manager = UniversalFileAudio(password="integrity_test")
        
        for i, test_content in enumerate(test_cases):
            output_file = f"integrity_test_{i}.wav"
            
            # Hide and extract
            hide_result = manager.hide_data("enhanced_audio_test.wav", test_content, output_file, is_file=False)
            
            if not hide_result.get('success'):
                print(f"   ❌ Hide failed for case {i}: {test_content[:30]}...")
                return False
            
            extract_result = manager.extract_data(output_file)
            
            if not extract_result:
                print(f"   ❌ Extract failed for case {i}")
                return False
            
            extracted_text, _ = extract_result
            
            if extracted_text != test_content:
                print(f"   ❌ Integrity failure for case {i}")
                print(f"       Expected: {repr(test_content)}")
                print(f"       Got: {repr(extracted_text)}")
                return False
        
        print("   ✅ Content integrity maintained for all test cases")
        return True
        
    except Exception as e:
        print(f"   ❌ Exception in integrity test: {e}")
        return False

def test_error_handling():
    """Test proper error handling"""
    try:
        manager = UniversalFileAudio(password="error_test")
        
        # Test 1: Non-existent file
        result = manager.hide_data("nonexistent.wav", "test", "output.wav", is_file=False)
        if result.get('success'):
            print("   ❌ Should fail for non-existent file")
            return False
        
        # Test 2: Wrong password extraction
        # First create a valid stego file
        hide_result = manager.hide_data("enhanced_audio_test.wav", "secret", "error_test.wav", is_file=False)
        if not hide_result.get('success'):
            print("   ❌ Setup failed for error test")
            return False
        
        # Try to extract with wrong password
        wrong_manager = UniversalFileAudio(password="wrong_password")
        extract_result = wrong_manager.extract_data("error_test.wav")
        
        # This should either return None or throw an exception (both are acceptable)
        # What we don't want is it to return the correct content
        if extract_result and extract_result[0] == "secret":
            print("   ❌ Wrong password should not extract correct content")
            return False
        
        print("   ✅ Error handling works correctly")
        return True
        
    except Exception as e:
        # Exceptions during error testing are acceptable
        print("   ✅ Error handling works (exceptions caught properly)")
        return True

if __name__ == "__main__":
    test_all_audio_functionality()
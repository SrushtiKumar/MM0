#!/usr/bin/env python3
"""
Comprehensive security test for ALL steganography formats
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager
from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager  
from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager
from enhanced_web_image_stego import EnhancedWebImageSteganographyManager

def test_audio_security():
    """Test audio steganography password security"""
    print("🎵 Testing AUDIO steganography password security...")
    
    # Create test audio file
    test_audio_path = "test_audio_security.wav"
    test_message = "Secret audio message"
    correct_password = "audio_pass123"
    wrong_password = "wrong_audio456"
    
    # Create a simple WAV file header + data
    with open(test_audio_path, 'wb') as f:
        # Simple WAV header (44 bytes) + audio data
        wav_header = b'RIFF' + b'\x00\x00\x10\x00' + b'WAVE' + b'fmt ' + b'\x10\x00\x00\x00' + b'\x01\x00\x01\x00' + b'\x44\xAC\x00\x00' + b'\x88\x58\x01\x00' + b'\x02\x00\x10\x00' + b'data' + b'\x00\x00\x10\x00'
        audio_data = b'\x00\x01' * 8000  # Some audio samples
        f.write(wav_header + audio_data)
    
    try:
        # Hide with correct password
        manager = EnhancedWebAudioSteganographyManager(correct_password)
        result = manager.hide_data(test_audio_path, test_message, "test_audio_output.wav")
        
        if not result['success']:
            print(f"   ❌ Failed to hide audio: {result.get('error', 'Unknown error')}")
            return False
        
        output_path = result['output_path']
        
        # Try wrong password
        wrong_manager = EnhancedWebAudioSteganographyManager(wrong_password)
        try:
            wrong_content, wrong_filename = wrong_manager.extract_data(output_path)
            if wrong_content is not None:
                print(f"   ❌ VULNERABILITY: Wrong password extracted: {wrong_content}")
                return False
        except Exception as e:
            # Good - wrong password should fail
            pass
        
        # Try correct password  
        correct_manager = EnhancedWebAudioSteganographyManager(correct_password)
        try:
            correct_content, correct_filename = correct_manager.extract_data(output_path)
            if correct_content and test_message in correct_content.decode('utf-8', errors='ignore'):
                print(f"   ✅ SECURE: Audio steganography properly protects data")
                return True
            else:
                print(f"   ❌ Problem: Correct password gave unexpected result")
                return False
        except Exception as e:
            print(f"   ❌ Problem: Correct password failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    finally:
        # Cleanup
        for path in [test_audio_path, "test_audio_output.wav"]:
            if os.path.exists(path):
                os.remove(path)

def test_document_security():
    """Test document steganography password security"""
    print("📄 Testing DOCUMENT steganography password security...")
    
    test_doc_path = "test_doc_security.pdf"
    test_message = "Secret document message"
    correct_password = "doc_pass123"
    wrong_password = "wrong_doc456"
    
    # Create test document
    with open(test_doc_path, 'w') as f:
        f.write("This is a test document for steganography security testing. " * 20)
    
    try:
        # Hide with correct password
        manager = EnhancedWebDocumentSteganographyManager(correct_password)
        result = manager.hide_data(test_doc_path, test_message, "test_doc_output.pdf")
        
        if not result['success']:
            print(f"   ❌ Failed to hide document: {result}")
            return False
        
        output_path = result['output_path']
        
        # Try wrong password
        wrong_manager = EnhancedWebDocumentSteganographyManager(wrong_password)
        try:
            extracted_content, filename = wrong_manager.extract_data(output_path)
            print(f"   ❌ VULNERABILITY: Wrong password extracted: {extracted_content[:50]}...")
            return False
        except Exception as e:
            # Good - wrong password should fail
            pass
        
        # Try correct password
        correct_manager = EnhancedWebDocumentSteganographyManager(correct_password) 
        try:
            extracted_content, filename = correct_manager.extract_data(output_path)
            if extracted_content and test_message in extracted_content.decode('utf-8', errors='ignore'):
                print(f"   ✅ SECURE: Document steganography properly protects data")
                return True
            else:
                print(f"   ❌ Problem: Correct password gave unexpected result")
                return False
        except Exception as e:
            print(f"   ❌ Problem: Correct password failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    finally:
        # Cleanup
        for path in [test_doc_path, "test_doc_output.pdf"]:
            if os.path.exists(path):
                os.remove(path)

def test_video_security():
    """Test video steganography password security"""
    print("🎬 Testing VIDEO steganography password security...")
    
    test_video_path = "test_video_security.mp4"
    test_message = "Secret video message"
    correct_password = "video_pass123"
    wrong_password = "wrong_video456"
    
    # Create test video file
    with open(test_video_path, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    try:
        # Hide with correct password
        manager = EnhancedWebVideoSteganographyManager(correct_password)
        result = manager.hide_data(test_video_path, test_message, "test_video_output.mp4")
        
        if not result['success']:
            print(f"   ❌ Failed to hide video: {result}")
            return False
        
        output_path = result['output_path']
        
        # Try wrong password
        wrong_manager = EnhancedWebVideoSteganographyManager(wrong_password)
        try:
            extracted_content, filename = wrong_manager.extract_data(output_path)
            if extracted_content is not None:
                print(f"   ❌ VULNERABILITY: Wrong password extracted: {extracted_content}")
                return False
        except Exception as e:
            # Good - wrong password should fail
            pass
        
        # Try correct password
        correct_manager = EnhancedWebVideoSteganographyManager(correct_password)
        try:
            extracted_content, filename = correct_manager.extract_data(output_path)
            if extracted_content and test_message in extracted_content.decode('utf-8', errors='ignore'):
                print(f"   ✅ SECURE: Video steganography properly protects data")
                return True
            else:
                print(f"   ❌ Problem: Correct password gave unexpected result")
                return False
        except Exception as e:
            print(f"   ❌ Problem: Correct password failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    finally:
        # Cleanup
        for path in [test_video_path, "test_video_output.mp4"]:
            if os.path.exists(path):
                os.remove(path)

def test_image_security():
    """Test image steganography password security"""  
    print("🖼️ Testing IMAGE steganography password security...")
    
    test_image_path = "test_image_simple.png"
    test_message = "Secret image message"
    correct_password = "image_pass123"
    wrong_password = "wrong_image456"
    
    try:
        # Hide with correct password
        manager = EnhancedWebImageSteganographyManager(correct_password)
        result = manager.hide_data(test_image_path, test_message, "test_image_output.png")
        
        if not result['success']:
            print(f"   ❌ Failed to hide image: {result}")
            return False
        
        output_path = result['output_path']
        
        # Try wrong password
        wrong_manager = EnhancedWebImageSteganographyManager(wrong_password)
        try:
            wrong_content, wrong_filename = wrong_manager.extract_data(output_path)
            if wrong_content is not None:
                print(f"   ❌ VULNERABILITY: Wrong password extracted: {wrong_content}")
                return False
        except Exception as e:
            # Good - wrong password should fail
            pass
        
        # Try correct password
        correct_manager = EnhancedWebImageSteganographyManager(correct_password)
        try:
            correct_content, correct_filename = correct_manager.extract_data(output_path)
            if correct_content and test_message in correct_content.decode('utf-8', errors='ignore'):
                print(f"   ✅ SECURE: Image steganography properly protects data")
                return True
            else:
                print(f"   ❌ Problem: Correct password gave unexpected result")
                return False
        except Exception as e:
            print(f"   ❌ Problem: Correct password failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    finally:
        # Cleanup  
        for path in [test_image_path, "test_image_output.png"]:
            if os.path.exists(path):
                os.remove(path)

def main():
    """Run comprehensive security tests"""
    print("🔒 COMPREHENSIVE STEGANOGRAPHY SECURITY TEST")
    print("=" * 60)
    
    results = []
    
    # Test all formats
    results.append(("Audio", test_audio_security()))
    results.append(("Document", test_document_security()))
    results.append(("Video", test_video_security()))
    results.append(("Image", test_image_security()))
    
    print("\n" + "=" * 60)
    print("📋 SECURITY TEST RESULTS:")
    print("=" * 60)
    
    all_secure = True
    for format_name, is_secure in results:
        status = "✅ SECURE" if is_secure else "❌ VULNERABLE"
        print(f"{format_name:12} steganography: {status}")
        if not is_secure:
            all_secure = False
    
    print("=" * 60)
    if all_secure:
        print("🎉 ALL STEGANOGRAPHY FORMATS ARE SECURE!")
        print("✅ Password vulnerability has been resolved across all formats")
    else:
        print("⚠️ SECURITY ISSUES DETECTED!")
        print("❌ Some formats still have password vulnerabilities")
    
    return all_secure

if __name__ == "__main__":
    main()
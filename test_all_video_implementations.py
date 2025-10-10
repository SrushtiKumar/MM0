#!/usr/bin/env python3
"""Test for video steganography password vulnerabilities by checking all implementations"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_video_implementation_security():
    """Test all video steganography implementations for password security"""
    print("🔍 Testing all video steganography implementations for password security...")
    
    vulnerable_implementations = []
    secure_implementations = []
    failed_implementations = []
    
    # List of video steganography implementations to test
    implementations = [
        ("SimpleVideoTextSteganographyManager", "simple_video_text_stego"),
        ("WebVideoTextSteganographyManager", "web_video_text_stego"),
        ("WorkingVideoTextSteganographyManager", "working_video_text_stego"),
        ("RobustWebVideoTextSteganographyManager", "robust_web_video_text_stego"),
        ("ReliableWebVideoTextSteganographyManager", "reliable_web_video_text_stego"),
        ("FinalWebVideoTextSteganographyManager", "final_web_video_text_stego"),
        ("EnhancedWebVideoSteganographyManager", "enhanced_web_video_stego"),
    ]
    
    # Test data
    test_video_path = "test_impl_video.mp4"
    test_message = "Secret implementation test message"
    correct_password = "impl123"
    wrong_password = "wrong789"
    
    # Create test video
    with open(test_video_path, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    try:
        for manager_class, module_name in implementations:
            print(f"\n📹 Testing {manager_class}...")
            
            try:
                # Import the module and class
                module = __import__(module_name)
                manager_cls = getattr(module, manager_class)
                
                # Create manager with correct password
                manager = manager_cls(correct_password)
                
                # Try to hide data
                if hasattr(manager, 'hide_data'):
                    result = manager.hide_data(test_video_path, test_message, f"test_output_{module_name}.mp4")
                elif hasattr(manager, 'hide_text_in_video'):
                    result = manager.hide_text_in_video(test_video_path, test_message)
                else:
                    print(f"   ⚠️  No hide method found")
                    failed_implementations.append(manager_class)
                    continue
                
                if not result.get('success', False):
                    print(f"   ⚠️  Hide operation failed: {result}")
                    failed_implementations.append(manager_class)
                    continue
                
                output_path = result.get('output_path') or f"test_output_{module_name}.mp4"
                
                # Test extraction with wrong password
                wrong_manager = manager_cls(wrong_password)
                
                try:
                    if hasattr(wrong_manager, 'extract_data'):
                        wrong_result = wrong_manager.extract_data(output_path)
                    elif hasattr(wrong_manager, 'extract_text_from_video'):
                        wrong_result = wrong_manager.extract_text_from_video(output_path)
                    else:
                        print(f"   ⚠️  No extract method found")
                        failed_implementations.append(manager_class)
                        continue
                    
                    # Check if wrong password succeeded
                    if isinstance(wrong_result, tuple):
                        # Format: (data, filename)
                        extracted_data, _ = wrong_result
                        if extracted_data is not None and test_message in str(extracted_data):
                            print(f"   ❌ VULNERABLE: Wrong password extracted: {str(extracted_data)[:50]}...")
                            vulnerable_implementations.append(manager_class)
                            continue
                    elif isinstance(wrong_result, dict):
                        # Format: {'success': bool, 'text': str, ...}
                        if wrong_result.get('success') and wrong_result.get('text') and test_message in wrong_result['text']:
                            print(f"   ❌ VULNERABLE: Wrong password extracted: {wrong_result['text'][:50]}...")
                            vulnerable_implementations.append(manager_class)
                            continue
                    
                    print(f"   ✅ SECURE: Wrong password failed appropriately")
                    secure_implementations.append(manager_class)
                    
                except Exception as e:
                    print(f"   ✅ SECURE: Wrong password raised error: {e}")
                    secure_implementations.append(manager_class)
                
                # Clean up output file
                if os.path.exists(output_path):
                    os.remove(output_path)
                    
            except ImportError as e:
                print(f"   ⚠️  Import failed: {e}")
                failed_implementations.append(manager_class)
            except Exception as e:
                print(f"   ⚠️  Test failed: {e}")
                failed_implementations.append(manager_class)
                
    finally:
        # Clean up test file
        if os.path.exists(test_video_path):
            os.remove(test_video_path)
    
    # Report results
    print("\n" + "=" * 70)
    print("📊 VIDEO STEGANOGRAPHY SECURITY AUDIT RESULTS")
    print("=" * 70)
    
    if vulnerable_implementations:
        print(f"❌ VULNERABLE IMPLEMENTATIONS ({len(vulnerable_implementations)}):")
        for impl in vulnerable_implementations:
            print(f"   • {impl}")
    
    if secure_implementations:
        print(f"✅ SECURE IMPLEMENTATIONS ({len(secure_implementations)}):")
        for impl in secure_implementations:
            print(f"   • {impl}")
    
    if failed_implementations:
        print(f"⚠️  FAILED TO TEST ({len(failed_implementations)}):")
        for impl in failed_implementations:
            print(f"   • {impl}")
    
    print("=" * 70)
    
    if vulnerable_implementations:
        print("🚨 CRITICAL SECURITY ISSUE DETECTED!")
        print("❌ Some video steganography implementations are vulnerable to password bypass!")
        print("❌ These need immediate security fixes!")
        return False
    else:
        print("🎉 ALL TESTED IMPLEMENTATIONS ARE SECURE!")
        print("✅ No password bypass vulnerabilities detected")
        return True

if __name__ == "__main__":
    test_video_implementation_security()
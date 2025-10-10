#!/usr/bin/env python3
"""Test video steganography password security"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager

def test_video_password_security():
    """Test if video steganography properly validates passwords"""
    print("Testing video steganography password security...")
    
    # Create test video file
    test_video_path = "test_video.mp4"
    test_message = "Secret message for video test"
    correct_password = "correct123"
    wrong_password = "wrong456"
    
    # Create a simple test video file
    with open(test_video_path, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)  # Simple fake video data
    
    try:
        # Create steganography manager with correct password
        manager = EnhancedWebVideoSteganographyManager(correct_password)
        print(f"Manager password: '{manager.password}'")
        print(f"Video stego password: '{manager.video_stego.password}'")
        
        # Hide message
        print("Hiding message with correct password...")
        result = manager.hide_data(
            test_video_path, 
            test_message,
            "test_output.mp4"
        )
        print(f"Hidden successfully. Result: {result}")
        
        # Try to extract with WRONG password
        print("\nTrying to extract with WRONG password...")
        wrong_manager = EnhancedWebVideoSteganographyManager(wrong_password)
        print(f"Wrong manager password: '{wrong_manager.password}'")
        print(f"Wrong video stego password: '{wrong_manager.video_stego.password}'")
        
        try:
            extracted_content, filename = wrong_manager.extract_data("test_output.mp4")
            if extracted_content is None:
                print("✅ Good: Wrong password returned None")
            else:
                print(f"❌ SECURITY VULNERABILITY: Successfully extracted with wrong password!")
                print(f"   Extracted: {extracted_content[:100] if isinstance(extracted_content, bytes) else extracted_content}...")
                print(f"   Filename: {filename}")
                return False
        except Exception as e:
            print(f"✅ Good: Wrong password failed with error: {e}")
            
        # Now try with correct password to verify it works
        print("\nTrying to extract with CORRECT password...")
        correct_manager = EnhancedWebVideoSteganographyManager(correct_password)
        print(f"Correct manager password: '{correct_manager.password}'")
        print(f"Correct video stego password: '{correct_manager.video_stego.password}'")
        
        try:
            extracted_content, filename = correct_manager.extract_data("test_output.mp4")
            if extracted_content is None:
                print(f"❌ Problem: Correct password returned None")
                return False
            else:
                print(f"✅ Good: Correct password worked!")
                if isinstance(extracted_content, bytes):
                    print(f"   Extracted: {extracted_content.decode('utf-8', errors='ignore')[:100]}...")
                else:
                    print(f"   Extracted: {extracted_content[:100]}...")
                print(f"   Filename: {filename}")
                return True
        except Exception as e:
            print(f"❌ Problem: Correct password failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test files
        for file_path in [test_video_path, "test_output.mp4"]:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    test_video_password_security()
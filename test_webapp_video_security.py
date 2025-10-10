#!/usr/bin/env python3
"""Test video steganography password security through web app simulation"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager

def test_web_app_video_security():
    """Test video steganography security the way the web app uses it"""
    print("🎬 Testing video steganography security through web app simulation...")
    
    # Create test video file
    test_video_path = "test_webapp_video.mp4"
    test_message = "Secret webapp video message"
    correct_password = "webapp123"
    wrong_password = "wrongpass456"
    
    # Create a simple test video file
    with open(test_video_path, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)  # Simple fake video data
    
    try:
        print("\n1. HIDING data with correct password...")
        # Hide message with correct password
        hide_manager = EnhancedWebVideoSteganographyManager(correct_password)
        hide_result = hide_manager.hide_data(
            test_video_path, 
            test_message,
            "webapp_output.mp4"
        )
        print(f"   Hide result: {hide_result['success']}")
        
        if not hide_result['success']:
            print(f"   ❌ Failed to hide: {hide_result}")
            return False
        
        output_path = hide_result['output_path']
        
        print("\n2. EXTRACTING with WRONG password (simulating web app behavior)...")
        # Try to extract with wrong password - this simulates the web app flow
        wrong_manager = EnhancedWebVideoSteganographyManager(wrong_password)
        
        try:
            wrong_data, wrong_filename = wrong_manager.extract_data(output_path)
            
            # Check web app logic: if extracted_data and filename:
            if wrong_data and wrong_filename:
                print(f"   ❌ CRITICAL VULNERABILITY: Wrong password succeeded!")
                print(f"   ❌ Extracted data: {wrong_data[:50]}...")
                print(f"   ❌ Filename: {wrong_filename}")
                print(f"   ❌ Web app would show: SUCCESS with wrong password!")
                return False
            else:
                print(f"   ✅ Good: Wrong password returned None data")
                print(f"   ✅ Web app would show: 'No hidden data found'")
                
        except ValueError as e:
            if "Data corruption detected or wrong password" in str(e):
                print(f"   ✅ Excellent: Wrong password raised proper error: {e}")
                print(f"   ✅ Web app would show: 'Video extraction failed' with password error")
            else:
                print(f"   ⚠️  Wrong password raised unexpected error: {e}")
        except Exception as e:
            print(f"   ⚠️  Wrong password caused unexpected exception: {e}")
        
        print("\n3. EXTRACTING with CORRECT password...")
        # Try to extract with correct password
        correct_manager = EnhancedWebVideoSteganographyManager(correct_password)
        
        try:
            correct_data, correct_filename = correct_manager.extract_data(output_path)
            
            if correct_data and correct_filename:
                extracted_text = correct_data.decode('utf-8', errors='ignore')
                if test_message in extracted_text:
                    print(f"   ✅ Perfect: Correct password extracted the right message!")
                    print(f"   ✅ Extracted: {extracted_text}")
                    print(f"   ✅ Filename: {correct_filename}")
                    return True
                else:
                    print(f"   ❌ Problem: Correct password extracted wrong data")
                    print(f"   ❌ Expected: {test_message}")
                    print(f"   ❌ Got: {extracted_text}")
                    return False
            else:
                print(f"   ❌ Problem: Correct password returned None")
                return False
                
        except Exception as e:
            print(f"   ❌ Problem: Correct password failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test files
        for file_path in [test_video_path, "webapp_output.mp4"]:
            if os.path.exists(file_path):
                os.remove(file_path)

def main():
    """Run the web app simulation test"""
    print("🔒 VIDEO STEGANOGRAPHY WEB APP SECURITY TEST")
    print("=" * 60)
    
    is_secure = test_web_app_video_security()
    
    print("\n" + "=" * 60)
    if is_secure:
        print("🎉 VIDEO STEGANOGRAPHY IS SECURE!")
        print("✅ Wrong passwords properly fail")
        print("✅ Correct passwords successfully extract data")
        print("✅ Web app will show appropriate error messages")
    else:
        print("⚠️ VIDEO STEGANOGRAPHY SECURITY ISSUE DETECTED!")
        print("❌ Wrong passwords may be succeeding inappropriately")
    
    return is_secure

if __name__ == "__main__":
    main()
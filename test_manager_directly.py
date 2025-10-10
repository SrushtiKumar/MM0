#!/usr/bin/env python3
"""Direct test of EnhancedWebVideoSteganographyManager to isolate the bug"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager

def test_manager_directly():
    """Test the manager class directly to find the exact issue"""
    
    # Create test video
    test_video = "manager_test.mp4"
    with open(test_video, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    correct_password = "manager123"
    wrong_password = "managerwrong456"
    test_message = "Manager test secret message"
    
    print("🔍 TESTING ENHANCED WEB VIDEO STEGANOGRAPHY MANAGER DIRECTLY...")
    
    try:
        # 1. Hide with correct password
        print(f"\n1. Hiding with correct password: '{correct_password}'")
        hide_manager = EnhancedWebVideoSteganographyManager(correct_password)
        print(f"   Manager password: '{hide_manager.password}'")
        print(f"   Underlying stego password: '{hide_manager.video_stego.password}'")
        
        hide_result = hide_manager.hide_data(test_video, test_message, "manager_output.mp4")
        
        if not hide_result.get('success'):
            print(f"❌ Hide failed: {hide_result}")
            return
        
        print("✅ Hide succeeded")
        
        # 2. Extract with WRONG password
        print(f"\n2. Extracting with WRONG password: '{wrong_password}'")
        wrong_manager = EnhancedWebVideoSteganographyManager(wrong_password)
        print(f"   Manager password: '{wrong_manager.password}'")
        print(f"   Underlying stego password: '{wrong_manager.video_stego.password}'")
        
        try:
            wrong_data, wrong_filename = wrong_manager.extract_data("manager_output.mp4")
            
            print(f"   Extract result: data={wrong_data}, filename={wrong_filename}")
            
            if wrong_data and wrong_filename:
                print(f"❌ CRITICAL BUG: Wrong password extraction succeeded!")
                print(f"   Extracted data: {wrong_data}")
                print(f"   Filename: {wrong_filename}")
                
                # Convert to text if it's bytes
                if isinstance(wrong_data, bytes):
                    try:
                        text_data = wrong_data.decode('utf-8')
                        print(f"   Text content: '{text_data}'")
                        if test_message in text_data:
                            print(f"   ❌ CRITICAL: Original message found!")
                    except:
                        pass
                
                return False  # Vulnerability found
            else:
                print("✅ Wrong password properly returned None")
                
        except Exception as e:
            if "wrong password" in str(e).lower() or "corruption" in str(e).lower():
                print(f"✅ Wrong password properly raised error: {e}")
            else:
                print(f"⚠️  Wrong password raised unexpected error: {e}")
        
        # 3. Extract with CORRECT password
        print(f"\n3. Extracting with CORRECT password: '{correct_password}'")
        correct_manager = EnhancedWebVideoSteganographyManager(correct_password)
        
        try:
            correct_data, correct_filename = correct_manager.extract_data("manager_output.mp4")
            
            if correct_data and correct_filename:
                print("✅ Correct password extraction succeeded")
                
                # Convert to text if it's bytes
                if isinstance(correct_data, bytes):
                    try:
                        text_data = correct_data.decode('utf-8')
                        print(f"   Text content: '{text_data}'")
                        if test_message in text_data:
                            print(f"   ✅ Original message correctly extracted")
                    except:
                        pass
                return True
            else:
                print("❌ Correct password returned None")
                return False
                
        except Exception as e:
            print(f"❌ Correct password raised error: {e}")
            return False
    
    finally:
        # Cleanup
        for file in ["manager_test.mp4", "manager_output.mp4"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = test_manager_directly()
    if success:
        print("\n✅ Manager is working correctly")
    else:
        print("\n❌ Manager has a security vulnerability")
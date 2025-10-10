#!/usr/bin/env python3
"""Test to replicate exact web API conditions"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(__file__))

from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager

def test_exact_web_api_conditions():
    """Test using exact same conditions as the web API"""
    
    correct_password = "webapi123"
    wrong_password = "webapiwrong456"
    test_message = "Web API exact test message"
    
    print("🔍 TESTING EXACT WEB API CONDITIONS...")
    
    # Create test video exactly like the web API does
    test_video = "webapi_exact_test.mp4"
    with open(test_video, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    try:
        # 1. Hide data like the web API does
        print(f"\n1. Hiding data (password: '{correct_password}')...")
        hide_manager = EnhancedWebVideoSteganographyManager(correct_password)
        
        # The web API calls hide_data with is_file=False for text
        hide_result = hide_manager.hide_data(test_video, test_message, "webapi_exact_output.mp4", is_file=False)
        
        if not hide_result.get('success'):
            print(f"❌ Hide failed: {hide_result}")
            return
        
        print("✅ Hide completed")
        print(f"   Result: {hide_result}")
        
        # 2. Create temporary file like the web API does for extraction
        print(f"\n2. Setting up extraction with temp files (like web API)...")
        
        # Read the steganographic video content
        with open("webapi_exact_output.mp4", 'rb') as f:
            stego_content = f.read()
        
        # Create a temporary file path like the web API does
        temp_extract_path = f"temp_extract_webapi_exact_output.mp4"
        with open(temp_extract_path, 'wb') as f:
            f.write(stego_content)
        
        print(f"   Temp extraction file: {temp_extract_path}")
        print(f"   File size: {len(stego_content)} bytes")
        
        # 3. Extract with WRONG password like the web API does
        print(f"\n3. Extracting with WRONG password ('{wrong_password}')...")
        wrong_manager = EnhancedWebVideoSteganographyManager(wrong_password)
        
        try:
            wrong_data, wrong_filename = wrong_manager.extract_data(temp_extract_path)
            
            print(f"   Manager extract result:")
            print(f"     Data: {wrong_data}")
            print(f"     Filename: {wrong_filename}")
            
            if wrong_data and wrong_filename:
                print(f"❌ CRITICAL: Wrong password returned data!")
                
                # Check if it's the actual message
                if isinstance(wrong_data, bytes):
                    try:
                        text_content = wrong_data.decode('utf-8')
                        print(f"     Text content: '{text_content}'")
                        if test_message in text_content:
                            print(f"❌ SEVERE: Original message extracted with wrong password!")
                    except:
                        pass
                
                return False  # Vulnerability confirmed
            else:
                print("✅ Wrong password properly returned None")
                
        except Exception as e:
            print(f"✅ Wrong password raised exception: {e}")
        
        # 4. Extract with CORRECT password
        print(f"\n4. Extracting with CORRECT password ('{correct_password}')...")
        correct_manager = EnhancedWebVideoSteganographyManager(correct_password)
        
        try:
            correct_data, correct_filename = correct_manager.extract_data(temp_extract_path)
            
            if correct_data and correct_filename:
                print("✅ Correct password extraction succeeded")
                
                if isinstance(correct_data, bytes):
                    try:
                        text_content = correct_data.decode('utf-8')
                        print(f"     Text content: '{text_content}'")
                        if test_message in text_content:
                            print(f"✅ Original message correctly extracted")
                    except:
                        pass
                
                return True
            else:
                print("❌ Correct password returned None")
                return False
                
        except Exception as e:
            print(f"❌ Correct password raised exception: {e}")
            return False
    
    finally:
        # Cleanup
        for file in [test_video, "webapi_exact_output.mp4", "temp_extract_webapi_exact_output.mp4"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = test_exact_web_api_conditions()
    if success:
        print("\n✅ No vulnerability found in exact conditions test")
    else:
        print("\n❌ VULNERABILITY CONFIRMED in exact conditions test!")
#!/usr/bin/env python3
"""
Minimal reproduction test that exactly mimics web app behavior
to isolate the exact security vulnerability
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import exactly what the web app imports
from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager

def minimal_reproduction():
    """Minimal test that exactly replicates web app behavior"""
    
    print("🔬 MINIMAL REPRODUCTION TEST")
    print("="*50)
    
    # Create test video
    test_video = "minimal_test.mp4"
    with open(test_video, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    correct_password = "minimal123"
    wrong_password = "minimalwrong456"
    test_data = "Minimal test secret message"
    
    try:
        print(f"\n1. Creating hide manager with password: '{correct_password}'")
        
        # This mimics what the web app does in process_hide_job
        hide_manager = EnhancedWebVideoSteganographyManager(correct_password)
        print(f"   Hide manager type: {type(hide_manager).__name__}")
        print(f"   Hide manager password attr: {getattr(hide_manager, 'password', 'NO PASSWORD')}")
        
        # Hide data (mimics web app hide logic)
        print(f"   Calling hide_data...")
        hide_result = hide_manager.hide_data(test_video, test_data, "minimal_output.mp4", is_file=False)
        
        if not hide_result.get('success'):
            print(f"❌ Hide failed: {hide_result}")
            return False
        
        print(f"✅ Hide succeeded: {hide_result}")
        
        # Save the output file content like web app does
        output_path = hide_result['output_path']
        with open(output_path, 'rb') as f:
            output_content = f.read()
        
        print(f"   Output file size: {len(output_content)} bytes")
        
        # Create temp file exactly like web app does in process_extract_job
        temp_extract_file = "temp_minimal_extract.mp4"
        with open(temp_extract_file, 'wb') as f:
            f.write(output_content)
        
        print(f"\n2. Creating extract manager with WRONG password: '{wrong_password}'")
        
        # This mimics what the web app does in process_extract_job
        wrong_manager = EnhancedWebVideoSteganographyManager(wrong_password)
        print(f"   Wrong manager type: {type(wrong_manager).__name__}")
        print(f"   Wrong manager password attr: {getattr(wrong_manager, 'password', 'NO PASSWORD')}")
        
        print(f"   Calling extract_data on: {temp_extract_file}")
        
        try:
            wrong_data, wrong_filename = wrong_manager.extract_data(temp_extract_file)
            print(f"   Extract result: data={type(wrong_data) if wrong_data else None}, filename={wrong_filename}")
            
            if wrong_data and wrong_filename:
                print(f"❌ VULNERABILITY: Wrong password returned data!")
                
                # Check if it's the original data
                if isinstance(wrong_data, bytes):
                    try:
                        text_content = wrong_data.decode('utf-8')
                        print(f"     Text: '{text_content}'")
                        if test_data in text_content:
                            print(f"❌ CRITICAL: Original message extracted with wrong password!")
                            return False  # Vulnerability confirmed
                    except:
                        pass
                
                print(f"❌ Wrong password extraction should have failed!")
                return False
            else:
                print(f"✅ Wrong password properly returned None")
                
        except Exception as e:
            if "wrong password" in str(e).lower() or "corruption" in str(e).lower():
                print(f"✅ Wrong password properly raised error: {e}")
            else:
                print(f"⚠️  Wrong password raised unexpected error: {e}")
        
        print(f"\n3. Creating extract manager with CORRECT password: '{correct_password}'")
        
        correct_manager = EnhancedWebVideoSteganographyManager(correct_password)
        print(f"   Correct manager type: {type(correct_manager).__name__}")
        print(f"   Correct manager password attr: {getattr(correct_manager, 'password', 'NO PASSWORD')}")
        
        try:
            correct_data, correct_filename = correct_manager.extract_data(temp_extract_file)
            
            if correct_data and correct_filename:
                print(f"✅ Correct password extraction succeeded")
                
                if isinstance(correct_data, bytes):
                    try:
                        text_content = correct_data.decode('utf-8')
                        print(f"     Text: '{text_content}'")
                        if test_data in text_content:
                            print(f"✅ Original message correctly extracted")
                    except:
                        pass
                
                return True
            else:
                print(f"❌ Correct password returned None")
                return False
                
        except Exception as e:
            print(f"❌ Correct password raised error: {e}")
            return False
    
    finally:
        # Cleanup
        for file in [test_video, "minimal_output.mp4", temp_extract_file]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = minimal_reproduction()
    
    print("\n" + "="*50)
    if success:
        print("✅ NO VULNERABILITY in minimal reproduction")
    else:
        print("❌ VULNERABILITY CONFIRMED in minimal reproduction!")
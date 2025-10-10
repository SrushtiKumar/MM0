#!/usr/bin/env python3
"""Test for race conditions or manager reuse issues"""

import sys
import os
import threading
import time
sys.path.append(os.path.dirname(__file__))

from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager

def test_race_conditions():
    """Test for race conditions that might occur in web environment"""
    
    # Create test video
    test_video = "race_test.mp4"
    with open(test_video, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    correct_password = "race123"
    wrong_password = "racewrong456"
    test_message = "Race condition test message"
    
    print("🏃 TESTING FOR RACE CONDITIONS...")
    
    try:
        # 1. Hide data
        hide_manager = EnhancedWebVideoSteganographyManager(correct_password)
        hide_result = hide_manager.hide_data(test_video, test_message, "race_output.mp4", is_file=False)
        
        if not hide_result.get('success'):
            print(f"❌ Hide failed: {hide_result}")
            return
        
        print("✅ Hide completed")
        
        # 2. Test multiple concurrent extractions
        results = []
        
        def extract_with_wrong_password(results, test_id):
            """Extract with wrong password in a thread"""
            try:
                manager = EnhancedWebVideoSteganographyManager(wrong_password)
                data, filename = manager.extract_data("race_output.mp4")
                results.append((test_id, "wrong", data, filename))
            except Exception as e:
                results.append((test_id, "wrong", None, str(e)))
        
        def extract_with_correct_password(results, test_id):
            """Extract with correct password in a thread"""
            try:
                manager = EnhancedWebVideoSteganographyManager(correct_password)
                data, filename = manager.extract_data("race_output.mp4")
                results.append((test_id, "correct", data, filename))
            except Exception as e:
                results.append((test_id, "correct", None, str(e)))
        
        # Start multiple threads simulating concurrent web requests
        threads = []
        for i in range(5):
            # Wrong password thread
            t1 = threading.Thread(target=extract_with_wrong_password, args=(results, f"wrong_{i}"))
            # Correct password thread  
            t2 = threading.Thread(target=extract_with_correct_password, args=(results, f"correct_{i}"))
            threads.extend([t1, t2])
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Analyze results
        print(f"\n📊 RACE CONDITION TEST RESULTS:")
        wrong_successes = 0
        correct_successes = 0
        
        for test_id, password_type, data, result in results:
            if password_type == "wrong":
                if data and isinstance(data, bytes) and test_message.encode() in data:
                    print(f"   ❌ {test_id}: VULNERABILITY - Wrong password extracted message!")
                    wrong_successes += 1
                elif data:
                    print(f"   ⚠️  {test_id}: Wrong password extracted some data: {data[:50]}...")
                    wrong_successes += 1
                else:
                    print(f"   ✅ {test_id}: Wrong password properly failed")
            else:  # correct
                if data and isinstance(data, bytes) and test_message.encode() in data:
                    print(f"   ✅ {test_id}: Correct password succeeded")
                    correct_successes += 1
                else:
                    print(f"   ❌ {test_id}: Correct password failed: {result}")
        
        print(f"\n📈 SUMMARY:")
        print(f"   Wrong password successes: {wrong_successes}/5")
        print(f"   Correct password successes: {correct_successes}/5")
        
        return wrong_successes == 0 and correct_successes == 5
    
    finally:
        # Cleanup
        for file in [test_video, "race_output.mp4"]:
            if os.path.exists(file):
                os.remove(file)

def test_manager_reuse():
    """Test if there's an issue with manager reuse"""
    
    print("\n🔄 TESTING MANAGER REUSE...")
    
    # Create test video
    test_video = "reuse_test.mp4"
    with open(test_video, 'wb') as f:
        f.write(b"FAKE_VIDEO_DATA" * 1000)
    
    correct_password = "reuse123"
    wrong_password = "reusewrong456"
    test_message = "Manager reuse test message"
    
    try:
        # Hide data
        hide_manager = EnhancedWebVideoSteganographyManager(correct_password)
        hide_result = hide_manager.hide_data(test_video, test_message, "reuse_output.mp4")
        
        if not hide_result.get('success'):
            print(f"❌ Hide failed")
            return False
        
        # Test: Create manager with wrong password, then try multiple extractions
        print("   Testing same manager instance with wrong password...")
        wrong_manager = EnhancedWebVideoSteganographyManager(wrong_password)
        
        for i in range(3):
            try:
                data, filename = wrong_manager.extract_data("reuse_output.mp4")
                if data:
                    print(f"   ❌ Attempt {i+1}: Wrong password succeeded!")
                    return False
                else:
                    print(f"   ✅ Attempt {i+1}: Wrong password failed properly")
            except Exception as e:
                print(f"   ✅ Attempt {i+1}: Wrong password raised error")
        
        # Test: Create multiple managers with wrong password
        print("   Testing multiple managers with wrong password...")
        for i in range(3):
            manager = EnhancedWebVideoSteganographyManager(wrong_password)
            try:
                data, filename = manager.extract_data("reuse_output.mp4")
                if data:
                    print(f"   ❌ Manager {i+1}: Wrong password succeeded!")
                    return False
                else:
                    print(f"   ✅ Manager {i+1}: Wrong password failed properly")
            except Exception as e:
                print(f"   ✅ Manager {i+1}: Wrong password raised error")
        
        return True
    
    finally:
        # Cleanup
        for file in [test_video, "reuse_output.mp4"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    print("🧪 ADVANCED RACE CONDITION AND REUSE TESTING")
    print("=" * 50)
    
    race_ok = test_race_conditions()
    reuse_ok = test_manager_reuse()
    
    print("\n" + "=" * 50)
    if race_ok and reuse_ok:
        print("✅ No race conditions or reuse issues found")
    else:
        print("❌ Issues detected in advanced testing")
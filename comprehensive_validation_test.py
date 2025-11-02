#!/usr/bin/env python3
"""
Comprehensive validation test for all three corruption fixes
"""

import os
import sys

def run_comprehensive_validation():
    """Run all three tests to validate complete fix"""
    
    print("🧪 COMPREHENSIVE STEGANOGRAPHY VALIDATION")
    print("=" * 60)
    
    results = {
        'document': False,
        'audio': False, 
        'video': False
    }
    
    # Test 1: Document Steganography
    print(f"\n📄 1. TESTING DOCUMENT STEGANOGRAPHY...")
    print("-" * 40)
    
    try:
        # Import and run the document test
        sys.path.insert(0, os.getcwd())
        from test_large_document_steganography import test_large_document_steganography
        
        results['document'] = test_large_document_steganography()
        
        if results['document']:
            print(f"✅ Document steganography: PASSED")
        else:
            print(f"❌ Document steganography: FAILED")
            
    except Exception as e:
        print(f"❌ Document test error: {e}")
        results['document'] = False
    
    # Test 2: Audio Steganography (No Noise)
    print(f"\n🎵 2. TESTING AUDIO STEGANOGRAPHY (NOISE FIX)...")
    print("-" * 40)
    
    try:
        from test_audio_noise_issue import test_audio_noise_issue
        
        results['audio'] = test_audio_noise_issue()
        
        if results['audio']:
            print(f"✅ Audio steganography (noise fix): PASSED")
        else:
            print(f"❌ Audio steganography (noise fix): FAILED")
            
    except Exception as e:
        print(f"❌ Audio test error: {e}")
        results['audio'] = False
    
    # Test 3: Video Steganography (Corruption Fix)
    print(f"\n🎬 3. TESTING VIDEO STEGANOGRAPHY (CORRUPTION FIX)...")
    print("-" * 40)
    
    try:
        from test_video_corruption_issue import test_video_corruption_issue
        
        results['video'] = test_video_corruption_issue()
        
        if results['video']:
            print(f"✅ Video steganography (corruption fix): PASSED")
        else:
            print(f"❌ Video steganography (corruption fix): FAILED")
            
    except Exception as e:
        print(f"❌ Video test error: {e}")
        results['video'] = False
    
    # Final Summary
    print(f"\n" + "=" * 60)
    print(f"📊 COMPREHENSIVE VALIDATION RESULTS")
    print(f"=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_type, result in results.items():
        status_icon = "✅" if result else "❌"
        status_text = "PASSED" if result else "FAILED"
        print(f"{status_icon} {test_type.upper()} steganography: {status_text}")
    
    print(f"\n📈 Success Rate: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL CORRUPTION ISSUES RESOLVED!")
        print(f"✅ Document steganography: Working with binary LSB")
        print(f"✅ Audio steganography: No noise in beginning (middle embedding)")
        print(f"✅ Video steganography: Files remain playable (lossless codec)")
        return True
    else:
        failed_count = total_tests - passed_tests
        print(f"\n⚠️ {failed_count} issue(s) still need attention")
        return False

if __name__ == "__main__":
    success = run_comprehensive_validation()
    
    if success:
        print(f"\n🎯 MISSION ACCOMPLISHED: All steganography corruption issues have been fixed!")
    else:
        print(f"\n🔧 Additional work needed on remaining issues.")
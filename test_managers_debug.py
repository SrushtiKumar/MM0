#!/usr/bin/env python3
"""
Test steganography managers directly
"""

# Import the enhanced_app to get the steganography_managers
try:
    from enhanced_app import steganography_managers, get_steganography_manager
    
    print("🔍 Checking steganography managers:")
    print("=" * 40)
    
    for media_type, manager_class in steganography_managers.items():
        print(f"{media_type}: {manager_class}")
        
        if manager_class:
            try:
                # Try to create an instance
                manager = get_steganography_manager(media_type, "testpass")
                print(f"  ✅ Manager created successfully: {manager}")
            except Exception as e:
                print(f"  ❌ Failed to create manager: {e}")
        else:
            print(f"  ❌ No manager available")
    
    print("\n🔍 Testing manager creation manually:")
    print("=" * 40)
    
    # Test video manager
    try:
        from final_video_steganography import FinalVideoSteganographyManager
        video_manager = FinalVideoSteganographyManager(password="test")
        print(f"✅ Video manager created: {video_manager}")
    except Exception as e:
        print(f"❌ Video manager failed: {e}")
    
    # Test audio manager
    try:
        from universal_file_audio import UniversalFileAudio
        audio_manager = UniversalFileAudio(password="test")
        print(f"✅ Audio manager created: {audio_manager}")
    except Exception as e:
        print(f"❌ Audio manager failed: {e}")
    
    # Test image/document manager
    try:
        from universal_file_steganography import UniversalFileSteganography
        image_manager = UniversalFileSteganography(password="test")
        print(f"✅ Image/Document manager created: {image_manager}")
    except Exception as e:
        print(f"❌ Image/Document manager failed: {e}")
        
except Exception as e:
    print(f"❌ Failed to import enhanced_app: {e}")
    import traceback
    traceback.print_exc()
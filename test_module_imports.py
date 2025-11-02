#!/usr/bin/env python3
"""
Test script to identify all missing steganography modules
"""

print("🔍 Testing steganography module imports...")

# Test video steganography
print("\n📹 Testing video steganography:")
try:
    from final_video_steganography import FinalVideoSteganographyManager
    print("✅ final_video_steganography - OK")
except ImportError as e:
    print(f"❌ final_video_steganography - FAILED: {e}")

try:
    from video_steganography import VideoSteganographyManager
    print("✅ video_steganography - OK")
except ImportError as e:
    print(f"❌ video_steganography - FAILED: {e}")

# Test image steganography 
print("\n🖼️ Testing image steganography:")
try:
    from universal_file_steganography import UniversalFileSteganography
    print("✅ universal_file_steganography - OK")
except ImportError as e:
    print(f"❌ universal_file_steganography - FAILED: {e}")

# Test document steganography
print("\n📄 Testing document steganography:")
try:
    from universal_file_steganography import UniversalFileSteganography
    print("✅ universal_file_steganography (documents) - OK")
except ImportError as e:
    print(f"❌ universal_file_steganography (documents) - FAILED: {e}")

# Test audio steganography
print("\n🔊 Testing audio steganography:")
try:
    from universal_text_audio_stego import UniversalTextAudioSteganographyManager
    print("✅ universal_text_audio_stego - OK")
except ImportError as e:
    print(f"❌ universal_text_audio_stego - FAILED: {e}")

try:
    from universal_file_audio import UniversalFileAudio
    print("✅ universal_file_audio - OK")
except ImportError as e:
    print(f"❌ universal_file_audio - FAILED: {e}")

# Test database service
print("\n🗄️ Testing database service:")
try:
    from supabase_service import get_database, SteganographyDatabase
    print("✅ supabase_service - OK")
except ImportError as e:
    print(f"❌ supabase_service - FAILED: {e}")

print("\n✅ Module import test completed!")
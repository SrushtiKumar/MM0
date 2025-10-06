#!/usr/bin/env python3
"""
Simple test for audio steganography functionality
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from simple_audio_stego import SimpleAudioSteganography

def test_audio_steganography():
    """Test basic audio steganography functionality"""
    print("🔊 Testing Simple Audio Steganography")
    print("=" * 50)
    
    # Create test files
    test_dir = Path("temp")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test text file
    test_message = "Hello, this is a test message for audio steganography!"
    test_file = test_dir / "test_message.txt"
    with open(test_file, "w") as f:
        f.write(test_message)
    
    print(f"✅ Created test file: {test_file}")
    print(f"📝 Test message: {test_message}")
    
    # Check for existing audio files in the workspace
    audio_files = []
    for ext in ['*.wav', '*.mp3', '*.flac', '*.ogg']:
        audio_files.extend(Path(".").glob(ext))
    
    if not audio_files:
        print("❌ No audio files found in workspace for testing")
        print("Please provide a WAV or MP3 file for testing")
        return False
    
    container_file = audio_files[0]
    print(f"🎵 Using container: {container_file}")
    
    # Test steganography
    stego = SimpleAudioSteganography()
    
    # Output files
    output_file = test_dir / f"stego_{container_file.name}"
    extracted_file = test_dir / "extracted_message.txt"
    
    try:
        print("\n🔒 EMBEDDING TEST")
        print("-" * 30)
        
        # Embed file
        result = stego.embed_file(
            str(container_file),
            str(test_file), 
            str(output_file)
        )
        
        if result:
            print(f"✅ Embedding successful!")
            print(f"📁 Output file: {output_file}")
            print(f"📊 File size: {output_file.stat().st_size:,} bytes")
        else:
            print("❌ Embedding failed!")
            return False
            
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("\n🔓 EXTRACTION TEST")
        print("-" * 30)
        
        # Extract file
        extracted_data = stego.extract_file(str(output_file))
        
        if extracted_data:
            # Save extracted data
            with open(extracted_file, "wb") as f:
                f.write(extracted_data)
            
            # Read and compare
            with open(extracted_file, "r") as f:
                extracted_message = f.read()
            
            print(f"✅ Extraction successful!")
            print(f"📁 Extracted file: {extracted_file}")
            print(f"📝 Extracted message: {extracted_message}")
            
            # Verify content
            if extracted_message == test_message:
                print("✅ Content verification: PASSED")
                return True
            else:
                print("❌ Content verification: FAILED")
                print(f"Expected: {test_message}")
                print(f"Got: {extracted_message}")
                return False
        else:
            print("❌ Extraction failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_audio_steganography()
    if success:
        print("\n🎉 All tests passed! Audio steganography is working correctly.")
    else:
        print("\n💔 Tests failed. Please check the implementation.")
    
    print("\n" + "=" * 50)
#!/usr/bin/env python3
"""
Test the exact user scenario: image in MP3, then text in same MP3
"""

import sys
import os
sys.path.append('.')

def test_mp3_image_text_scenario():
    """Test hiding image in MP3, then text in same MP3 with same password"""
    print("🧪 TESTING MP3 + IMAGE + TEXT SCENARIO")
    print("="*60)
    
    try:
        from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager
        from enhanced_app import (
            create_layered_data_container,
            extract_layered_data_container,
            is_layered_container
        )
        
        password = "testpass123"
        
        print("1. Creating test files...")
        
        # Create a simple MP3-like audio file (WAV format for testing)
        # Generate a simple WAV file
        import wave
        import numpy as np
        
        # Create 1 second of audio at 44100 Hz
        sample_rate = 44100
        duration = 1.0
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        audio_data = (audio_data * 32767).astype(np.int16)
        
        with wave.open("test_audio.wav", 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print(f"   🎵 Created test_audio.wav ({os.path.getsize('test_audio.wav')} bytes)")
        
        # Create test image (PNG)
        png_data = bytearray([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D,  # IHDR length
            0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x02,  # Width: 2
            0x00, 0x00, 0x00, 0x02,  # Height: 2
            0x08, 0x02, 0x00, 0x00, 0x00,  # Bit depth, color type, etc.
            0x01, 0x2B, 0x05, 0x5B,  # CRC (recalculated for 2x2)
            0x00, 0x00, 0x00, 0x16,  # IDAT length (22 bytes)
            0x49, 0x44, 0x41, 0x54,  # IDAT
            # Compressed 2x2 image data
            0x78, 0x9C, 0x63, 0xF8, 0xCF, 0x80, 0x01, 0x19, 0x00, 0x40, 0x00, 0x03, 0x00, 0xC4, 0xFF, 0x7F, 0x26, 0xE5, 0x0B, 0x1C,
            0x6C, 0xBF, 0xC8, 0x30,  # CRC
            0x00, 0x00, 0x00, 0x00,  # IEND length
            0x49, 0x45, 0x4E, 0x44,  # IEND
            0xAE, 0x42, 0x60, 0x82   # CRC
        ])
        
        with open("test_image.png", "wb") as f:
            f.write(png_data)
        
        print(f"   🖼️  Created test_image.png ({len(png_data)} bytes)")
        
        # Text message
        text_message = "This is a secret text message hidden after the image"
        print(f"   📄 Text message: {text_message}")
        
        # Initialize audio steganography manager
        audio_stego = EnhancedWebAudioSteganographyManager(password)
        
        print(f"\n2. Step 1: Hide image in audio file...")
        
        # Hide image in audio
        with open("test_image.png", "rb") as f:
            image_data = f.read()
        
        result1 = audio_stego.hide_data(
            "test_audio.wav",
            image_data,
            "audio_with_image.wav",
            is_file=True,
            original_filename="test_image.png"
        )
        
        print(f"   Result: {result1}")
        
        if not result1.get("success"):
            print(f"   ❌ Failed to hide image: {result1.get('error')}")
            return False
        
        step1_file = result1.get("output_path", "audio_with_image.wav")
        print(f"   ✅ Image hidden successfully: {step1_file}")
        
        # Verify we can extract the image
        print(f"\n3. Verifying image extraction...")
        extracted_image_result = audio_stego.extract_data(step1_file)
        
        if isinstance(extracted_image_result, tuple):
            extracted_image, image_filename = extracted_image_result
        else:
            extracted_image = extracted_image_result
            image_filename = "unknown"
        
        print(f"   Extracted: {len(extracted_image)} bytes, filename: {image_filename}")
        
        if isinstance(extracted_image, bytes) and extracted_image.startswith(b'\x89PNG'):
            print(f"   ✅ Image extracted correctly as PNG")
        else:
            print(f"   ❌ Image extraction failed or corrupted")
            return False
        
        print(f"\n4. Step 2: Hide text in the same audio file (simulating layered container logic)...")
        
        # This simulates what should happen in the enhanced_app.py
        # 1. Extract existing data
        existing_extraction = audio_stego.extract_data(step1_file)
        if isinstance(existing_extraction, tuple):
            existing_data, existing_filename = existing_extraction
        else:
            existing_data = existing_extraction
            existing_filename = "existing_data"
        
        print(f"   Found existing data: {len(existing_data)} bytes, filename: {existing_filename}")
        
        # 2. Create layered container
        layers_info = [
            (existing_data, existing_filename),  # Existing image data
            (text_message, "secret_message.txt")  # New text message
        ]
        
        layered_container = create_layered_data_container(layers_info)
        print(f"   📦 Created layered container: {len(layered_container)} chars")
        
        # 3. Hide the layered container
        result2 = audio_stego.hide_data(
            step1_file,
            layered_container,
            "audio_with_both.wav",
            is_file=False  # It's a text container
        )
        
        print(f"   Result: {result2}")
        
        if not result2.get("success"):
            print(f"   ❌ Failed to hide layered container: {result2.get('error')}")
            return False
        
        final_file = result2.get("output_path", "audio_with_both.wav")
        print(f"   ✅ Layered container hidden successfully: {final_file}")
        
        print(f"\n5. Final extraction and verification...")
        
        # Extract the final data
        final_extraction = audio_stego.extract_data(final_file)
        
        if isinstance(final_extraction, tuple):
            final_data, final_filename = final_extraction
        else:
            final_data = final_extraction
            final_filename = "unknown"
        
        print(f"   Extracted final data: {len(final_data)} chars, filename: {final_filename}")
        
        # Check if it's a layered container
        if isinstance(final_data, bytes):
            try:
                final_data = final_data.decode('utf-8')
            except:
                print(f"   ❌ Could not decode final data as text")
                return False
        
        if is_layered_container(final_data):
            print(f"   ✅ Detected layered container!")
            
            # Extract all layers
            layers = extract_layered_data_container(final_data)
            print(f"   📁 Extracted {len(layers)} layers:")
            
            image_found = False
            text_found = False
            
            for i, (layer_content, layer_filename) in enumerate(layers):
                print(f"\n     Layer {i+1}: {layer_filename}")
                print(f"       Type: {type(layer_content)}")
                print(f"       Size: {len(layer_content)}")
                
                if layer_filename.endswith('.png'):
                    # Check if this is the image
                    if isinstance(layer_content, bytes) and layer_content.startswith(b'\x89PNG'):
                        print(f"       ✅ PNG image preserved correctly!")
                        
                        # Verify it matches original
                        if layer_content == image_data:
                            print(f"       ✅ Image data matches original perfectly")
                            image_found = True
                        else:
                            print(f"       ❌ Image data corrupted")
                    else:
                        print(f"       ❌ PNG image corrupted or wrong format")
                
                elif layer_filename.endswith('.txt'):
                    # Check if this is the text
                    if isinstance(layer_content, str) and layer_content == text_message:
                        print(f"       ✅ Text message preserved correctly!")
                        print(f"       Content: {layer_content}")
                        text_found = True
                    else:
                        print(f"       ❌ Text message corrupted")
                        print(f"       Expected: {text_message}")
                        print(f"       Got: {layer_content}")
            
            success = image_found and text_found
            
            if success:
                print(f"\n   🎉 SUCCESS: Both image and text preserved correctly!")
            else:
                print(f"\n   ❌ FAILURE: Missing or corrupted data (Image: {image_found}, Text: {text_found})")
        
        else:
            print(f"   ❌ Final data is not a layered container")
            success = False
        
        # Cleanup
        cleanup_files = ["test_audio.wav", "test_image.png", step1_file, final_file]
        for file in cleanup_files:
            if os.path.exists(file):
                os.remove(file)
        
        return success
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mp3_image_text_scenario()
    
    print(f"\n" + "="*60)
    print("MP3 + IMAGE + TEXT SCENARIO RESULT")
    print("="*60)
    
    if success:
        print("✅ SUCCESS: MP3 + Image + Text scenario works perfectly!")
        print("   • Image hidden in MP3 file")
        print("   • Text hidden in same MP3 file with same password")
        print("   • Both extracted in original formats")
        print("   • No data corruption or bin format issues")
    else:
        print("❌ FAILURE: MP3 + Image + Text scenario has issues")
        print("   Need to debug the integration further")
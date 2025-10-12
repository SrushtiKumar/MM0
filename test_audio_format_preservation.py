#!/usr/bin/env python3
"""
Test audio steganography file format preservation
Specifically testing hiding images inside audio files
"""
import os
import shutil
import tempfile
from pathlib import Path

def create_test_files():
    """Create test files for audio steganography testing"""
    print("📁 Creating test files...")
    
    # Create a test PNG image file
    test_image_path = "test_image_for_audio.png"
    if not os.path.exists(test_image_path):
        # Create a simple PNG file content (basic PNG header + minimal data)
        png_header = b'\x89PNG\r\n\x1a\n'
        ihdr_chunk = b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        idat_chunk = b'\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x8e\xfc\xe7\x00'
        iend_chunk = b'\x00\x00\x00\x00IEND\xaeB`\x82'
        png_content = png_header + ihdr_chunk + idat_chunk + iend_chunk
        
        with open(test_image_path, 'wb') as f:
            f.write(png_content)
        print(f"  Created test PNG: {test_image_path}")
    
    # Create a test DOC file
    test_doc_path = "test_document_for_audio.doc"
    if not os.path.exists(test_doc_path):
        # Create a simple DOC file content (minimal DOC structure)
        doc_content = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' + b'Test document content for audio steganography' + b'\x00' * 100
        with open(test_doc_path, 'wb') as f:
            f.write(doc_content)
        print(f"  Created test DOC: {test_doc_path}")
    
    # Create a test WAV audio file
    test_audio_path = "test_audio_carrier.wav"
    if not os.path.exists(test_audio_path):
        try:
            import numpy as np
            import soundfile as sf
            
            # Generate 3 seconds of test audio at 44100 Hz
            sample_rate = 44100
            duration = 3.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            frequency = 440.0  # A4 note
            audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
            
            sf.write(test_audio_path, audio_data, sample_rate)
            print(f"  Created test WAV: {test_audio_path}")
        except ImportError:
            print("  soundfile not available, creating basic WAV file...")
            # Create a minimal WAV file
            wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
            wav_data = b'\x00\x00' * 1024  # Simple silence
            with open(test_audio_path, 'wb') as f:
                f.write(wav_header + wav_data)
            print(f"  Created basic WAV: {test_audio_path}")
    
    return test_image_path, test_doc_path, test_audio_path

def test_audio_image_hiding():
    """Test hiding image files in audio and check format preservation"""
    print("\n🎵 Testing Audio Steganography - Image File Format Preservation")
    print("=" * 70)
    
    # Create test files
    test_image_path, test_doc_path, test_audio_path = create_test_files()
    
    try:
        from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager
        
        # Test 1: Hide PNG image in WAV audio
        print("\n📸 Test 1: Hide PNG image in WAV audio")
        print("-" * 40)
        
        manager = EnhancedWebAudioSteganographyManager(password="test123")
        output_path = "audio_with_hidden_image.wav"
        
        print(f"  Hiding {test_image_path} in {test_audio_path}")
        print(f"  Expected: Extracted file should be .png, not .bin")
        
        # Hide the image
        result = manager.hide_data(
            test_audio_path,
            test_image_path,
            output_path,
            is_file=True
        )
        
        if result.get('success'):
            print(f"  ✅ Hiding successful: {result.get('message', '')}")
            
            # Extract and check format
            print(f"  Extracting from {output_path}...")
            extracted_data, extracted_filename = manager.extract_data(output_path)
            
            if extracted_data and extracted_filename:
                print(f"  📤 Extracted filename: {extracted_filename}")
                
                # Check if it's preserving the .png extension
                if extracted_filename.endswith('.png'):
                    print(f"  ✅ FORMAT PRESERVED: {extracted_filename} (correct .png extension)")
                    
                    # Save extracted file and verify
                    with open(f"extracted_{extracted_filename}", 'wb') as f:
                        f.write(extracted_data)
                    print(f"  💾 Saved extracted file: extracted_{extracted_filename}")
                    
                elif extracted_filename.endswith('.bin'):
                    print(f"  ❌ FORMAT ISSUE: {extracted_filename} (should be .png, not .bin)")
                    print(f"  🐛 BUG CONFIRMED: Audio steganography not preserving PNG format")
                else:
                    print(f"  ⚠️  UNEXPECTED: {extracted_filename} (neither .png nor .bin)")
            else:
                print(f"  ❌ Extraction failed")
        else:
            print(f"  ❌ Hiding failed: {result.get('error', 'Unknown error')}")
        
        # Test 2: Hide DOC file in WAV audio  
        print(f"\n📄 Test 2: Hide DOC file in WAV audio")
        print("-" * 40)
        
        output_path2 = "audio_with_hidden_doc.wav"
        
        print(f"  Hiding {test_doc_path} in {test_audio_path}")
        print(f"  Expected: Extracted file should be .doc, not .bin")
        
        # Hide the document
        result2 = manager.hide_data(
            test_audio_path,
            test_doc_path,
            output_path2,
            is_file=True
        )
        
        if result2.get('success'):
            print(f"  ✅ Hiding successful: {result2.get('message', '')}")
            
            # Extract and check format
            print(f"  Extracting from {output_path2}...")
            extracted_data2, extracted_filename2 = manager.extract_data(output_path2)
            
            if extracted_data2 and extracted_filename2:
                print(f"  📤 Extracted filename: {extracted_filename2}")
                
                # Check if it's preserving the .doc extension
                if extracted_filename2.endswith('.doc'):
                    print(f"  ✅ FORMAT PRESERVED: {extracted_filename2} (correct .doc extension)")
                    
                    # Save extracted file
                    with open(f"extracted_{extracted_filename2}", 'wb') as f:
                        f.write(extracted_data2)
                    print(f"  💾 Saved extracted file: extracted_{extracted_filename2}")
                    
                elif extracted_filename2.endswith('.bin'):
                    print(f"  ❌ FORMAT ISSUE: {extracted_filename2} (should be .doc, not .bin)")
                    print(f"  🐛 BUG CONFIRMED: Audio steganography not preserving DOC format")
                else:
                    print(f"  ⚠️  UNEXPECTED: {extracted_filename2} (neither .doc nor .bin)")
            else:
                print(f"  ❌ Extraction failed")
        else:
            print(f"  ❌ Hiding failed: {result2.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Audio steganography module not available: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print(f"\n" + "=" * 70)
    print("🎯 DIAGNOSIS: If files extract as .bin instead of original format,")
    print("   the audio steganography manager is not passing original_filename")
    print("   to the underlying steganography module.")
    print("=" * 70)

if __name__ == "__main__":
    test_audio_image_hiding()
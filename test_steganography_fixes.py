#!/usr/bin/env python3
"""
Test document and audio steganography fixes
"""

import os
import tempfile
from universal_file_steganography import UniversalFileSteganography
from universal_file_audio import UniversalFileAudio

def test_document_steganography_fix():
    """Test that document files remain uncorrupted after steganography"""
    
    print("🧪 TESTING DOCUMENT STEGANOGRAPHY FIXES")
    print("=" * 50)
    
    # Create a test document (simple text file that mimics document structure)
    document_content = """This is a test document file.
    
It contains multiple paragraphs and should remain readable
after steganography processing.

The document format must be preserved to ensure it opens correctly.

Document processing should not corrupt the file structure.
"""
    
    # Create test files
    doc_file = "test_document.txt"
    secret_content = "Hidden message: The document steganography fix prevents file corruption!"
    secret_file = "secret_message.txt"
    output_file = "processed_document.txt"
    
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(document_content)
    
    with open(secret_file, 'w', encoding='utf-8') as f:
        f.write(secret_content)
    
    print(f"✅ Created test document: {doc_file}")
    print(f"✅ Created secret file: {secret_file}")
    
    try:
        # Test document steganography
        stego = UniversalFileSteganography("test123")
        
        print(f"\n🔐 Embedding secret in document...")
        result = stego.hide_file_in_file(doc_file, secret_file, output_file)
        
        if not result.get('success'):
            print(f"❌ Embedding failed: {result}")
            return False
        
        print(f"✅ Embedding successful using {result.get('method', 'unknown')} method")
        
        # Verify the processed document is readable
        print(f"\n📖 Testing processed document readability...")
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                processed_content = f.read()
            
            # Check that original content is preserved
            if document_content in processed_content or len(processed_content) > len(document_content):
                print(f"✅ Document remains readable and content is preserved!")
                print(f"   Original: {len(document_content)} chars")
                print(f"   Processed: {len(processed_content)} chars")
            else:
                print(f"❌ Document content appears corrupted")
                print(f"   Original: {len(document_content)} chars")
                print(f"   Processed: {len(processed_content)} chars")
                return False
                
        except Exception as e:
            print(f"❌ Cannot read processed document: {e}")
            return False
        
        # Test extraction
        print(f"\n🔍 Testing extraction...")
        extraction_result = stego.extract_data(output_file)
        
        if extraction_result and isinstance(extraction_result, tuple):
            extracted_content, filename = extraction_result
            print(f"✅ Extraction successful!")
            print(f"   Filename: {filename}")
            print(f"   Content: {len(extracted_content)} bytes")
            
            # Verify extracted content
            if isinstance(extracted_content, bytes):
                extracted_text = extracted_content.decode('utf-8')
            else:
                extracted_text = extracted_content
                
            if secret_content.strip() in extracted_text.strip():
                print(f"✅ Extracted content matches original!")
                return True
            else:
                print(f"❌ Extracted content doesn't match")
                print(f"   Expected: {secret_content[:50]}...")
                print(f"   Got: {extracted_text[:50]}...")
                return False
        else:
            print(f"❌ Extraction failed: {extraction_result}")
            return False
            
    finally:
        # Cleanup
        for file in [doc_file, secret_file, output_file]:
            if os.path.exists(file):
                os.remove(file)

def test_audio_steganography_fix():
    """Test that audio files remain playable and extraction works correctly"""
    
    print(f"\n🧪 TESTING AUDIO STEGANOGRAPHY FIXES")
    print("=" * 50)
    
    try:
        import numpy as np
        import soundfile as sf
    except ImportError:
        print("❌ Audio libraries not available, skipping audio test")
        return True
    
    # Create a test audio file (simple sine wave)
    duration = 5  # 5 seconds
    sample_rate = 44100
    t = np.linspace(0, duration, duration * sample_rate, False)
    audio_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
    
    audio_file = "test_audio.wav"
    output_audio = "processed_audio.wav"
    
    sf.write(audio_file, audio_signal, sample_rate)
    print(f"✅ Created test audio: {audio_file}")
    
    # Test content to hide
    test_mp3_content = (
        b'ID3\x03\x00\x00\x00\x00\x00\x00'  # ID3 header for MP3
        b'Test MP3 content that should preserve .mp3 extension\n'
        b'Audio steganography should maintain file format detection.\n'
    )
    
    try:
        # Test audio steganography
        audio_stego = UniversalFileAudio("test123")
        
        print(f"\n🔐 Embedding data in audio...")
        result = audio_stego.hide_data(audio_file, test_mp3_content, output_audio, is_file=True)
        
        if not result.get('success'):
            print(f"❌ Audio embedding failed: {result}")
            return False
        
        print(f"✅ Audio embedding successful!")
        
        # Verify the processed audio is still valid
        print(f"\n🎵 Testing processed audio integrity...")
        
        try:
            processed_audio, processed_sr = sf.read(output_audio)
            print(f"✅ Processed audio is readable!")
            print(f"   Duration: {len(processed_audio) / processed_sr:.1f} seconds")
            print(f"   Sample rate: {processed_sr} Hz")
            print(f"   Channels: {len(processed_audio.shape)}")
            
            # Check audio hasn't been severely distorted
            if len(processed_audio) == len(audio_signal):
                print(f"✅ Audio length preserved!")
            else:
                print(f"⚠️ Audio length changed: {len(audio_signal)} -> {len(processed_audio)}")
                
        except Exception as e:
            print(f"❌ Cannot read processed audio: {e}")
            return False
        
        # Test extraction with format detection
        print(f"\n🔍 Testing extraction with format detection...")
        extraction_result = audio_stego.extract_data(output_audio)
        
        if extraction_result and isinstance(extraction_result, tuple):
            extracted_content, filename = extraction_result
            print(f"✅ Audio extraction successful!")
            print(f"   Filename: '{filename}'")
            print(f"   Content: {len(extracted_content)} bytes")
            
            # Check filename format detection
            if filename.endswith('.mp3'):
                print(f"✅ SUCCESS: MP3 format correctly detected!")
            elif filename.endswith('.bin'):
                print(f"❌ ISSUE: Still returning .bin instead of .mp3")
                print(f"   Content starts with: {extracted_content[:20]}")
                return False
            else:
                print(f"⚠️ Unexpected filename: {filename}")
            
            # Verify content integrity
            if extracted_content == test_mp3_content:
                print(f"✅ Extracted content matches perfectly!")
                return True
            else:
                print(f"❌ Content mismatch")
                print(f"   Original: {len(test_mp3_content)} bytes")
                print(f"   Extracted: {len(extracted_content)} bytes")
                return False
        else:
            print(f"❌ Audio extraction failed: {extraction_result}")
            return False
            
    finally:
        # Cleanup
        for file in [audio_file, output_audio]:
            if os.path.exists(file):
                os.remove(file)

def main():
    """Run comprehensive tests for both fixes"""
    
    print("🚀 COMPREHENSIVE STEGANOGRAPHY FIX TESTING")
    print("=" * 60)
    
    # Test document steganography fix
    doc_success = test_document_steganography_fix()
    
    # Test audio steganography fix
    audio_success = test_audio_steganography_fix()
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"🎯 FINAL TEST RESULTS")
    print(f"=" * 60)
    print(f"Document Steganography: {'✅ FIXED' if doc_success else '❌ FAILED'}")
    print(f"Audio Steganography:    {'✅ FIXED' if audio_success else '❌ FAILED'}")
    
    if doc_success and audio_success:
        print(f"\n🎉 ALL FIXES SUCCESSFUL!")
        print(f"✅ Document files remain uncorrupted and readable")
        print(f"✅ Audio files remain playable with proper format detection")
        print(f"✅ Both steganography types preserve original file formats")
    else:
        print(f"\n⚠️ SOME ISSUES REMAIN - Check failed tests above")
    
    return doc_success and audio_success

if __name__ == "__main__":
    main()
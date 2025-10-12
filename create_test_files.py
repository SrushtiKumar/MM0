#!/usr/bin/env python3
"""
Create test files for steganography testing
"""

import numpy as np
import cv2
import os
from pathlib import Path

def create_test_video():
    """Create a simple test MP4 video"""
    print("🎬 Creating test video...")
    
    # Video parameters
    width, height = 640, 480
    fps = 10
    duration = 3  # seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('test_video.mp4', fourcc, fps, (width, height))
    
    for frame_num in range(total_frames):
        # Create a frame with changing colors
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some pattern
        color_intensity = int(255 * (frame_num / total_frames))
        frame[:, :] = [color_intensity, 100, 255 - color_intensity]
        
        # Add frame number text
        cv2.putText(frame, f'Frame {frame_num}', (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print("✅ Test video created: test_video.mp4")

def create_test_mp3():
    """Create a simple test MP3 audio file"""
    print("🎵 Creating test MP3...")
    
    try:
        # Try using pydub if available
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Generate a 3-second 440Hz tone (A4 note)
        tone = Sine(440).to_audio_segment(duration=3000)
        
        # Export as MP3
        tone.export("test_audio.mp3", format="mp3")
        print("✅ Test MP3 created: test_audio.mp3")
        
    except ImportError:
        print("⚠️  pydub not available, creating placeholder MP3...")
        
        # Create a minimal MP3-like file with ID3 header
        mp3_header = b'ID3\x03\x00\x00\x00\x00\x00\x00'  # Minimal ID3v2 header
        mp3_data = b'\xff\xfb\x90\x00' + b'\x00' * 1000  # Minimal MP3 frame + padding
        
        with open("test_audio.mp3", "wb") as f:
            f.write(mp3_header + mp3_data)
        
        print("✅ Placeholder MP3 created: test_audio.mp3")

def create_test_image():
    """Create a simple test PNG image"""
    print("🖼️  Creating test image...")
    
    # Create a colorful test image
    img = np.random.randint(0, 256, (400, 400, 3), dtype=np.uint8)
    
    # Add some pattern
    cv2.rectangle(img, (50, 50), (350, 350), (255, 255, 255), 5)
    cv2.putText(img, 'Test Image', (120, 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    cv2.imwrite('test_image.png', img)
    print("✅ Test image created: test_image.png")

def create_test_document():
    """Create a simple test PDF document"""
    print("📄 Creating test document...")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas("test_document.pdf", pagesize=letter)
        c.drawString(100, 750, "Test Document for Steganography")
        c.drawString(100, 700, "This is a sample PDF document.")
        c.drawString(100, 650, "It will be used for testing document steganography.")
        c.save()
        
        print("✅ Test PDF created: test_document.pdf")
        
    except ImportError:
        print("⚠️  reportlab not available, creating text document...")
        
        # Create a text document instead
        content = """Test Document for Steganography

This is a sample text document.
It will be used for testing document steganography.
The document contains multiple lines of text.
Hidden data can be embedded using various techniques.

End of document.
"""
        with open("test_document.txt", "w") as f:
            f.write(content)
        
        print("✅ Test text document created: test_document.txt")

def create_test_wav():
    """Create a simple test WAV audio file"""
    print("🎶 Creating test WAV...")
    
    try:
        import soundfile as sf
        
        # Generate 3 seconds of test audio at 44100 Hz
        sample_rate = 44100
        duration = 3.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Generate a simple sine wave (440 Hz)
        frequency = 440.0
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        sf.write("test_audio.wav", audio_data, sample_rate)
        print("✅ Test WAV created: test_audio.wav")
        
    except ImportError:
        print("⚠️  soundfile not available, creating minimal WAV...")
        
        # Create a minimal WAV file header
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xAC\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        wav_data = b'\x00\x00' * 1000  # Silent audio data
        
        with open("test_audio.wav", "wb") as f:
            f.write(wav_header + wav_data)
        
        print("✅ Minimal WAV created: test_audio.wav")

if __name__ == "__main__":
    print("🛠️  Creating test files for steganography...")
    print("=" * 50)
    
    # Create test files
    create_test_video()
    create_test_mp3()
    create_test_image() 
    create_test_document()
    create_test_wav()
    
    print("\n✅ All test files created successfully!")
    print("You can now run the steganography tests.")
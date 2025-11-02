import sys
import os
sys.path.append(os.getcwd())

import numpy as np
import pywt
import librosa
import soundfile as sf

def test_robust_dwt_embedding():
    """Test a more robust DWT embedding approach"""
    print("Testing robust DWT embedding approach...")
    
    # Load audio
    audio_path = 'test_audio_carrier.wav'
    y, sr = librosa.load(audio_path, sr=None)
    
    print(f"Audio loaded: {len(y)} samples at {sr} Hz")
    
    # Use first 95% for embedding
    segment = y[:int(len(y) * 0.95)]
    
    # DWT parameters
    wavelet = 'db4'
    level = 4
    coeffs = pywt.wavedec(segment, wavelet, level=level)
    
    print(f"DWT decomposition: {len(coeffs)} levels")
    for i, coeff in enumerate(coeffs):
        print(f"  Level {i}: {len(coeff)} coefficients, range: [{np.min(coeff):.3f}, {np.max(coeff):.3f}]")
    
    # Test embedding simple pattern in detail band 2 (usually has good capacity)
    detail_band = 2
    if detail_band >= len(coeffs):
        detail_band = len(coeffs) - 1
    
    print(f"\nTesting embedding in detail band {detail_band}")
    
    # Simple test pattern
    test_bits = "11001100" * 10  # 80 bits
    print(f"Test pattern: {test_bits}")
    
    # Embed with very aggressive magnitude changes
    modified_coeffs = [c.copy() for c in coeffs]
    detail = modified_coeffs[detail_band]
    
    embed_positions = []
    for i, bit in enumerate(test_bits):
        if i * 4 < len(detail):  # Use every 4th coefficient for spacing
            pos = i * 4
            original_val = detail[pos]
            
            # Use very large magnitudes to survive DWT reconstruction
            if bit == '1':
                detail[pos] = 1.0  # Strong positive
            else:
                detail[pos] = -1.0  # Strong negative
            
            embed_positions.append((pos, bit, original_val, detail[pos]))
            
            if i < 10:  # Show first 10 modifications
                print(f"  Pos {pos}: bit '{bit}', {original_val:.6f} -> {detail[pos]:.6f}")
    
    print(f"Embedded {len(embed_positions)} bits at positions")
    
    # Reconstruct audio
    modified_audio = pywt.waverec(modified_coeffs, wavelet)
    
    # Save modified audio
    output_path = 'debug_robust_dwt.wav'
    # Ensure same length
    if len(modified_audio) != len(segment):
        if len(modified_audio) > len(segment):
            modified_audio = modified_audio[:len(segment)]
        else:
            padding = np.zeros(len(segment) - len(modified_audio))
            modified_audio = np.concatenate([modified_audio, padding])
    
    # Update full audio
    y_out = y.copy()
    y_out[:len(modified_audio)] = modified_audio
    
    sf.write(output_path, y_out, sr)
    print(f"Modified audio saved to {output_path}")
    
    # Test extraction
    print(f"\nTesting extraction from {output_path}")
    y_test, _ = librosa.load(output_path, sr=None)
    segment_test = y_test[:int(len(y_test) * 0.95)]
    coeffs_test = pywt.wavedec(segment_test, wavelet, level=level)
    
    detail_test = coeffs_test[detail_band]
    
    # Extract bits
    extracted_bits = []
    for i in range(len(test_bits)):
        if i * 4 < len(detail_test):
            pos = i * 4
            coeff = detail_test[pos]
            
            # Simple threshold extraction
            bit = '1' if coeff > 0 else '0'
            extracted_bits.append(bit)
            
            if i < 10:  # Show first 10 extractions
                original_pos, original_bit, original_orig, original_mod = embed_positions[i]
                print(f"  Pos {pos}: coeff {coeff:.6f} -> bit '{bit}' (original: '{original_bit}')")
    
    extracted_pattern = ''.join(extracted_bits)
    print(f"\nOriginal:  {test_bits}")
    print(f"Extracted: {extracted_pattern}")
    
    # Calculate accuracy
    matches = sum(1 for i in range(min(len(test_bits), len(extracted_pattern))) 
                 if test_bits[i] == extracted_pattern[i])
    accuracy = matches / min(len(test_bits), len(extracted_pattern)) * 100
    
    print(f"Accuracy: {accuracy:.1f}% ({matches}/{min(len(test_bits), len(extracted_pattern))})")
    
    if accuracy > 90:
        print("✅ Robust DWT embedding works well")
    elif accuracy > 50:
        print("⚠️ Robust DWT embedding has some issues")
    else:
        print("❌ Robust DWT embedding fails")

if __name__ == "__main__":
    test_robust_dwt_embedding()
#!/usr/bin/env python3
"""
Universal File-in-File Steganography
====================================

This module provides the ability to hide any file inside any other file
using advanced steganographic techniques. Unlike traditional steganography
that relies on specific container formats (images, audio), this system
can hide files in ANY file type.

Features:
- Hide any file inside any other file
- Least Significant Bit (LSB) steganography for binary files
- Text-based steganography using whitespace and formatting
- Redundancy and error correction
- Password protection with AES encryption
- Perfect file integrity preservation

Author: Enhanced Steganography System
"""

import os
import sys
import hashlib
import json
import struct
import random
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

# Cryptography
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import secrets

class UniversalFileSteganography:
    """Universal file-in-file steganography system"""
    
    def __init__(self, password: str = None):
        self.password = password
        self.magic_header = b"UNISTEGOFILE"
        self.redundancy = 3  # For error correction
        
    def hide_file_in_file(self, container_path: str, secret_file_path: str, output_path: str) -> Dict[str, Any]:
        """Hide a file inside another file"""
        
        print(f"[+] Hiding '{secret_file_path}' inside '{container_path}'")
        
        # Read container and secret files
        with open(container_path, 'rb') as f:
            container_data = f.read()
        
        with open(secret_file_path, 'rb') as f:
            secret_data = f.read()
        
        # Get file info
        secret_filename = os.path.basename(secret_file_path)
        container_type = self._detect_container_type(container_path)
        
        print(f"[+] Container type: {container_type}")
        print(f"[+] Secret file: {secret_file_path} ({len(secret_data)} bytes)")
        print(f"[+] Container size: {len(container_data)} bytes")
        
        # Create metadata
        metadata = {
            'magic': self.magic_header.decode('latin-1'),
            'filename': secret_filename,
            'file_size': len(secret_data),
            'container_type': container_type,
            'checksum': hashlib.sha256(secret_data).hexdigest()[:16]
        }
        
        # Encrypt if password provided
        if self.password:
            encrypted_data = self._encrypt_data(secret_data)
            payload = encrypted_data
            metadata['encrypted'] = True
        else:
            payload = secret_data
            metadata['encrypted'] = False
        
        # Create full payload with metadata
        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_length = struct.pack('<I', len(metadata_json))
        full_payload = self.magic_header + metadata_length + metadata_json + payload
        
        print(f"[+] Total payload: {len(full_payload)} bytes")
        
        # Choose embedding method based on container type
        if container_type in ['text', 'source_code']:
            modified_container = self._embed_in_text(container_data, full_payload)
        else:
            modified_container = self._embed_in_binary(container_data, full_payload)
        
        # Calculate capacity usage
        capacity_used = (len(full_payload) * 8) / (len(container_data) * 8) * 100
        
        # Save result
        with open(output_path, 'wb') as f:
            f.write(modified_container)
        
        print(f"[+] File hidden successfully in '{output_path}'")
        print(f"[+] Capacity used: {capacity_used:.1f}%")
        
        return {
            'success': True,
            'secret_file_size': len(secret_data),
            'container_size': len(container_data),
            'output_size': len(modified_container),
            'capacity_used': f"{capacity_used:.1f}%",
            'method': 'text' if container_type in ['text', 'source_code'] else 'binary',
            'encrypted': metadata['encrypted']
        }
    
    def extract_file_from_file(self, stego_file_path: str, output_dir: str = None) -> str:
        """Extract hidden file from container"""
        
        print(f"[+] Extracting hidden file from '{stego_file_path}'")
        
        with open(stego_file_path, 'rb') as f:
            stego_data = f.read()
        
        # Detect container type to choose extraction method
        container_type = self._detect_container_type(stego_file_path)
        
        if container_type in ['text', 'source_code']:
            payload = self._extract_from_text(stego_data)
        else:
            payload = self._extract_from_binary(stego_data)
        
        if not payload:
            raise ValueError("No hidden file found or extraction failed")
        
        # Parse metadata
        if not payload.startswith(self.magic_header):
            raise ValueError("Invalid file format or corrupted data")
        
        offset = len(self.magic_header)
        metadata_length = struct.unpack('<I', payload[offset:offset+4])[0]
        offset += 4
        
        metadata_json = payload[offset:offset+metadata_length]
        metadata = json.loads(metadata_json.decode('utf-8'))
        offset += metadata_length
        
        # Extract file data
        file_data = payload[offset:]
        
        # Decrypt if needed
        if metadata.get('encrypted', False):
            if not self.password:
                raise ValueError("Password required for encrypted file")
            file_data = self._decrypt_data(file_data)
        
        # Verify integrity
        actual_checksum = hashlib.sha256(file_data).hexdigest()[:16]
        expected_checksum = metadata['checksum']
        
        if actual_checksum != expected_checksum:
            print(f"⚠️ Warning: Checksum mismatch (expected: {expected_checksum}, got: {actual_checksum})")
        
        # Save extracted file
        output_dir = output_dir or os.getcwd()
        output_filename = f"extracted_{metadata['filename']}"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        print(f"[SUCCESS] File extracted successfully!")
        print(f"[+] Original filename: {metadata['filename']}")
        print(f"[+] File size: {len(file_data)} bytes")
        print(f"[+] Saved as: {output_path}")
        
        return output_path
    
    def _detect_container_type(self, file_path: str) -> str:
        """Detect if file is text-based or binary"""
        
        try:
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024)  # Read first 1KB
            
            # Check if it's likely source code
            code_extensions = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h']
            if any(file_path.lower().endswith(ext) for ext in code_extensions):
                return 'source_code'
            
            # Check if it's plain text
            text_extensions = ['.txt', '.md', '.log', '.csv']
            if any(file_path.lower().endswith(ext) for ext in text_extensions):
                return 'text'
            
            # If readable as UTF-8, consider it text
            if all(ord(c) < 128 for c in content[:100]):  # ASCII check
                return 'text'
                
        except (UnicodeDecodeError, IOError):
            pass
        
        return 'binary'
    
    def _embed_in_text(self, container_data: bytes, payload: bytes) -> bytes:
        """Embed data in text file using whitespace steganography"""
        
        try:
            # Convert to text
            container_text = container_data.decode('utf-8')
            
            # Convert payload to binary string
            payload_bits = ''.join(format(byte, '08b') for byte in payload)
            
            print(f"[+] Using whitespace steganography for text file")
            print(f"[+] Embedding {len(payload_bits)} bits")
            
            # Use spaces/tabs to encode bits (space = 0, tab = 1)
            # Add redundancy by embedding each bit multiple times
            modified_text = ""
            bit_index = 0
            
            for char in container_text:
                modified_text += char
                
                # Add hidden bits after certain characters
                if char in [' ', '\n', '.', ',', ';', ':', '!', '?'] and bit_index < len(payload_bits):
                    # Embed bit using invisible characters
                    bit = payload_bits[bit_index]
                    
                    # Use zero-width characters for steganography
                    if bit == '1':
                        # Zero-width space (U+200B) for 1
                        modified_text += '\u200B'
                    else:
                        # Zero-width non-joiner (U+200C) for 0  
                        modified_text += '\u200C'
                    
                    bit_index += 1
            
            # If we haven't embedded all bits, append to end with invisible chars
            while bit_index < len(payload_bits):
                bit = payload_bits[bit_index]
                if bit == '1':
                    modified_text += '\u200B'
                else:
                    modified_text += '\u200C'
                bit_index += 1
            
            return modified_text.encode('utf-8')
            
        except Exception as e:
            print(f"⚠️ Text embedding failed: {e}, falling back to binary method")
            return self._embed_in_binary(container_data, payload)
    
    def _embed_in_binary(self, container_data: bytes, payload: bytes) -> bytes:
        """Embed data in binary file using LSB steganography"""
        
        container_array = bytearray(container_data)
        payload_bits = ''.join(format(byte, '08b') for byte in payload)
        
        print(f"💾 Using LSB steganography for binary file")
        print(f"🔢 Embedding {len(payload_bits)} bits")
        
        # Check capacity
        available_bits = len(container_array) * 8 // self.redundancy
        if len(payload_bits) > available_bits:
            raise ValueError(f"Payload too large: need {len(payload_bits)} bits, have {available_bits}")
        
        # Embed with redundancy
        bit_index = 0
        for i in range(0, len(payload_bits) * self.redundancy, self.redundancy):
            if i // self.redundancy >= len(payload_bits):
                break
                
            bit = payload_bits[i // self.redundancy]
            
            # Embed the same bit in multiple positions for redundancy
            for r in range(self.redundancy):
                byte_pos = (i + r) % len(container_array)
                
                # Modify LSB
                if bit == '1':
                    container_array[byte_pos] |= 1  # Set LSB to 1
                else:
                    container_array[byte_pos] &= 0xFE  # Set LSB to 0
        
        return bytes(container_array)
    
    def _extract_from_text(self, stego_data: bytes) -> Optional[bytes]:
        """Extract data from text file using whitespace analysis"""
        
        try:
            # Convert to text
            stego_text = stego_data.decode('utf-8')
            
            print(f"[+] Extracting from text using whitespace analysis")
            
            # Extract hidden bits from zero-width characters
            extracted_bits = ""
            
            for char in stego_text:
                if char == '\u200B':  # Zero-width space = 1
                    extracted_bits += '1'
                elif char == '\u200C':  # Zero-width non-joiner = 0
                    extracted_bits += '0'
            
            if not extracted_bits:
                print("❌ No hidden data found in text")
                return None
            
            print(f"🔢 Extracted {len(extracted_bits)} bits")
            
            # Convert bits to bytes
            extracted_bytes = bytearray()
            for i in range(0, len(extracted_bits), 8):
                if i + 7 < len(extracted_bits):
                    byte_bits = extracted_bits[i:i+8]
                    extracted_bytes.append(int(byte_bits, 2))
            
            return bytes(extracted_bytes)
            
        except Exception as e:
            print(f"⚠️ Text extraction failed: {e}, trying binary method")
            return self._extract_from_binary(stego_data)
    
    def _extract_from_binary(self, stego_data: bytes) -> Optional[bytes]:
        """Extract data from binary file using LSB analysis"""
        
        print(f"💾 Extracting from binary using LSB analysis")
        
        # Extract bits from LSBs with majority voting for redundancy
        max_bits = len(stego_data) * 8 // self.redundancy
        extracted_bits = ""
        
        for bit_pos in range(max_bits):
            # Check multiple positions for this bit (redundancy)
            votes = []
            for r in range(self.redundancy):
                byte_pos = (bit_pos * self.redundancy + r) % len(stego_data)
                lsb = stego_data[byte_pos] & 1
                votes.append(str(lsb))
            
            # Majority voting
            bit = '1' if votes.count('1') > votes.count('0') else '0'
            extracted_bits += bit
            
            # Stop when we've found the complete payload
            if len(extracted_bits) >= len(self.magic_header) * 8:
                # Try to parse header to see if we have valid data
                try:
                    temp_bytes = bytearray()
                    for i in range(0, len(extracted_bits), 8):
                        if i + 7 < len(extracted_bits):
                            byte_bits = extracted_bits[i:i+8]
                            temp_bytes.append(int(byte_bits, 2))
                    
                    if bytes(temp_bytes).startswith(self.magic_header):
                        # Continue extracting to get full payload
                        break
                except:
                    continue
            
            # Limit extraction to prevent infinite loop
            if len(extracted_bits) > 1000000:  # 1MB limit
                break
        
        if not extracted_bits:
            return None
        
        # Convert bits to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits), 8):
            if i + 7 < len(extracted_bits):
                byte_bits = extracted_bits[i:i+8]
                extracted_bytes.append(int(byte_bits, 2))
        
        # Find the actual payload by looking for magic header
        payload_data = bytes(extracted_bytes)
        magic_pos = payload_data.find(self.magic_header)
        
        if magic_pos == -1:
            print("❌ No valid payload found")
            return None
        
        # Extract from magic header position
        payload = payload_data[magic_pos:]
        
        # Try to get complete payload by reading metadata
        try:
            offset = len(self.magic_header)
            if len(payload) >= offset + 4:
                metadata_length = struct.unpack('<I', payload[offset:offset+4])[0]
                needed_length = offset + 4 + metadata_length
                
                # Extract more bits if needed
                while len(payload) < needed_length and len(extracted_bits) < len(stego_data) * 8:
                    # Continue bit extraction...
                    bit_pos = len(extracted_bits) // 8
                    if bit_pos * self.redundancy < len(stego_data):
                        votes = []
                        for r in range(self.redundancy):
                            byte_pos = (bit_pos * self.redundancy + r) % len(stego_data)
                            if byte_pos < len(stego_data):
                                lsb = stego_data[byte_pos] & 1
                                votes.append(str(lsb))
                        
                        if votes:
                            bit = '1' if votes.count('1') > votes.count('0') else '0'
                            extracted_bits += bit
                            
                            if len(extracted_bits) % 8 == 0:
                                # Convert new byte
                                byte_bits = extracted_bits[-8:]
                                new_byte = int(byte_bits, 2)
                                payload += bytes([new_byte])
                    else:
                        break
        except:
            pass
        
        print(f"🔢 Extracted {len(payload)} bytes from binary")
        return payload
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-GCM"""
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
        
        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        return salt + nonce + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-GCM"""
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ciphertext = encrypted_data[28:]
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
        
        # Decrypt
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)


def test_universal_file_steganography():
    """Test the universal file steganography system"""
    
    print("🧪 TESTING UNIVERSAL FILE-IN-FILE STEGANOGRAPHY")
    print("=" * 60)
    
    # Create test files
    container_files = {
        'text_container.txt': "This is a plain text file.\nIt contains multiple lines.\nWe will hide a secret file inside it!",
        'script_container.py': '#!/usr/bin/env python3\nprint("This is a Python script")\nresult = 42 + 8\nprint(f"Result: {result}")',
        'binary_container.bin': bytes([i % 256 for i in range(1000)])  # Binary data
    }
    
    secret_files = {
        'secret.txt': "SECRET DOCUMENT\nClassified information here!",
        'data.json': '{"secret": "data", "hidden": true, "value": 12345}'
    }
    
    # Create test files
    for filename, content in container_files.items():
        if isinstance(content, str):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(filename, 'wb') as f:
                f.write(content)
    
    for filename, content in secret_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    stego = UniversalFileSteganography(password="test123")
    
    test_results = []
    
    # Test combinations
    test_cases = [
        ('text_container.txt', 'secret.txt', 'Text in Text'),
        ('script_container.py', 'data.json', 'JSON in Python Script'), 
        ('binary_container.bin', 'secret.txt', 'Text in Binary'),
    ]
    
    for container, secret, description in test_cases:
        print(f"\n🔬 Testing: {description}")
        print("-" * 40)
        
        try:
            # Hide file
            output_file = f"stego_{container}"
            result = stego.hide_file_in_file(container, secret, output_file)
            
            if result['success']:
                print(f"✅ Hiding successful - {result['capacity_used']} capacity used")
                
                # Extract file
                extracted_file = stego.extract_file_from_file(output_file)
                
                # Verify content
                with open(secret, 'rb') as f:
                    original_content = f.read()
                with open(extracted_file, 'rb') as f:
                    extracted_content = f.read()
                
                if original_content == extracted_content:
                    print(f"✅ Extraction and verification successful!")
                    test_results.append(True)
                else:
                    print(f"❌ Content mismatch after extraction")
                    test_results.append(False)
            else:
                print(f"❌ Hiding failed")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            test_results.append(False)
    
    # Cleanup
    all_files = list(container_files.keys()) + list(secret_files.keys())
    all_files += [f"stego_{f}" for f in container_files.keys()]
    all_files += [f"extracted_{f}" for f in secret_files.keys()]
    
    for file in all_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except:
            pass
    
    # Results
    print(f"\n📊 Test Results: {sum(test_results)}/{len(test_results)} passed")
    return sum(test_results) == len(test_results)


if __name__ == "__main__":
    test_universal_file_steganography()
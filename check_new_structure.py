"""
Check the new embedded file structure to see if password was used correctly
"""

def check_new_embedded_file():
    """Check the structure of the newly embedded file"""
    
    embedded_file = r"outputs\stego_carrier_fresh_carrier_1762183532_5fa13b11_1762183532_40f6205d.png"
    magic_header = b"VEILFORGE_UNIVERSAL_SAFE_V2"
    
    print("🔍 CHECKING NEW EMBEDDED FILE")
    print("=" * 50)
    print(f"File: {embedded_file}")
    
    try:
        with open(embedded_file, 'rb') as f:
            file_data = f.read()
        
        print(f"File size: {len(file_data)} bytes")
        
        # Look for magic header
        magic_pos = file_data.find(magic_header)
        
        if magic_pos == -1:
            print("❌ NO MAGIC HEADER FOUND!")
            return False
        else:
            print(f"✅ Magic header found at position: {magic_pos}")
            
            # Parse metadata
            try:
                metadata_size_pos = magic_pos + len(magic_header)
                metadata_size = int.from_bytes(file_data[metadata_size_pos:metadata_size_pos+4], 'little')
                
                metadata_pos = metadata_size_pos + 4
                metadata_json = file_data[metadata_pos:metadata_pos+metadata_size]
                
                import json
                metadata = json.loads(metadata_json.decode('utf-8'))
                print(f"📋 Metadata: {json.dumps(metadata, indent=2)}")
                
                # Parse payload
                data_size_pos = metadata_pos + metadata_size
                data_size = int.from_bytes(file_data[data_size_pos:data_size_pos+4], 'little')
                
                payload_pos = data_size_pos + 4
                payload_data = file_data[payload_pos:payload_pos+data_size]
                
                print(f"📦 Payload size: {data_size} bytes")
                print(f"📦 First 32 bytes: {payload_data[:32].hex()}")
                
                # Check if encrypted
                if metadata.get('encrypted'):
                    print("🔒 Data is encrypted")
                    
                    # Compare with previous file to see if salt/nonce are different
                    salt = payload_data[:16]
                    nonce = payload_data[16:28]
                    
                    print(f"🧂 Salt: {salt.hex()}")
                    print(f"🎯 Nonce: {nonce.hex()}")
                    
                    # Compare with previous salt/nonce from debug output
                    previous_salt = "7658f2aa5e8ef7a8388021bea1c7a550"
                    previous_nonce = "bb36efca37e34b0376c46052"
                    
                    current_salt = salt.hex()
                    current_nonce = nonce.hex()
                    
                    if current_salt == previous_salt and current_nonce == previous_nonce:
                        print("⚠️  SAME SALT/NONCE AS BEFORE - Password issue persists!")
                        return False
                    else:
                        print("✅ DIFFERENT SALT/NONCE - Password is being used correctly!")
                        return True
                        
                else:
                    print("🔓 Data is not encrypted - PASSWORD NOT USED!")
                    return False
                    
            except Exception as e:
                print(f"❌ Error parsing: {e}")
                return False
        
    except FileNotFoundError:
        print("❌ File not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_new_embedded_file()
import nacl.encoding
import nacl.signing

# Generate a new random signing key
signing_key = nacl.signing.SigningKey.generate()

# Sign a message with the signing key
signed = signing_key.sign(b"Attack at Dawn")

# Obtain the verify key for a given signing key
verify_key = signing_key.verify_key

# Serialize the verify key to send it to a third party
verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
signing_key_hex = signing_key.encode(encoder=nacl.encoding.HexEncoder)

print("Verify key:", verify_key_hex)
print("Private key:", signing_key_hex)
print("Message:", (signed))

with open("test.privket", "wb") as f:
    f.write(signing_key_hex)

with open("test.pubkey", "wb") as f:
    f.write(verify_key_hex)

with open("message", "wb") as f:
    f.write(signed)

import base64
import nacl.encoding
import nacl.signing

with open("test.pubkey", "rb") as f:
    verify_key_hex = f.read()

with open("message", "rb") as f:
    message = f.read()

print(type(message))

verify_key = nacl.signing.VerifyKey(verify_key_hex, encoder=nacl.encoding.HexEncoder)

print("Verify key:", verify_key_hex)
print("Message:", message)

print("Verification: {}".format(verify_key.verify(message)))

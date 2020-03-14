import base64
import nacl.encoding
import nacl.signing

with open("test.pubkey", "rb") as f:
    verify_key_hex = f.read()

with open("test.privkey", "rb") as f:
    private_key_hex = f.read()

with open("plaintext", "rb") as f:
    plaintext = f.read()

verify_key = nacl.signing.VerifyKey(verify_key_hex, encoder=nacl.encoding.HexEncoder)
private_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)

signed = private_key.sign(plaintext)

print("Verify key:", verify_key_hex)
print
print("Message:{}\n\n{}\n\n{}".format(signed, signed.message, signed.signature))

with open("ciphertext", "wb") as f:
    f.write(signed)

# print(verify_key.verify(signed.message, signed.signature))

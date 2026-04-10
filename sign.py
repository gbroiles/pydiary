import nacl.encoding
import nacl.signing

if __name__ == "__main__":
    with open("test.privkey", "rb") as f:
        private_key_hex = f.read()

    with open("plaintext", "rb") as f:
        plaintext = f.read()

    private_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)

    signed = private_key.sign(plaintext)

    print(f"Message:{signed}\n\n{signed.message}\n\n{signed.signature}")

    with open("message", "wb") as f:
        f.write(signed)

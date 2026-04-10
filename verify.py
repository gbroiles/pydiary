import nacl.encoding
import nacl.signing

if __name__ == "__main__":
    with open("test.pubkey", "rb") as f:
        verify_key_hex = f.read()

    with open("message", "rb") as f:
        message = f.read()

    verify_key = nacl.signing.VerifyKey(verify_key_hex, encoder=nacl.encoding.HexEncoder)

    print("Verify key:", verify_key_hex)
    print("Message:", message)

    print(f"Verification: {verify_key.verify(message)}")

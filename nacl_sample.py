from nacl import pwhash, secret, utils

if __name__ == "__main__":
    password = b"password shared between Alice and Bob"
    message = b"This is a message for Bob's eyes only"

    kdf = pwhash.argon2i.kdf
    salt = utils.random(pwhash.argon2i.SALTBYTES)
    ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
    mem = pwhash.argon2i.MEMLIMIT_SENSITIVE

    # or, if there is a need to use scrypt:
    # kdf = pwhash.scrypt.kdf
    # salt = utils.random(pwhash.scrypt.SALTBYTES)
    # ops = pwhash.scrypt.OPSLIMIT_SENSITIVE
    # mem = pwhash.scrypt.MEMLIMIT_SENSITIVE

    alice_key = kdf(secret.SecretBox.KEY_SIZE, password, salt, opslimit=ops, memlimit=mem)
    alice_box = secret.SecretBox(alice_key)

    encrypted = alice_box.encrypt(message)

    # now Alice must send to Bob both the encrypted message
    # and the KDF parameters: salt, opslimit and memlimit;
    # using the same kdf mechanism, parameters **and password**
    # Bob is able to derive the correct key to decrypt the message
    #
    # salt must be stored alongside the ciphertext to re-derive the key on decryption.
    # Here we prepend it so the full payload is self-contained.
    payload = salt + encrypted

    # On the receiving end, split off the salt before decrypting.
    received_salt = payload[:pwhash.argon2i.SALTBYTES]
    received_encrypted = payload[pwhash.argon2i.SALTBYTES:]

    bob_key = kdf(secret.SecretBox.KEY_SIZE, password, received_salt, opslimit=ops, memlimit=mem)
    bob_box = secret.SecretBox(bob_key)
    received = bob_box.decrypt(received_encrypted)
    print(received.decode("utf-8"))

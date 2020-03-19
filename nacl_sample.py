from nacl import pwhash, secret, utils


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

Alices_key = kdf(secret.SecretBox.KEY_SIZE, password, salt, opslimit=ops, memlimit=mem)
Alices_box = secret.SecretBox(Alices_key)
nonce = utils.random(secret.SecretBox.NONCE_SIZE)

encrypted = Alices_box.encrypt(message, nonce)

# now Alice must send to Bob both the encrypted message
# and the KDF parameters: salt, opslimit and memlimit;
# using the same kdf mechanism, parameters **and password**
# Bob is able to derive the correct key to decrypt the message


Bobs_key = kdf(secret.SecretBox.KEY_SIZE, password, salt, opslimit=ops, memlimit=mem)
Bobs_box = secret.SecretBox(Bobs_key)
received = Bobs_box.decrypt(encrypted)
print(received.decode("utf-8"))

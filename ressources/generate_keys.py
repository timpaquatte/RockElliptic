import ecdsa

# SECP256k1 is the Bitcoin elliptic curve
sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
vk = sk.get_verifying_key()

file = open("signkey.pem", "wb")
file.write(sk.to_pem())
file.close()

file = open("verifkey.pem", "wb")
file.write(vk.to_pem())
file.close()
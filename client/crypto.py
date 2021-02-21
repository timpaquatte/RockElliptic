from os import path
import ecdsa
import Crypto
from Crypto.PublicKey import RSA

from .instructions import *
from .misc import log, handleReturnCode
from .specs import TOTAL_SIZE


def getSigningKey():
    relpath = "./ressources/signkey.pem"
    abspath = path.abspath(relpath)
    file = open(abspath, "rb")
    signing_key = ecdsa.SigningKey.from_pem(file.read())
    file.close()
    return signing_key

def getVerifyingKey():
    relpath = "./ressources/verifkey.pem"
    abspath = path.abspath(relpath)
    file = open(abspath, "rb")
    verif_key = ecdsa.VerifyingKey.from_pem(file.read())
    file.close()
    return verif_key


def cryptoChallenge(connection, pubkey):
    ## Ask for the challenge
    Lc = 0
    challenge, sw1, sw2 = connection.transmit([CLA,INS_START_CHALLENGE,P1,P2,Lc])

    ## Encrypt
    pubkey = RSA.construct(pubkey)
    encrypted = pubkey.encrypt(int.from_bytes(challenge, "big"), 0)[0]
    encrypted = list(encrypted.to_bytes(64, "big"))

    ## Send the answer
    Lc = len(encrypted)
    success, sw1, sw2 = connection.transmit([CLA,INS_VERIF_CHALLENGE,P1,P2,Lc]+encrypted)

    return success[0]

def verifySig(connection):
    vk = getVerifyingKey()

    Lc = 0
    data, sw1, sw2 = connection.transmit([CLA,INS_SEND_DATA,P1,P2,Lc])
    info = bytearray(data[:TOTAL_SIZE])
    sig = bytearray(data[TOTAL_SIZE:])
    try:
        vk.verify(sig, info)
        return info
    except Exception:
        log("Unvalid signature", error=True)
        return -1

def sendPINCode(connection, PIN):
    Lc = 4
    success, sw1, sw2 = connection.transmit([CLA,INS_CHECK_PIN,P1,P2,Lc]+PIN)
    if not handleReturnCode(success[0], "Right PIN", "Wrong PIN"):
        return -1

def receivePubKey(connection):
    Lc=0
    pubkey, sw1, sw2 = connection.transmit([CLA,INS_SEND_PUBKEY,P1,P2,Lc])
    return bytearray(pubkey)
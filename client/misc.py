from colorama import Fore
from .specs import *
from .instructions import CODE_ERROR, CODE_OK

def log(message, *args, error=False):
    s = str(message)
    for x in args:
        s += " " + str(x)
    if error:
        print(Fore.RED + "[ERROR]", s, Fore.RESET)
    else:
        print("[+]", s)

def checkParams(id_user, first_name, name, balance):
    if len(first_name) > SIZE_NAME:
        log("First name too long (%d max)" % SIZE_NAME)
        return -1
    if len(first_name) == 0:
        log("You need to enter a first name")
        return -1
    if len(name) > SIZE_NAME:
        log("Name too long (%d max)" % SIZE_NAME)
        return -1
    if len(name) == 0:
        log("You need to enter a name")
        return -1
    if id_user > (2**(SIZE_ID*8)):
        log("ID too big (%d max)" % (2**(SIZE_ID*8)))
        return -1
    if balance > (2**(SIZE_BALANCE*8)):
        log("Balance too big (%d max)" % (2**(SIZE_BALANCE*8)))
        return -1
    return 0

def parsePubKey(pubkey):
    expLength = int.from_bytes(pubkey[:2], "big")
    exp = int.from_bytes(pubkey[2:2 + expLength], "big")

    offset = 2 + expLength
    modLength = int.from_bytes(pubkey[offset:offset+2], "big")
    mod = int.from_bytes(pubkey[offset + 2:offset + 2 + modLength], "big")

    pin = list(pubkey[offset + 2 + modLength:])

    return (mod, exp), pin

def handleReturnCode(return_code, msg_success, msg_error):
    if return_code == CODE_OK:
        log(msg_success)
        return True
    else:
        log(msg_error, error=True)
        return False
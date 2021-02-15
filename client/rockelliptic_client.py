#gp -v --install HelloIO.cap --params 4a6176614361726479

from smartcard.System import readers

from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from tkinter.messagebox import *

import ecdsa
from os import path
import Crypto
from Crypto.PublicKey import RSA
from colorama import Fore
import string

from .instructions import *
from .specs import *
from .sql import getSQLConn

FONT = "Sawasdee"
canvas = None
txt = None

def log(message, *args, error=False):
    s = str(message)
    for x in args:
        s += " " + str(x)
    if error:
        print(Fore.RED + "[ERROR]", s, Fore.RESET)
    else:
        print("[+]", s)

def connectReader():
    # Connect to the reader
    r=readers()
    connection=r[0].createConnection()
    try:
        connection.connect()
    except:
        return None

    # Send the apdu
    data, sw1, sw2 = connection.transmit(apdu)
    return connection

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


def createAccount(id_user, first_name, name, balance):
    if checkParams(id_user, first_name, name, balance) == -1:
        return

    connection = connectReader()

    # Form the data
    info = id_user.to_bytes(SIZE_ID, ENDIANNESS)
    info += first_name.encode() + b"\x00"*(SIZE_NAME - len(first_name))
    info += name.encode() + b"\x00"*(SIZE_NAME - len(name))
    info += balance.to_bytes(SIZE_BALANCE, ENDIANNESS)

    # Sign it
    sk = getSigningKey()
    sig = sk.sign(info)
    info = list(info + sig)

    # Send it
    Lc = len(info)
    data, sw1, sw2 = connection.transmit([CLA,INS_RECEIVE_DATA,P1,P2,Lc]+info)

    # Receive public key
    Lc=0
    pubkey, sw1, sw2 = connection.transmit([CLA,INS_SEND_PUBKEY,P1,P2,Lc])
    pubkey = bytearray(pubkey)

    ## SQL part
    conn = getSQLConn()
    req = "INSERT INTO CLIENT (id, first_name, name, balance, pubkey) values (?, ?, ?, ?, ?)"
    data = (id_user, first_name, name, balance, pubkey)
    with conn:
        conn.execute(req, data)

    pubkey, PIN = parsePubKey(pubkey)
    log("Pin created:", PIN)

    #Disconnect the reader
    connection.disconnect()

def getPinCode():
    newWindow = Toplevel()
    newWindow.title("Code PIN")

    def limitSize(*args):
        value = PIN.get()
        if len(value) > 2: PIN.set(value[:4])
        elif value[-1] not in string.digits:
            PIN.set(value[:-1])

    def end(*args):
        newWindow.quit()
        newWindow.destroy()

    PIN = StringVar()
    PIN.trace('w', limitSize)
    ttk.Label(newWindow, text="Entrez le code PIN").pack(padx=5, pady=5)
    entry = ttk.Entry(newWindow, textvariable=PIN, show="*")
    entry.pack(padx=5, pady=5)
    ttk.Button(newWindow, text="OK", command=end).pack(padx=5, pady=5)

    entry.focus_set()
    newWindow.bind("<Return>", end)
    newWindow.mainloop()

    return [int(x) for x in PIN.get()]


def transaction(amount):
    connection = connectReader()

    vk = getVerifyingKey()

    log("=== VERIF SIGNATURE ===")
    Lc = 0
    data, sw1, sw2 = connection.transmit([CLA,INS_SEND_DATA,P1,P2,Lc])
    info = bytearray(data[:TOTAL_SIZE])
    sig = bytearray(data[TOTAL_SIZE:])
    if not vk.verify(sig, info):
        log("Unvalid signature", error=True)
    else:
        log("Nice signature")

    ## Get the ID and the public key of the user
    id_user = int.from_bytes(info[:SIZE_ID], byteorder=ENDIANNESS)
    conn = getSQLConn()
    with conn:
        c = conn.execute("SELECT pubkey, balance, first_name, name  FROM CLIENT WHERE id=?", (id_user,))
        pubkey, balance, first_name, name = c.fetchone()
    pubkey, pin_created = parsePubKey(pubkey)
    log("ID:", id_user)
    log("First name:", first_name)
    log("Name:", name)
    log("Balance:", balance)
    log("Public key:", pubkey)
    log("PIN created:", pin_created)

    ## Check that the balance is sufficient
    if balance - amount > 0:
        log("Balance is sufficient")
    else:
        log("Balance not sufficient (%d - %d)" % (balance, amount), error=True)
        return

    ## Ask for the challenge
    log("=== Challenge ===")
    Lc = 0
    challenge, sw1, sw2 = connection.transmit([CLA,INS_START_CHALLENGE,P1,P2,Lc])
    log("Plaintext:", challenge)

    ## Encrypt
    pubkey = RSA.construct(pubkey)
    encrypted = pubkey.encrypt(int.from_bytes(challenge, "big"), 0)[0]
    encrypted = list(encrypted.to_bytes(64, "big"))
    log("Encrypted:",  encrypted, len(encrypted))

    ## Send the answer
    Lc = len(encrypted)
    success, sw1, sw2 = connection.transmit([CLA,INS_VERIF_CHALLENGE,P1,P2,Lc]+encrypted)
    success = success[0]

    if success == 0:
        log("Challenge succeeded")
    else:
        log("Fail in challenge", error=True)


    ## Send the PIN code
    PIN = getPinCode()
    log("PIN:", PIN)
    Lc = 4
    success, sw1, sw2 = connection.transmit([CLA,INS_CHECK_PIN,P1,P2,Lc]+PIN)
    success = success[0]

    if success == 0:
        log("Right PIN")
    else:
        log("Wrong PIN", error=True)

    ## Write the new information
    # Form the data
    balance -= amount
    info = id_user.to_bytes(SIZE_ID, ENDIANNESS)
    info += first_name.encode() + b"\x00"*(SIZE_NAME - len(first_name))
    info += name.encode() + b"\x00"*(SIZE_NAME - len(name))
    info += balance.to_bytes(SIZE_BALANCE, ENDIANNESS)

    # Sign it
    sk = getSigningKey()
    sig = sk.sign(info)
    info = list(info + sig)

    # Send it
    Lc = len(info)
    data, sw1, sw2 = connection.transmit([CLA,INS_RECEIVE_DATA,P1,P2,Lc]+info)

    ## SQL part
    conn = getSQLConn()
    req = "UPDATE CLIENT SET balance = ? WHERE id=?"
    data = (balance, id_user)
    with conn:
        conn.execute(req, data)

    connection.disconnect()

def seeBalance():
    global canvas, txt

    connection = connectReader()

    if connection != None:
        Lc = 0
        data, sw1, sw2 = connection.transmit([CLA,INS_SEND_DATA,P1,P2,Lc])
        info = bytearray(data[:TOTAL_SIZE])
        balance = int.from_bytes(info[-SIZE_BALANCE:], ENDIANNESS)

        canvas.delete(txt)
        txt = canvas.create_text(400, 150, text="%d €"%balance, font=(FONT, 70))
    else:
        canvas.delete(txt)
        txt = canvas.create_text(400, 150, text="Carte non détectée", font=(FONT, 50))

def main():
    global canvas, txt

    ## Initialization
    root = Tk()
    root.geometry("800x600")

    root.title("RockElliptic v1.0")
    mainframe = ttk.Frame(root).pack()

    ## Canvas
    canvas = Canvas(mainframe, width=800, height=300, bg="ivory")
    txt = canvas.create_text(400, 150, text="", font=(FONT, 70))
    canvas.pack(padx=5, pady=5)

    ## See balance
    btn = ttk.Button(mainframe, text="Voir solde", command=seeBalance)
    btn.pack(side=RIGHT, padx=5, pady=5, fill=Y)

    ## Create account
    account_frame = LabelFrame(root, text="Créer un compte", padx=5, pady=5)
    account_frame.pack(fill="both", padx=5, pady=5)

    name = StringVar()
    balance = IntVar()
    first_name = StringVar()
    id_user = IntVar()
    ttk.Label(account_frame, text="Prénom").grid(row=0, column=0)
    ttk.Entry(account_frame, textvariable=first_name).grid(row=0, column=1)
    ttk.Label(account_frame, text="Nom").grid(row=1, column=0)
    ttk.Entry(account_frame, textvariable=name).grid(row=1, column=1)
    ttk.Label(account_frame, text="Débit").grid(row=2, column=0)
    ttk.Entry(account_frame, textvariable=balance).grid(row=2, column=1)
    ttk.Label(account_frame, text="€").grid(row=2, column=2)
    ttk.Label(account_frame, text="Numéro de participant").grid(row=3, column=0)
    ttk.Entry(account_frame, textvariable=id_user).grid(row=3, column=1)

    callback = lambda: createAccount(id_user.get(), first_name.get(), name.get(), balance.get())
    btn = ttk.Button(account_frame, width=38, text="Créer", command=callback)
    btn.grid(columnspan=2, rowspan=2, row=1, column=3, padx=30)

    ## Refill card
    refill_frame = LabelFrame(root, text="Recharger sa carte", padx=5, pady=5)
    refill_frame.pack(fill="both", padx=5, pady=5, expand=True)

    amount_refill = IntVar()
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_refill).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Recharger",
        command=lambda: transaction(-amount_refill.get()))
    btn.pack(side=LEFT, padx=10, pady=5)

    ## Pay
    refill_frame = LabelFrame(root, text="Payer", padx=5, pady=5)
    refill_frame.pack(fill="both", padx=5, pady=5, expand=True)

    amount_pay = IntVar()
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_pay).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Payer",
        command=lambda: transaction(amount_pay.get()))

    btn.pack(side=LEFT, padx=10, pady=5)

    root.mainloop()
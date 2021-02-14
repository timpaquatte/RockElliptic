#gp -v --install HelloIO.cap --params 4a6176614361726479

from smartcard.System import readers
from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
import ecdsa
from os import path

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
        print("[ERROR]", s)
    else:
        print(s)

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
        log("ID too big (%d max)" % (2**SIZE_ID))
        return -1
    if balance > (2**(SIZE_BALANCE*8)):
        log("Balance too big (%d max)" % (2**SIZE_BALANCE))
        return -1
    return 0

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
    log(info)
    log("Size data sent:", Lc)
    data, sw1, sw2 = connection.transmit([CLA,INS_RECEIVE_DATA,P1,P2,Lc]+info)
    log(hex(sw1), hex(sw2), data)

    # Receive public key
    pubkey = None

    ## SQL part
    conn = getSQLConn()
    req = "INSERT INTO CLIENT (id, first_name, name, balance, pubkey) values (?, ?, ?, ?, ?)"
    data = (id_user, first_name, name, balance, pubkey)
    with conn:
        conn.execute(req, data)

    #Disconnect the reader
    connection.disconnect()

def refill(*args):
    pass

def pay(*args):
    connection = connectReader()

    vk = getVerifyingKey()

    print("=== PAIEMENT ===")
    Lc = 0
    data, sw1, sw2 = connection.transmit([CLA,INS_SEND_DATA,P1,P2,Lc])
    print("Received:")
    print(hex(sw1),hex(sw2), data)
    info = bytearray(data[:TOTAL_SIZE])
    sig = bytearray(data[TOTAL_SIZE:])

    print("Verif signature:", vk.verify(sig, info))

    pass

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

    amount_refill = StringVar()
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_refill).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Recharger", command=refill)
    btn.pack(side=LEFT, padx=10, pady=5)

    ## Pay
    refill_frame = LabelFrame(root, text="Payer", padx=5, pady=5)
    refill_frame.pack(fill="both", padx=5, pady=5, expand=True)

    amount_pay = StringVar()
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_pay).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Recharger", command=pay)
    btn.pack(side=LEFT, padx=10, pady=5)

    root.mainloop()
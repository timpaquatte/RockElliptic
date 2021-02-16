#gp -v --install HelloIO.cap --params 4a6176614361726479

from smartcard.System import readers

from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from tkinter.messagebox import *

import string

from .instructions import *
from .specs import *
from .sql import *
from .crypto import *
from .misc import *

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

def sendData(connection, id_user, first_name, name, balance):
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

    return handleReturnCode(data[0], "Data sent on the card", "Problem during sending")

def createAccount(id_user, first_name, name, balance):
    if checkParams(id_user, first_name, name, balance) == -1:
        return

    connection = connectReader()

    if not sendData(connection, id_user, first_name, name, balance):
        return

    pubkey = receivePubKey(connection)

    insertInDatabase(id_user, first_name, name, balance, pubkey)

    pubkey, PIN = parsePubKey(pubkey)
    log("Pin created:", PIN)

    #Disconnect the reader
    connection.disconnect()

def transaction(amount):
    connection = connectReader()

    info = verifySig(connection)
    if info == -1:
        return

    ## Get the ID and the public key of the user
    id_user = int.from_bytes(info[:SIZE_ID], byteorder=ENDIANNESS)
    first_name, name, balance, pubkey, PIN = getEntrySQL(id_user)
    log("=== Content of the card ===")
    log("ID:", id_user)
    log("First name:", first_name)
    log("Name:", name)
    log("Balance:", balance)
    # log("Public key:", pubkey)
    # log("PIN:", PIN)
    log("===========================")

    if (balance - amount) < 0:
        log("Balance not sufficient (%d - %d)" % (balance, amount), error=True)
        return

    return_code = cryptoChallenge(connection, pubkey)
    if not handleReturnCode(return_code, "Challenge succeeded", "Fail in challenge"):
        return

    PIN_entered = enterPinCode()
    if sendPINCode(connection, PIN_entered) == -1:
        return

    balance -= amount
    if not sendData(connection, id_user, first_name, name, balance):
        return

    updateEntry(id_user, balance)
    updateBalanceDisplay(balance)

    connection.disconnect()

##############################
## Graphical User Interface ##
##############################

FONT = "Sawasdee"
canvas = None
txt = None


def updateBalanceDisplay(balance):
    global canvas, txt
    canvas.delete(txt)
    txt = canvas.create_text(400, 150, text="%d €"%balance, font=(FONT, 70))

def seeBalance():
    global canvas, txt

    connection = connectReader()

    if connection != None:
        Lc = 0
        data, sw1, sw2 = connection.transmit([CLA,INS_SEND_DATA,P1,P2,Lc])
        info = bytearray(data[:TOTAL_SIZE])
        balance = int.from_bytes(info[-SIZE_BALANCE:], ENDIANNESS)

        updateBalanceDisplay(balance)
    else:
        canvas.delete(txt)
        txt = canvas.create_text(400, 150, text="Carte non détectée", font=(FONT, 50))

def enterPinCode():
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
    balance = StringVar()
    first_name = StringVar()
    id_user = StringVar()
    balance.set("0")
    id_user.set("0")
    ttk.Label(account_frame, text="Prénom").grid(row=0, column=0)
    ttk.Entry(account_frame, textvariable=first_name).grid(row=0, column=1)
    ttk.Label(account_frame, text="Nom").grid(row=1, column=0)
    ttk.Entry(account_frame, textvariable=name).grid(row=1, column=1)
    ttk.Label(account_frame, text="Débit").grid(row=2, column=0)
    ttk.Entry(account_frame, textvariable=balance).grid(row=2, column=1)
    ttk.Label(account_frame, text="€").grid(row=2, column=2)
    ttk.Label(account_frame, text="Numéro de participant").grid(row=3, column=0)
    ttk.Entry(account_frame, textvariable=id_user).grid(row=3, column=1)

    callback = lambda: createAccount(int(id_user.get()), first_name.get(), name.get(), int(balance.get()))
    btn = ttk.Button(account_frame, width=38, text="Créer", command=callback)
    btn.grid(columnspan=2, rowspan=2, row=1, column=3, padx=30)

    ## Refill card
    refill_frame = LabelFrame(root, text="Recharger sa carte", padx=5, pady=5)
    refill_frame.pack(fill="both", padx=5, pady=5, expand=True)

    amount_refill = StringVar()
    amount_refill.set("0")
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_refill).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Recharger",
        command=lambda: transaction(-int(amount_refill.get())))
    btn.pack(side=LEFT, padx=10, pady=5)

    ## Pay
    refill_frame = LabelFrame(root, text="Payer", padx=5, pady=5)
    refill_frame.pack(fill="both", padx=5, pady=5, expand=True)

    amount_pay = StringVar()
    amount_pay.set("0")
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_pay).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Payer",
        command=lambda: transaction(int(amount_pay.get())))

    btn.pack(side=LEFT, padx=10, pady=5)


    ## Limit the input to ASCII characters
    def limitToAscii(var):
        value = var.get()
        if len(value) > 20: var.set(value[:20])
        elif len(value) > 0 and value[-1] not in string.ascii_letters:
            var.set(value[:-1])
    name.trace('w', lambda x,y,z: limitToAscii(name))
    first_name.trace('w', lambda x,y,z: limitToAscii(first_name))

    ## Limit the numeric inputs to digits
    def limitToDigits(var):
        value = var.get()
        if len(value) > 0 and value[-1] not in string.digits:
            var.set(value[:-1])
    balance.trace('w', lambda x,y,z: limitToDigits(balance))
    id_user.trace('w', lambda x,y,z: limitToDigits(id_user))
    amount_pay.trace('w', lambda x,y,z: limitToDigits(amount_pay))
    amount_refill.trace('w', lambda x,y,z: limitToDigits(amount_refill))

    root.mainloop()
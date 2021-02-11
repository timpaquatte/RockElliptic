#gp -v --install HelloIO.cap --params 4a6176614361726479

from smartcard.System import readers
from tkinter import *
from tkinter import ttk
from .instructions import *
from .specs import *
import ecdsa


def createAccount(id_user, first_name, name, amount):

    # Connect to the reader
    r=readers()
    connection=r[0].createConnection()
    connection.connect()

    # Send the apdu
    data, sw1, sw2 = connection.transmit(apdu)

    # Send the data
    info = id_user.to_bytes(SIZE_ID, ENDIANNESS)
    info += first_name.encode() + b"\x00"*(SIZE_NAME - len(first_name))
    info += name.encode() + b"\x00"*(SIZE_NAME - len(name))
    info += amount.to_bytes(SIZE_AMOUNT, ENDIANNESS)

    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    sig = sk.sign(info)
    info = list(info + sig)

    Lc = len(info)
    print(info)
    print("Size data sent:", Lc)
    data, sw1, sw2 = connection.transmit([CLA,INS_RECEIVE_DATA,P1,P2,Lc]+info)
    print(hex(sw1),hex(sw2), data)

    # Receive
    print("Receive")
    Lc = 0
    data, sw1, sw2 = connection.transmit([CLA,INS_SEND_DATA,P1,P2,Lc])
    print(hex(sw1),hex(sw2), data)

    #Disconnect the reader
    connection.disconnect()

def refill(*args):
    pass

def pay(*args):
    # Ask the user ID to the card
    # Make sure this ID has enough money
    # Ask for PIN code to the user
    # If it matches, challenge to the card to make sure it's the right one (crypto challenge)
    # Withdraw the amount of the transaction from the account
    pass

def main():

    ## Initialization
    root = Tk()
    root.geometry("800x600")

    root.title("RockElliptic v1.0")
    mainframe = ttk.Frame(root).pack()

    ## Canvas
    canvas = Canvas(mainframe, width=800, height=300, bg="ivory").pack(padx=5, pady=5)
    ttk.Label(canvas, text="Welcome to RockElliptic !!").pack(side=TOP)

    ## Create account
    account_frame = LabelFrame(root, text="Créer un compte", padx=5, pady=5)
    account_frame.pack(fill="both", padx=5, pady=5)

    name = StringVar()
    debit = StringVar()
    first_name = StringVar()
    id_num = StringVar()
    ttk.Label(account_frame, text="Nom").grid(row=0, column=0)
    ttk.Entry(account_frame, textvariable=name).grid(row=0, column=1)
    ttk.Label(account_frame, text="Prénom").grid(row=1, column=0)
    ttk.Entry(account_frame, textvariable=first_name).grid(row=1, column=1)
    ttk.Label(account_frame, text="Débit").grid(row=2, column=0)
    ttk.Entry(account_frame, textvariable=debit).grid(row=2, column=1)
    ttk.Label(account_frame, text="€").grid(row=2, column=2)
    ttk.Label(account_frame, text="Numéro de participant").grid(row=3, column=0)
    ttk.Entry(account_frame, textvariable=id_num).grid(row=3, column=1)

    btn = ttk.Button(account_frame, width=50, text="Créer", command=createAccount)
    btn.grid(columnspan=2, rowspan=2, row=1, column=3, padx=30)

    ## Refill card
    refill_frame = LabelFrame(root, text="Recharger sa carte", padx=5, pady=5)
    refill_frame.pack(fill="both", padx=5, pady=5)

    amount_refill = StringVar()
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_refill).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Recharger", command=refill)
    btn.pack(side=LEFT, padx=10)

    ## Pay
    refill_frame = LabelFrame(root, text="Payer", padx=5, pady=5)
    refill_frame.pack(fill="both", padx=5, pady=5)

    amount_pay = StringVar()
    ttk.Label(refill_frame, text="Montant").pack(side=LEFT, padx=10)
    ttk.Entry(refill_frame, textvariable=amount_pay).pack(side=LEFT, padx=10)
    ttk.Label(refill_frame, text="€").pack(side=LEFT, padx=10)

    btn = ttk.Button(refill_frame, width=50, text="Recharger", command=pay)
    btn.pack(side=LEFT, padx=10)

    root.mainloop()
    pass
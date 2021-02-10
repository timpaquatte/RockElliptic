#gp -v --install HelloIO.cap --params 4a6176614361726479

from smartcard.System import readers
from tkinter import *
from tkinter import ttk

def createAccount(root):
    root.geometry("800x800")

def refill(*args):
    pass

def pay(*args):
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


if __name__=="__main__":
    main()

""" r=readers()
connection=r[0].createConnection()
connection.connect()
SELECT = [0x00,0xA4,0x04,0x00,0x08]

#Selection AID
AID = [0x01,0x02,0x03,0x04,0x05,0x09,0x32,0x70]
apdu = SELECT + AID
data, sw1, sw2 = connection.transmit(apdu)

#affichage message
CLA = 0xA0
INS1 = 0x00
INS2 = 0x01
INS3 = 0x02
P1,P2 = 0x00, 0x00
Le = 0x00 # set to 0 means the client does not know the size of received data 


#Printing debug message
data, sw1, sw2 = connection.transmit([CLA,INS3,P1,P2,Le])
print(hex(sw1),hex(sw2), data)

#Sending Master Name
PIN = [2, 7, 0, 0]
Lc = len(PIN)
print(Lc)
data, sw1, sw2 = connection.transmit([CLA,INS1,P1,P2,Lc]+PIN)
print(hex(sw1),hex(sw2), data)

#Printing message
data, sw1, sw2 = connection.transmit([CLA,INS2,P1,P2,Le])
print(hex(sw1),hex(sw2), data)

mess1 = ''
for e in data:
    mess1 += chr(e)

print(mess1)


#Disconnect the reader
connection.disconnect() """

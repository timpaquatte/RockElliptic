import time
from smartcard.System import readers

r=readers()
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

PIN = [0, 0, 0, 0]
Lc = len(PIN)
for i in range(10):
    PIN[0] = i
    total = 0
    t = time.perf_counter()
    for n in range(100):
        #Sending PIN
        data, sw1, sw2 = connection.transmit([CLA,INS1,P1,P2,Lc]+PIN)
        #Asking secret
        data, sw1, sw2 = connection.transmit([CLA,INS2,P1,P2,Le])

    total_time = (time.perf_counter() - t) / 100
    print(i, ":", total_time, "s")

#Disconnect the reader
connection.disconnect()

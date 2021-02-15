SELECT = [0x00,0xA4,0x04,0x00,0x08]

## Selection AID
AID = [0x01,0x02,0x03,0x04,0x05,0x09,0x32,0x70]
apdu = SELECT + AID

## Affichage message
CLA = 0xA0
P1,P2 = 0x00, 0x00
Le = 0x00 # set to 0 means the client does not know the size of received data

## Instructions
INS_RECEIVE_DATA = 0x01
INS_SEND_DATA = 0x02
INS_SEND_PUBKEY = 0x03
INS_START_CHALLENGE = 0x04
INS_VERIF_CHALLENGE = 0x05
INS_CHECK_PIN = 0x06
DEBUG = 0x00
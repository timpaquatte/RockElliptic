# RockElliptic
A Public Key Infrastructure for JavaCard with a Python client

## Installation

```
git clone https://github.com/timpaquatte/RockElliptic.git
cd RockElliptic
```

The graphical library *Tkinter* is usually installed by default, you can check with the following command:
```
python -m tkinter
```
If it's not the case, please refer to the *Tkinter* documentation.

Then you have to install the additional python libraries (essentially *colorama*, *ecdsa* and *pycrypto*):
```
python -m requirements.txt
```
Modify the file "configure.py" to specify the path to the JavaCard directory and to the gp.jar file then run:
```
python configure.py
```
Generate the ECDSA keys
```
make create_keys
```

Plug in the card reader, insert a card then run:
```
make install_card
```
to install the software on the JavaCard.

## Use

If the installation worked, the client can be run:
```
python -m client
```

The GUI should be displayed and the software is then ready to use. Its functioning is very intuitive. The terminal where the client was run will display some information during the execution. 

In the case of an organization with several machines that sould accept the cards created by the other ones, you have to:
* __Share the private and public keys with all instances__, you can find them in the ressources directory (privey.pem et pubkey.pem). Both of these files are created with `make create_keys` and have to be shared on all computers at the installation.
* __Share the database__ (file ressources/client\_data.db) in order to access the public keys of all users. At the opposite of the signature keys, it's not enough to share the database at the installation. As users can be added to the database at any moment, the database has to be common and up-to-date.

### Create a user account
This button initializes the card with the personal information of a client: name, first name, participant number and initial balance. Once an account has been created, the card cannot be overwritten without being reset. At this moment a PIN code is given to the user, who has to remember it to be able to use his card.

### See balance
This button prints the balance of the inserted card on the clear canvas.

### Refill and pay
These buttons correspond to the same transaction operation, in opposite directions: *Refill* adds money on the card and *Pay* withdraws the amount from the balance. Cryptographic operations are conduced to avoid any fraud and the PIN code is asked to the consumer.

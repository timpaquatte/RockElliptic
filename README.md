# RockElliptic
A Public Key Infrastructure for JavaCard with a Python client


## Installation

```
git clone https://github.com/timpaquatte/RockElliptic.git
cd RockElliptic
```

### Install the libraries

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
to install the software on the JavaCard

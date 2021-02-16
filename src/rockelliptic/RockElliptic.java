package rockelliptic;

import java.security.GeneralSecurityException;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.JCSystem;
import javacard.framework.OwnerPIN;
import javacard.security.KeyBuilder;
import javacard.security.KeyPair;
import javacard.security.RSAPrivateCrtKey;
import javacard.security.RSAPublicKey;

import javacard.security.RandomData;
import javacardx.crypto.Cipher;

public class RockElliptic extends Applet {
    public static final byte CLA_MONAPPLET = (byte) 0xA0;

	// Instructions
    public static final byte INS_RECEIVE_DATA = 0x01;
    public static final byte INS_SEND_DATA = 0x02;
    public static final byte INS_SEND_PUBKEY = 0x03;
    public static final byte INS_START_CHALLENGE = 0x04;
    public static final byte INS_VERIF_CHALLENGE = 0x05;
    public static final byte INS_CHECK_PIN = 0x06;
    public static final byte DEBUG = 0x00;

    public static final byte STATE_EMPTY = 0x00;
    public static final byte STATE_PUBKEY = 0x01;
    public static final byte STATE_WAITCHALL = 0x02;
    public static final byte STATE_VERIFCHALL = 0x03;
    public static final byte STATE_WAITPIN = 0x04;
    public static final byte STATE_CHANGEDATA = 0x05;
    public static byte state;


	private static final short SIZE_INFO = 128;
	private static final short SIZE_CHALLENGE = 64;
	private static byte[] SIGNED_INFORMATION = new byte[SIZE_INFO];
	private static byte[] CHALLENGE = new byte[SIZE_CHALLENGE];

    private static byte[] MY_DEBUG;
	private static final short keyLength = 113;

	private static RSAPrivateCrtKey privateKey;
    private static RSAPublicKey publicKey;
    private static KeyPair keyPair;
	private static OwnerPIN pin;

    /* Constructor */
    private RockElliptic() {
		RockElliptic.keyPair = new KeyPair(KeyPair.ALG_RSA_CRT, KeyBuilder.LENGTH_RSA_512);
		RockElliptic.state = STATE_EMPTY;
		RockElliptic.pin = new OwnerPIN((byte) 100, (byte) 4);
		register();
    }

    private static void debug(byte[] bArray, short bOffset, byte bLength) throws ISOException {
		byte aidLength = bArray[bOffset];
		byte controlLength = bArray[(short)(bOffset+1+aidLength)];
		byte dataLength = bArray[(short)(bOffset+1+aidLength+1+controlLength)];
		short dataOffset = (short)(bOffset+1+aidLength+1+controlLength+1);

		//Puts in MY_DEBUG all the line passed to installer
		MY_DEBUG = new byte[(short)(dataOffset + dataLength)];
		Util.arrayCopy(bArray, (short) 0, MY_DEBUG, (short)0, (short)(dataOffset + dataLength));
    }


    public static void install(byte bArray[], short bOffset, byte bLength) throws ISOException {
		debug(bArray, bOffset, bLength);
		new RockElliptic();
    }

	private final short serializeKey(RSAPublicKey key, byte[] buffer, short offset) {
		short expLen = key.getExponent(buffer, (short) (offset + 2));
		Util.setShort(buffer, offset, expLen);
		short modLen = key.getModulus(buffer, (short) (offset + 4 + expLen));
		Util.setShort(buffer, (short) (offset + 2 + expLen), modLen);
		return (short) (4 + expLen + modLen);
	}

    public void process(APDU apdu) throws ISOException {
		byte[] buffer = apdu.getBuffer();

		if (this.selectingApplet()) return;

		if (buffer[ISO7816.OFFSET_CLA] != CLA_MONAPPLET) {
				ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
		}

		switch (buffer[ISO7816.OFFSET_INS]) {

			case INS_RECEIVE_DATA:
				if((state == STATE_EMPTY) || (state == STATE_CHANGEDATA))
				{
					apdu.setIncomingAndReceive();

					Util.arrayCopyNonAtomic(buffer,
						ISO7816.OFFSET_CDATA,
						SIGNED_INFORMATION,
						(short)0,
						(short) SIGNED_INFORMATION.length);

					if(state == STATE_EMPTY)
						state = STATE_PUBKEY;
					else
						state = STATE_WAITCHALL;
					buffer[0] = 0;
					apdu.setOutgoingAndSend((short) 0, (short) 1);
				}
				else {
					buffer[0] = -1;
					apdu.setOutgoingAndSend((short) 0, (short) 1);
					state = STATE_WAITCHALL;
				}

				break;

			case INS_SEND_DATA:
				Util.arrayCopyNonAtomic(SIGNED_INFORMATION,
					(short)0,
					buffer,
					(short)0,
					(short)SIGNED_INFORMATION.length);

				apdu.setOutgoingAndSend((short) 0, SIZE_INFO);
				break;

			case INS_SEND_PUBKEY:
				if(state == STATE_PUBKEY) {
					keyPair.genKeyPair();

					// Crypto keys
					privateKey = (RSAPrivateCrtKey) keyPair.getPrivate();
					publicKey = (RSAPublicKey) keyPair.getPublic();
					short totalLength = serializeKey(publicKey, buffer, (short) 0);

					// PIN code
					RandomData randInstance = RandomData.getInstance(RandomData.ALG_PSEUDO_RANDOM);
					byte[] pinCode = new byte[4];
					randInstance.generateData(pinCode, (short) 0, (short) 4);
					byte i = 0;
					for(i = 0; i < 4; i++) {
						pinCode[i] %=  10;
						if(pinCode[i] < 0)
							pinCode[i] += 10;
					}
					pin.update(pinCode, (short) 0, (byte) 4);
					Util.arrayCopyNonAtomic(pinCode,
						(short) 0,
						buffer,
						totalLength,
						(short) 4);


					apdu.setOutgoingAndSend((short) 0, (short) (totalLength + 4));

					state = STATE_WAITCHALL;
				}
				else {
					buffer[0] = -1;
					apdu.setOutgoingAndSend((short) 0, (short) 1);
					state = STATE_WAITCHALL;
				}

				break;

			case INS_START_CHALLENGE:
				if(state == STATE_WAITCHALL) {
					RandomData randInstance = RandomData.getInstance(RandomData.ALG_SECURE_RANDOM);
					randInstance.generateData(CHALLENGE, (short) 1, (short) (SIZE_CHALLENGE-1));
					Util.arrayCopyNonAtomic(CHALLENGE,
						(short)0,
						buffer,
						(short)0,
						SIZE_CHALLENGE);

					apdu.setOutgoingAndSend((short) 0, SIZE_CHALLENGE);

					state = STATE_VERIFCHALL;
				}
				else {
					buffer[0] = -1;
					apdu.setOutgoingAndSend((short) 0, (short) 1);
					state = STATE_WAITCHALL;
				}
				break;

			case INS_VERIF_CHALLENGE:
				if(state == STATE_VERIFCHALL) {
					byte[] toCompare = new byte[SIZE_CHALLENGE];
					apdu.setIncomingAndReceive();

					Cipher cipherInstance = Cipher.getInstance(Cipher.ALG_RSA_NOPAD, false);
					cipherInstance.init(publicKey, Cipher.MODE_ENCRYPT);
					cipherInstance.doFinal(CHALLENGE, (short) 0, SIZE_CHALLENGE, toCompare, (short) 0);

					byte comp = Util.arrayCompare(toCompare, (short) 0, buffer, ISO7816.OFFSET_CDATA, SIZE_CHALLENGE);
					buffer[0] = comp;
					apdu.setOutgoingAndSend((short) 0, (short) (1));

					state = STATE_WAITPIN;
				}
				else {
					buffer[0] = -1;
					apdu.setOutgoingAndSend((short) 0, (short) 1);
					state = STATE_WAITCHALL;
				}
				break;

			case INS_CHECK_PIN:
				if(state == STATE_WAITPIN) {
					apdu.setIncomingAndReceive();

					if(pin.check(buffer, ISO7816.OFFSET_CDATA, (byte) 4)) {
						buffer[0] = 0;
						state = STATE_CHANGEDATA;
					}
					else {
						buffer[0] = -2;
						state = STATE_WAITCHALL;
					}
					apdu.setOutgoingAndSend((short) 0, (short) 1);
				}
				else {
					buffer[0] = -1;
					apdu.setOutgoingAndSend((short) 0, (short) 1);
					state = STATE_WAITCHALL;
				}

				break;

			case DEBUG:
				Util.arrayCopyNonAtomic(MY_DEBUG,
											(short)0,
											buffer,
											(short)0,
											(short)MY_DEBUG.length);
				apdu.setOutgoingAndSend((short) 0, (short)(MY_DEBUG.length));
				break;

			default:
				ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
		}
    }
}

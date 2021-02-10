package rockelliptic;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.JCSystem;

public class RockElliptic extends Applet {
    public static final byte CLA_MONAPPLET = (byte) 0xA0;

    public static final byte INS_INPUT_PIN = 0x00;
    public static final byte INS_OUTPUT_SECRET = 0x01;
	public static final byte DEBUG = 0x02;
	public static boolean RIGHT_PIN = false;

    private final byte[] PIN = {2, 7, 0, 0};
	private final byte[] SECRET = {'Y', 'o', 'u', 'h', 'o', 'u', ' ', '!'};

	private final byte[] ERROR_MESSAGE = {'W', 'r', 'o', 'n', 'g', ' ', 'P', 'I', 'N'};
    private static byte[] MY_DEBUG;

    /* Constructor */
    private RockElliptic() {
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


    public void process(APDU apdu) throws ISOException {
		byte[] buffer = apdu.getBuffer();

		if (this.selectingApplet()) return;

		if (buffer[ISO7816.OFFSET_CLA] != CLA_MONAPPLET) {
				ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
		}

		switch (buffer[ISO7816.OFFSET_INS]) {

			case INS_INPUT_PIN:
				short lc = buffer[ISO7816.OFFSET_LC];

				if(lc == 4) {
					byte pin_sent[] = {0, 0, 0, 0};
					short i = 0;


					apdu.setIncomingAndReceive();
					Util.arrayCopyNonAtomic(buffer,
						ISO7816.OFFSET_CDATA,
						pin_sent,
						(short)0,
						lc);

					if(Util.arrayCompare(pin_sent, (short) 0, PIN, (short) 0, (short)4) == 0) {
						RIGHT_PIN = true;
					}
				}

				break;

			case INS_OUTPUT_SECRET:
				if(RIGHT_PIN) {
					Util.arrayCopyNonAtomic(SECRET,
												(short)0,
												buffer,
												(short)0,
												(short)SECRET.length);

					apdu.setOutgoingAndSend((short) 0, (short)SECRET.length);
				}
				else {
					Util.arrayCopyNonAtomic(ERROR_MESSAGE,
												(short)0,
												buffer,
												(short)0,
												(short)ERROR_MESSAGE.length);

					apdu.setOutgoingAndSend((short) 0, (short)ERROR_MESSAGE.length);
				}
				RIGHT_PIN = false;
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

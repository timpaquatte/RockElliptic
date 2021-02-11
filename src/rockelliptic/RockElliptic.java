package rockelliptic;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.JCSystem;

public class RockElliptic extends Applet {
    public static final byte CLA_MONAPPLET = (byte) 0xA0;

	// Instructions
    public static final byte INS_RECEIVE_DATA = 0x01;
    public static final byte INS_SEND_DATA = 0x02;
    public static final byte INS_CHALLENGE = 0x03;
    public static final byte DEBUG = 0x00;

	private static final short SIZE_INFO = 128;
	private static byte[] SIGNED_INFORMATION = new byte[SIZE_INFO];

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

			case INS_RECEIVE_DATA:
				short lc = buffer[ISO7816.OFFSET_LC];
				apdu.setIncomingAndReceive();

				if(lc == SIZE_INFO) {
				Util.arrayCopyNonAtomic(buffer,
					ISO7816.OFFSET_CDATA,
					SIGNED_INFORMATION,
					(short)0,
					(short) SIGNED_INFORMATION.length);
				}
				break;

			case INS_SEND_DATA:
				Util.arrayCopyNonAtomic(SIGNED_INFORMATION,
					(short)0,
					buffer,
					(short)0,
					(short)SIGNED_INFORMATION.length);

				apdu.setOutgoingAndSend((short) 0, (short)SIGNED_INFORMATION.length);
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

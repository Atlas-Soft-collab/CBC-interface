"""
TCP Server بيستقبل الاتصال من جهاز الـ CBC (Dymind).
الجهاز بيتصل بالـ IP/Port المحددين في config/settings.json
ويبعت البيانات بصيغة HL7 عبر TCP، مؤطرة بـ MLLP framing:

    <VT> ... HL7 message ... <FS><CR>

    VT (Vertical Tab) = 0x0B  -> بداية الرسالة
    FS (File Separator) = 0x1C
    CR (Carriage Return) = 0x0D -> نهاية الرسالة (FS ثم CR مع بعض)

ده الـ framing القياسي لأي جهاز بيبعت HL7 v2.x عبر شبكة (MLLP - Minimal
Lower Layer Protocol)، وده اللي أجهزة Dymind بتستخدمه حسب مستند
"LIS Communication Protocol" الرسمي بتاعهم.
"""
import logging
import socket

logger = logging.getLogger(__name__)

VT = b"\x0b"   # بداية الرسالة
FS = b"\x1c"   # جزء من نهاية الرسالة
CR = b"\x0d"   # جزء من نهاية الرسالة (FS + CR مع بعض = end of message)


class CBCTCPServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(1)
            logger.info(f"Listening on {self.host}:{self.port} ...")

            while True:
                conn, addr = server_sock.accept()
                logger.info(f"Connection from {addr}")
                try:
                    self._handle_connection(conn)
                except Exception as e:
                    logger.exception(f"Error handling connection: {e}")
                finally:
                    conn.close()

    def _handle_connection(self, conn: socket.socket):
        """
        بيقرا الـ stream ويفصل الرسايل على حسب MLLP framing (VT ... FS CR).
        كل رسالة كاملة بتتسجل خام عشان نشوف شكلها الحقيقي قبل ما نبني
        الـ HL7 parser عليها.
        """
        conn.settimeout(60)
        buffer = b""

        while True:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data
            logger.debug(f"Raw bytes received: {data!r}")

            while VT in buffer and (FS + CR) in buffer:
                start = buffer.index(VT) + 1
                end = buffer.index(FS + CR)
                message = buffer[start:end]
                buffer = buffer[end + 2:]

                logger.info(f"Full HL7 message received ({len(message)} bytes)")
                logger.info(f"Message content: {message!r}")

                # TODO: نمرر الرسالة لـ protocol_parser.py بعد ما نتأكد
                # من بنية الـ segments (MSH/PID/OBR/OBX) من رسالة حقيقية

                # نرد ACK بسيط عشان الجهاز يعرف إن الرسالة اتسلمت
                # (لسه placeholder - محتاج نبني MSH صح حسب فيلدز الرسالة الأصلية)
                # conn.sendall(VT + ack_bytes + FS + CR)

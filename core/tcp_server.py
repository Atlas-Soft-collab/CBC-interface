"""
TCP Server بيستقبل الاتصال من جهاز الـ CBC (Dymind).
الجهاز بيتصل بالـ IP/Port المحددين في config/settings.json
ويبعت البيانات بصيغة ASTM (على الأغلب) مؤطرة بـ ENQ/STX/ETX/EOT.

ملاحظة: ده skeleton أساسي - لسه محتاج تأكيد شكل الفريمنج
الفعلي من أول اتصال حقيقي مع الجهاز.
"""
import logging
import socket

logger = logging.getLogger(__name__)

# ASTM control characters (الأشهر في أجهزة الـ hematology analyzers)
ENQ = b"\x05"
ACK = b"\x06"
NAK = b"\x15"
STX = b"\x02"
ETX = b"\x03"
EOT = b"\x04"


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
        بيستقبل البيانات الخام ويسجلها.
        دلوقتي بيطبع/يسجل أي حاجة توصل عشان نشوف شكل الرسالة الحقيقي
        قبل ما نبني protocol_parser.py عليها.
        """
        conn.settimeout(30)
        buffer = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data
            logger.debug(f"Raw bytes received: {data!r}")

            # رد ACK مبدئي لأي إرسال (ASTM handshake عادةً محتاج كده)
            if ENQ in data:
                conn.sendall(ACK)

        logger.info(f"Full message received ({len(buffer)} bytes): {buffer!r}")
        # TODO: تبعت الـ buffer دي لـ protocol_parser.py بعد ما نأكد الصيغة

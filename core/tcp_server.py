"""
TCP Server بيستقبل الاتصال من جهاز الـ CBC (Dymind).
الجهاز بيتصل بالـ IP/Port المحددين في config/settings.json
ويبعت البيانات بصيغة HL7 عبر TCP، مؤطرة بـ MLLP framing:

    <VT> ... HL7 message ... <FS><CR>

بعد كل رسالة، السيرفر بيرد HL7 ACK (AA لو نجح التفكيك، AE لو حصل خطأ
في المعالجة، AR لو الرسالة نفسها مش مفهومة) - ده جزء أساسي من بروتوكول
HL7 عشان الجهاز يعرف إن النتيجة وصلت وموثوقة.
"""
import logging
import socket

from core.ack_builder import build_ack
from core.protocol_parser import parse_hl7_message
from core.sample_handler import handle_result

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
                    self._handle_connection(conn, addr)

                except (ConnectionResetError, BrokenPipeError, TimeoutError) as net_err:
                    # الاتصال اتقطع فجأة (الجهاز اتقفل، الشبكة وقعت...)
                    # يتسجل كـ warning والسيرفر يفضل شغال للاتصال الجاي
                    logger.warning(f"Connection with {addr} dropped unexpectedly: {net_err}")

                except Exception:
                    # أي حاجة تانية غير متوقعة - تتسجل بالتفصيل من غير
                    # ما توقّع السيرفر كله
                    logger.exception(f"Unexpected error while handling connection {addr}")

                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    logger.info(f"Connection with {addr} closed")

    def _handle_connection(self, conn: socket.socket, addr):
        """
        بيقرا الـ stream ويفصل الرسايل على حسب MLLP framing (VT ... FS CR).
        كل رسالة كاملة بتتبعت لـ protocol_parser ثم sample_handler،
        وبعدين بيترجعلها ACK مناسب.
        """
        conn.settimeout(60)
        buffer = b""

        while True:
            data = conn.recv(4096)
            if not data:
                logger.info(f"Connection closed by device {addr}")
                break
            buffer += data
            logger.debug(f"Raw bytes received: {data!r}")

            while VT in buffer and (FS + CR) in buffer:
                start = buffer.index(VT) + 1
                end = buffer.index(FS + CR)
                raw_message = buffer[start:end]
                buffer = buffer[end + 2:]

                logger.info(f"Full HL7 message received ({len(raw_message)} bytes)")

                message_text = raw_message.decode("ascii", errors="replace")

                try:
                    result = parse_hl7_message(raw_message)
                    logger.info(
                        f"Parsed sample_id={result.sample_id} "
                        f"wbc={result.wbc} rbc={result.rbc} hgb={result.hgb}"
                    )
                    handle_result(result)
                    ack_bytes = build_ack(message_text, ack_code="AA")

                except (ValueError, KeyError, IndexError) as parse_err:
                    # رسالة وصلت لكن ناقصة/تالفة - نسجل ونرد AE
                    logger.error(
                        f"Failed to parse/save HL7 message from {addr}: {parse_err}",
                        exc_info=True,
                    )
                    ack_bytes = build_ack(
                        message_text, ack_code="AE", error_text=str(parse_err)[:80]
                    )

                except Exception as e:
                    logger.exception(f"Unexpected error handling message from {addr}: {e}")
                    ack_bytes = build_ack(
                        message_text, ack_code="AE", error_text="Internal processing error"
                    )

                conn.sendall(ack_bytes)
                logger.debug(f"ACK sent to {addr}")

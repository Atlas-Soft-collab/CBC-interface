"""
device_simulator.py
سكريبت بيقلّد جهاز الـ CBC (Dymind) - بيفتح اتصال TCP للسيرفر بتاعنا
ويبعتله رسالة HL7 حقيقية الشكل، مؤطرة بـ MLLP framing، بالظبط زي ما
الجهاز الحقيقي هيعمل.

الاستخدام:
    1. شغّل السيرفر الأول في terminal منفصل:
       python main.py

    2. شغّل السيمولاتور في terminal تاني:
       python tools/device_simulator.py

    3. شوف ملف logs/cbc_interface.log هتلاقي الرسالة اتستقبلت واتفكّت صح.
"""
import socket
import sys
import time

VT = b"\x0b"
FS = b"\x1c"
CR = b"\x0d"

FAKE_HL7_MESSAGE = (
    b"MSH|^~\\&|Dymind|LabDevice|LIS|LAB|20260910221600||ORU^R01|MSG001|P|2.3.1\r"
    b"PID|1||PATIENT001^^^||\r"
    b"OBR|1|250908001||\r"
    b"OBX|1|NM|6690-2^WBC^LN||7.2|10*9/L|4.0-10.0|N|||F\r"
    b"OBX|2|NM|789-8^RBC^LN||4.85|10*12/L|4.2-5.4|N|||F\r"
    b"OBX|3|NM|718-7^HGB^LN||14.2|g/dL|12.0-16.0|N|||F\r"
    b"OBX|4|NM|4544-3^HCT^LN||42.0|%|36.0-46.0|N|||F\r"
    b"OBX|5|NM|777-3^PLT^LN||265|10*9/L|150-450|N|||F\r"
)


def send_fake_message(host: str, port: int):
    framed_message = VT + FAKE_HL7_MESSAGE + FS + CR

    print(f"Connecting to {host}:{port} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        sock.connect((host, port))
        print("Connected. Sending fake HL7 message...")
        sock.sendall(framed_message)

        # ننتظر شوية لو السيرفر هيرد ACK
        try:
            response = sock.recv(4096)
            if response:
                print(f"Received response from server: {response!r}")
        except socket.timeout:
            print("No ACK received (server may not send one yet - that's OK for now).")

    print("Done. Check logs/cbc_interface.log on the server side.")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5600

    time.sleep(0.5)
    send_fake_message(host, port)

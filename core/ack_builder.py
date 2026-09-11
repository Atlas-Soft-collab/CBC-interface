"""
ack_builder.py
بيبني رسالة HL7 ACK (MSH + MSA) رد على أي رسالة واردة، ملفوفة بـ MLLP
framing جاهزة للإرسال مباشرة على الـ socket.

مبني على الباتش اللي جهزه [صاحبك] - شغل نضيف ومطابق لمعايير HL7 v2.x.
"""
from datetime import datetime


def _get_field(segment_fields, index, default=""):
    """يرجع الحقل رقم index من segment، أو default لو مش موجود."""
    try:
        return segment_fields[index]
    except IndexError:
        return default


def build_ack(raw_msg: str, ack_code: str = "AA", error_text: str = "") -> bytes:
    """
    ack_code:
        "AA" = Application Accept (الحالة العادية - كل حاجة تمام)
        "AE" = Application Error (وصلت الرسالة لكن حصل خطأ في المعالجة)
        "AR" = Application Reject (الرسالة مرفوضة / مش متعرف على الصيغة)

    ملاحظة HL7 مهمة: في الـ ACK، الـ Sending/Receiving App والـ Facility
    بيتعكسوا بالنسبة للرسالة الأصلية، وMSA-2 لازم يساوي MSH-10 بتاع
    الرسالة الأصلية بالظبط عشان الجهاز يعرف يربط الـ ACK بالرسالة الصح.
    """
    import logging
    logger = logging.getLogger(__name__)

    MLLP_START = b"\x0b"
    MLLP_END = b"\x1c\x0d"

    try:
        segments = raw_msg.strip().split("\r")
        msh_fields = segments[0].split("|")

        sending_app = _get_field(msh_fields, 2)
        sending_facility = _get_field(msh_fields, 3)
        receiving_app = _get_field(msh_fields, 4)
        receiving_facility = _get_field(msh_fields, 5)
        message_control_id = _get_field(msh_fields, 9, "UNKNOWN")

    except Exception:
        logger.exception(
            "Failed to parse incoming MSH for ACK building; "
            "falling back to a minimal reject ACK"
        )
        sending_app = sending_facility = receiving_app = receiving_facility = ""
        message_control_id = "UNKNOWN"
        ack_code = "AR"
        error_text = error_text or "Malformed or unparsable MSH segment"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    msh = (
        f"MSH|^~\\&|{receiving_app}|{receiving_facility}|"
        f"{sending_app}|{sending_facility}|{timestamp}||"
        f"ACK^R01|ACK{message_control_id}|P|2.3.1"
    )
    msa = f"MSA|{ack_code}|{message_control_id}"
    if error_text:
        msa += f"|{error_text}"

    ack_message = f"{msh}\r{msa}\r"
    return MLLP_START + ack_message.encode("utf-8") + MLLP_END

"""
protocol_parser.py
بيفكك رسالة HL7 (اللي وصلت من tcp_server.py) لنتائج CBC مفهومة.

شكل HL7 v2.x المتوقع تقريبًا (segments مفصولة بـ \\r، fields بـ |):

  MSH|^~\\&|Dymind|LabDevice|LIS|LAB|20260910221600||ORU^R01|MSG001|P|2.3.1
  PID|1||PATIENT001^^^||...
  OBR|1|250908001||...
  OBX|1|NM|6690-2^WBC^LN||7.2|10*9/L|4.0-10.0|N|||F
  OBX|2|NM|789-8^RBC^LN||4.85|10*12/L|4.2-5.4|N|||F
  ...

لسه TODO: تأكيد أسماء OBX identifiers (زي 6690-2 لـ WBC) وترتيب
الحقول الفعلي، بعد أول رسالة حقيقية توصل من الجهاز.
"""
from dataclasses import dataclass, field

# خريطة مبدئية لأكواد LOINC الشائعة لتحاليل CBC -> اسم الحقل عندنا
# (هنعدلها/نكملها بعد ما نشوف الأكواد الحقيقية اللي الجهاز بيبعتها)
LOINC_TO_FIELD = {
    "6690-2": "wbc",
    "789-8": "rbc",
    "718-7": "hgb",
    "4544-3": "hct",
    "787-2": "mcv",
    "785-6": "mch",
    "786-4": "mchc",
    "777-3": "plt",
    "788-0": "rdw",
}

# القيم اللي لازم يتحقق وجود واحدة منها على الأقل عشان نعتبر إن فيه
# نتيجة فعلية اتقرأت من الرسالة (مش بس MSH/PID فاضيين من غير OBX).
# الشرط "على الأقل واحدة" مش "الثلاثة كلهم" - عشان بعض الرسائل ممكن
# تكون retest لقيمة واحدة بس. لو اتأكدنا إن كل رسالة من الجهاز لازم
# تجيب الباقة كاملة، غيّر any() لـ all() في _validate_core_results.
REQUIRED_CORE_FIELDS = ("wbc", "rbc", "hgb")


@dataclass
class CBCResult:
    sample_id: str = ""
    wbc: float | None = None
    rbc: float | None = None
    hgb: float | None = None
    hct: float | None = None
    mcv: float | None = None
    mch: float | None = None
    mchc: float | None = None
    plt: float | None = None
    rdw: float | None = None
    raw_segments: list = field(default_factory=list)


def _validate_core_results(result: CBCResult, message_control_id: str = "") -> None:
    """
    يرمي ValueError لو مفيش أي قيمة من REQUIRED_CORE_FIELDS موجودة فعليًا
    (مش None) - عشان tcp_server.py يرد AE بدل AA تلقائيًا لما الرسالة
    اتفكّت لكن مفيهاش أي نتيجة فعلية.
    """
    found_any = any(
        getattr(result, field_name) is not None
        for field_name in REQUIRED_CORE_FIELDS
    )

    if not found_any:
        raise ValueError(
            f"No core CBC values (WBC/RBC/HGB) found in message "
            f"{message_control_id or '(no control id)'} - "
            f"message parsed but contained no usable OBX results"
        )


def parse_hl7_message(raw: bytes) -> CBCResult:
    """
    بيفكك رسالة HL7 واحدة (من غير MLLP framing - ده بيتشال في tcp_server)
    ويرجع CBCResult. يرمي ValueError لو الرسالة اتفكّت لكن مفيهاش أي
    قيمة أساسية فعلية (راجع _validate_core_results).
    """
    text = raw.decode("ascii", errors="replace")
    segments = [seg for seg in text.split("\r") if seg]

    result = CBCResult(raw_segments=segments)
    message_control_id = ""

    for segment in segments:
        fields_ = segment.split("|")
        segment_type = fields_[0]

        if segment_type == "MSH" and len(fields_) > 9:
            message_control_id = fields_[9]

        elif segment_type == "OBR" and len(fields_) > 2:
            # الـ Sample ID غالبًا في OBR-2 أو OBR-3 - محتاج تأكيد
            result.sample_id = fields_[2] or fields_[1]

        elif segment_type == "OBX" and len(fields_) > 5:
            # OBX|seq|type|code^name^system||value|units|...
            observation_id = fields_[3].split("^")[0]
            value = fields_[5]
            field_name = LOINC_TO_FIELD.get(observation_id)
            if field_name:
                try:
                    setattr(result, field_name, float(value))
                except ValueError:
                    pass  # القيمة مش رقم - نسيبها زي ما هي في raw_segments

    _validate_core_results(result, message_control_id)

    return result

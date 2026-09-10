"""
protocol_parser.py
بيفكك الرسالة الخام (اللي وصلت من tcp_server.py) لنتائج CBC مفهومة.

لسه TODO - محتاجين رسالة حقيقية واحدة على الأقل من الجهاز
عشان نعرف شكل الـ ASTM records بالظبط (H|, P|, O|, R|, L| ...)
"""
from dataclasses import dataclass, field


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
    raw_fields: dict = field(default_factory=dict)


def parse_astm_message(raw: bytes) -> list[CBCResult]:
    """
    Placeholder - هنبنيها بعد ما نشوف رسالة حقيقية من الجهاز.
    شكل ASTM المتوقع تقريبًا:
      H|\^&|||...          -> Header
      P|1||PatientID|...   -> Patient
      O|1|SampleID|...     -> Order
      R|1|^^^WBC|7.2|...   -> Result (سطر لكل قيمة)
      L|1|N                -> Terminator
    """
    text = raw.decode("ascii", errors="replace")
    lines = [line for line in text.split("\r") if line]

    results = []
    current = CBCResult()

    for line in lines:
        if line.startswith("O|"):
            fields = line.split("|")
            if len(fields) > 2:
                current.sample_id = fields[2]
        elif line.startswith("R|"):
            fields = line.split("|")
            # TODO: تحديد index القيمة والاسم بعد شوف رسالة حقيقية
            current.raw_fields[line] = fields

    if current.sample_id or current.raw_fields:
        results.append(current)

    return results

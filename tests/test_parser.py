"""
اختبار مبدئي للـ parser على رسالة HL7 وهمية.
هنحدّث الرسالة دي بعد ما ناخد رسالة حقيقية من الجهاز.
"""
from core.protocol_parser import parse_hl7_message

FAKE_HL7_MESSAGE = (
    b"MSH|^~\\&|Dymind|LabDevice|LIS|LAB|20260910221600||ORU^R01|MSG001|P|2.3.1\r"
    b"PID|1||PATIENT001^^^||\r"
    b"OBR|1|250908001||\r"
    b"OBX|1|NM|6690-2^WBC^LN||7.2|10*9/L|4.0-10.0|N|||F\r"
    b"OBX|2|NM|789-8^RBC^LN||4.85|10*12/L|4.2-5.4|N|||F\r"
)


def test_parse_sample_id_and_values():
    result = parse_hl7_message(FAKE_HL7_MESSAGE)
    assert result.sample_id == "250908001"
    assert result.wbc == 7.2
    assert result.rbc == 4.85


if __name__ == "__main__":
    test_parse_sample_id_and_values()
    print("OK - basic HL7 parser test passed")

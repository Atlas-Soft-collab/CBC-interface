"""
اختبار مبدئي للـ parser على رسالة ASTM وهمية.
هنحدّث الرسالة دي بعد ما ناخد رسالة حقيقية من الجهاز.
"""
from core.protocol_parser import parse_astm_message

FAKE_ASTM_MESSAGE = (
    b"H|\\^&|||Dymind|||||||P|1\r"
    b"P|1||PATIENT001||\r"
    b"O|1|250908001||\r"
    b"R|1|^^^WBC|7.2|10^9/L||N||F\r"
    b"L|1|N\r"
)


def test_parse_sample_id():
    results = parse_astm_message(FAKE_ASTM_MESSAGE)
    assert len(results) == 1
    assert results[0].sample_id == "250908001"


if __name__ == "__main__":
    test_parse_sample_id()
    print("OK - basic parser test passed")

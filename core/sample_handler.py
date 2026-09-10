"""
sample_handler.py
بياخد CBCResult (من protocol_parser) ويحفظه عن طريق database.py،
وممكن بعدين يبعته لـ LIS تاني لو احتجنا Bidirectional communication.
"""
import logging

from core.protocol_parser import CBCResult
from storage.database import save_result

logger = logging.getLogger(__name__)


def handle_result(result: CBCResult):
    logger.info(f"Handling result for sample: {result.sample_id}")
    save_result(result)
    # TODO: لو احتجنا نبعت تأكيد او النتيجة لـ LIS خارجي تاني

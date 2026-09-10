"""
CBC Interface - نقطة الدخول الرئيسية
بيشغل TCP server عشان يستقبل بيانات من جهاز Dymind CBC Analyzer
"""
import json
import logging
import os
from core.tcp_server import CBCTCPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    config_path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def setup_logging(config):
    log_path = os.path.join(BASE_DIR, config["logging"]["path"])
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    level = getattr(logging, config["logging"]["level"], logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main():
    config = load_config()
    setup_logging(config)
    logging.info("Starting CBC Interface...")

    server = CBCTCPServer(
        host=config["tcp_server"]["listen_ip"],
        port=config["tcp_server"]["listen_port"],
    )
    server.start()


if __name__ == "__main__":
    main()

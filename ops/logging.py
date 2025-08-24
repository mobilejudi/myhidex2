# ops/logging.py
import logging, sys, structlog, os

def setup_logging():
    level = os.getenv("LOG_LEVEL","INFO")
    logging.basicConfig(stream=sys.stdout, level=level)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

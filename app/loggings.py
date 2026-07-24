import logging.config
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": (
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            )
        },
    },

    "handlers": {

        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },

        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "app.log",
            "formatter": "default",
            "encoding": "utf-8",
        },
    },

    "root": {
        "level": "INFO",
        "handlers": [
            "console",
            "file",
        ],
    },

    "loggers": {

        "uvicorn": {
            "level": "INFO",
            "handlers": [
                "console",
                "file",
            ],
            "propagate": False,
        },

        "uvicorn.error": {
            "level": "INFO",
            "handlers": [
                "console",
                "file",
            ],
            "propagate": False,
        },

        "uvicorn.access": {
            "level": "INFO",
            "handlers": [
                "console",
                "file",
            ],
            "propagate": False,
        },

        "aiogram": {
            "level": "INFO",
            "handlers": [
                "console",
                "file",
            ],
            "propagate": False,
        },
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

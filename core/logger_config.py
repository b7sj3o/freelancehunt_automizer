import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Logging path
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(name: str, level=logging.DEBUG, log_file: str = None):
    """
    Повертає налаштований логер для модуля
    :param name: ім'я логера (__name__ модуля)
    :param level: рівень логування
    :param log_file: шлях до файлу (якщо None, лог лише в консоль)
    """
    
    logger = logging.Logger(name)
    logger.setLevel(level)
    logger.propagate = False # Щоб не дублювати логи у root

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s | %(filename)s:%(lineno)d"
    )

    if log_file:
        file_path = LOG_DIR / log_file
        file_handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
    

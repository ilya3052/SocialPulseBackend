# logger.py
import logging
import os


def setup_logger(
    name: str = "app_logger",
    log_file: str = "debug.log",
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Простой файловый логгер.
    Без сложных handler'ов и formatter'ов.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # чтобы не дублировались хендлеры при перезапуске (например, в dev)
    if logger.handlers:
        return logger

    # создаём директорию если нужно
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

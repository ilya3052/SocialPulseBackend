import logging
import os
import json
from datetime import datetime


class HtmlDebugFileHandler(logging.FileHandler):
    """
    Если в сообщении обнаружен HTML-документ (django debug page),
    сохраняет его в отдельный .html файл.
    """

    def emit(self, record: logging.LogRecord):
        try:
            message = record.getMessage()

            html_content = None

            # Если сообщение — JSON с debug_message
            try:
                parsed = json.loads(message)
                debug_message = parsed.get("debug_message")
                if debug_message and "<html" in debug_message.lower():
                    html_content = debug_message
            except Exception:
                pass

            # Если просто строка с html
            if not html_content and "<html" in message.lower():
                html_content = message

            if html_content:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                html_filename = f"django_debug_{timestamp}.html"
                html_path = os.path.join(
                    os.path.dirname(self.baseFilename),
                    html_filename
                )

                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                return  # НЕ пишем в основной лог

        except Exception:
            pass

        super().emit(record)


def setup_logger(
    name: str = "app_logger",
    log_file: str = "debug.log",
    level: int = logging.DEBUG,
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

    handler = HtmlDebugFileHandler(log_file, encoding="utf-8")
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
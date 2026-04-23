import json


def try_parse_json(value):
    """
    Если value — строка с JSON, пытаемся распарсить.
    Иначе возвращаем как есть.
    """
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value

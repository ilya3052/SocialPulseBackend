import secrets

def generate_short_token() -> str:
    url_token = secrets.token_urlsafe(48)
    return url_token

def prepare_message(token) -> str:
    url = f'http://127.0.0.1/email/activate?token={token}'
    # добавить в сообщение больше информации, возможно даже сделать html шаблон в котором будут также отображаться некоторые данные пользователя
    message = f"Для подтверждения электронной почты перейдите по <p><a href=\"{url}\" target=_blank>ссылке</a></p>"

    return message
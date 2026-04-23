def prepare_message(token) -> str:
    url = f'https://socialpulse.sandbox.com/email/activate?token={token}'
    # добавить в сообщение больше информации, возможно даже сделать html шаблон в котором будут также отображаться некоторые данные пользователя
    message = f"Для подтверждения электронной почты перейдите по <a href=\"{url}\" target=_blank>ссылке</a>"

    return message

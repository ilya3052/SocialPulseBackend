import secrets


def generate_short_token() -> str:
    url_token = secrets.token_urlsafe(48)
    return url_token

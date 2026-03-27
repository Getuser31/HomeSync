import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def check_email_format(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))

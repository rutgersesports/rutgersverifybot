from config import EMAIL_CODE_LENGTH
import random

SMTP_SERVER: str = "smtp.outlook.com"
PORT: int = 587


def create_verification_code() -> str:
    out = ""
    for x in range(EMAIL_CODE_LENGTH):
        out += str(random.randint(0, 9))

    return out

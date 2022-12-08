from config import EMAIL_CODE_EXPIRE


class MemberQueue:
    def __init__(self, email: str, netid: str, code: str) -> None:
        self.email = email
        self.netid = netid
        self.code = code
        self.expire = EMAIL_CODE_EXPIRE

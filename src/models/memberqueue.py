from utils import create_verification_code
from config import EMAIL_CODE_EXPIRE
import time


class MemberQueue:
    def __init__(self, email: str, netid: str, discord_id: int, guild_id: int) -> None:
        self.email = email
        self.netid = netid
        self.discord_id = discord_id
        self.guild_id = guild_id
        self.code = create_verification_code()
        self.expire = EMAIL_CODE_EXPIRE + time.time()

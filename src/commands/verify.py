from typing import Any
from discord.ext import commands
from discord.ext.commands import Bot
from models.memberqueue import MemberQueue
from config import BOT_EMAIL
import discord


class VerifyCog(commands.Cog):
    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot

    @commands.command(name="verify")
    async def verify(self, ctx: Any):
        user_email = ctx.args[0]
        netid = ctx.args[1]
        mq = MemberQueue(user_email, netid)
        self.bot.server.sendmail(BOT_EMAIL, user_email, "Test")


async def setup(bot: Bot) -> None:
    await bot.add_cog()

from typing import Any
from discord.ext import commands
from discord.ext.commands import Bot
from models.memberqueue import MemberQueue
from models.embed_templates import email_sent
from config import BOT_EMAIL, BOT_EMAIL_PWD
from utils import SMTP_SERVER, PORT
import discord
import ssl
import smtplib


class VerifyCog(commands.Cog):
    def __init__(self, bot: discord.Client) -> None:
        self.bot: discord.Client = bot

    @commands.command()
    async def verify(self, ctx: Any, user_email: str, netid: str):
        try:
            self.server = smtplib.SMTP(SMTP_SERVER, PORT)
            self.server.ehlo()
            self.server.starttls(context=ssl.create_default_context())
            self.server.login(BOT_EMAIL, BOT_EMAIL_PWD)
            mq: MemberQueue = MemberQueue(user_email, netid, ctx.author.id)
            code: str = mq.code
            message = f"""
Here is your verification code: {code}
            """
            self.server.sendmail(BOT_EMAIL, user_email, message)
            self.bot.codes[code] = mq

            await ctx.channel.send(embed=email_sent())
        except Exception as e:
            print(e)
        finally:
            self.server.quit()


async def setup(bot: Bot) -> None:
    await bot.add_cog(VerifyCog(bot))

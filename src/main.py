from config import TOKEN, BOT_EMAIL, BOT_EMAIL_PWD
from utils import SMTP_SERVER, PORT
from commands.verify import VerifyCog
from discord.ext import commands
import discord
import ssl
import smtplib


class Bot(commands.Bot):
    async def on_ready(self):
        startup_extensions = ["verify"]
        for extension in startup_extensions:
            try:
                await bot.load_extension(extension)
            except Exception as e:
                exc = "{}: {}".format(type(e).__name__, e)
                print("Failed to load extension {}\n{}".format(extension, exc))

        self.queued_members = []
        try:
            self.server = smtplib.SMTP(SMTP_SERVER, PORT)
            self.server.ehlo()
            self.server.starttls(context=ssl.create_default_context())
            r = self.server.login(BOT_EMAIL, BOT_EMAIL_PWD)
            print(r)
            e = self.server.sendmail(BOT_EMAIL, "andrew.jwn.hong@gmail.com", "Test")
            print(e)
        except Exception as e:
            print(e)
        finally:
            self.server.quit()

    async def on_message(self, message: discord.Message) -> None:
        pass


intents = discord.Intents.default()
intents.message_content = True

bot = Bot(intents=intents, command_prefix="?")

bot.run(TOKEN)

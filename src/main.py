from typing import List
from config import TOKEN
from models.memberqueue import MemberQueue
from discord.ext import commands
import discord


class Bot(commands.Bot):
    async def on_ready(self):
        self.queued_members: List[MemberQueue] = []

        startup_extensions: List[str] = ["commands.verify"]
        for extension in startup_extensions:
            try:
                await bot.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                print(
                    "Failed to load extension {}\n{}".format(
                        extension, "{}: {}".format(type(e).__name__, e)
                    )
                )


intents: discord.Intents = discord.Intents.default()
intents.message_content = True

bot: Bot = Bot(intents=intents, command_prefix="?")

bot.run(TOKEN)

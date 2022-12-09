from typing import List, Dict, Any
from config import TOKEN
from models.memberqueue import MemberQueue
from models.embed_templates import verified_embed, email_sent
from discord.ext import commands, tasks
from config import BOT_EMAIL, BOT_EMAIL_PWD
from utils import SMTP_SERVER, PORT
import ssl
import smtplib
import discord
import time
import json


class Bot(commands.Bot):
    async def on_ready(self) -> None:
        self.awaiting_email: Dict[str, discord.Guild] = {}
        self.codes: Dict[str, MemberQueue] = {}

        startup_extensions: List[str] = [
            "commands.register",
            "commands.agree",
        ]
        for extension in startup_extensions:
            try:
                await bot.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                file_name = type(e).__name__
                print(f"Failed to load extension {file_name}\n{e}")

        self.check_queue.start()

    async def on_message(self, message: discord.Message) -> None:
        await self.process_commands(message)

        msg_content: str = message.content
        channel: Any = message.channel
        author_id: int = message.author.id
        is_channel_dm: bool = message.channel.type == discord.ChannelType.private

        if author_id == self.user.id:
            return

        if is_channel_dm and str(author_id) in self.awaiting_email:
            try:
                self.server = smtplib.SMTP(SMTP_SERVER, PORT)
                self.server.ehlo()
                self.server.starttls(context=ssl.create_default_context())
                self.server.login(BOT_EMAIL, BOT_EMAIL_PWD)
                user_email = message.content
                mq: MemberQueue = MemberQueue(
                    user_email,
                    "",
                    message.author.id,
                    self.awaiting_email[str(author_id)],
                )
                code: str = mq.code
                email_message = f"""
Here is your verification code: {code}
                """
                self.server.sendmail(BOT_EMAIL, user_email, email_message)
                self.codes[code] = mq
                self.awaiting_email.pop(str(author_id))

                await message.author.dm_channel.send(embed=email_sent(user_email))
            except Exception as e:
                await message.author.dm_channel.send("Invalid email. Try again")
            finally:
                self.server.quit()

        elif is_channel_dm and msg_content in self.codes:
            c: MemberQueue = self.codes[msg_content]
            if author_id == c.discord_id:
                guild_json_file_read = open("data/guilds.json", "r")
                data = json.load(guild_json_file_read)
                guild: discord.Guild = self.codes[msg_content].guild
                verified_role_id = data[str(guild.id)]["verified_role"]
                verified_role = discord.utils.get(guild.roles, id=verified_role_id)
                guild_member: discord.Member = guild.get_member(author_id)
                await guild_member.add_roles(verified_role)
                self.codes.pop(msg_content)

                await channel.send(embed=verified_embed())

    @tasks.loop(seconds=1.0)
    async def check_queue(self) -> None:
        for x in list(self.codes.keys()):
            if self.codes[x].expire <= time.time():
                self.codes.pop(x)


intents: discord.Intents = discord.Intents.all()

bot: Bot = Bot(intents=intents, command_prefix="?")

bot.run(TOKEN)

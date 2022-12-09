from typing import Any
from discord.ext import commands
from discord.ext.commands import Bot, Context
from models.embed_templates import ask_email
import discord
import json


class AgreeCog(commands.Cog):
    def __init__(self, bot: discord.Client) -> None:
        self.bot: discord.Client = bot

    @commands.command()
    async def agree(self, ctx: Context):
        guild_json_file_read = open("data/guilds.json", "r")
        data = json.load(guild_json_file_read)

        if str(ctx.guild.id) not in data or (
            str(ctx.guild.id) in data and "verified_role" not in data[str(ctx.guild.id)]
        ):
            await ctx.channel.send("Agree channel does not exist.")
            return

        role_id: int = data[str(ctx.guild.id)]["verified_role"]
        role: discord.Role = discord.utils.get(ctx.guild.roles, id=role_id)

        if data[str(ctx.guild.id)]["readme_channel_id"] != ctx.channel.id:
            await ctx.channel.send("Not the correct channel.")
            return

        if role in ctx.author.roles:
            await ctx.channel.send("You are already verified..")
            return

        if ctx.author.id in self.bot.awaiting_email:
            self.awaiting_email.pop(str(ctx.author.id))

        self.bot.awaiting_email[str(ctx.author.id)] = ctx.guild
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(embed=ask_email())


async def setup(bot: Bot) -> None:
    await bot.add_cog(AgreeCog(bot))

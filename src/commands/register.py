from typing import Dict
from discord.ext import commands
from discord.ext.commands import Bot, Context
import discord
import json


class Register(commands.Cog):
    def __init__(self, bot: discord.Client) -> None:
        self.bot: discord.Client = bot

    @commands.command()
    async def register(self, ctx: Context, *args):
        if len(args) == 0 or len(args) >= 3:
            await ctx.channel.send(
                "Invalid argument. Use either `verifyrole` or `readme`"
            )
            return

        register_type = args[0]
        if register_type == "verifyrole":
            await self.registerrole(ctx, int(args[1]))
        elif register_type == "readme":
            await self.registerreadme(ctx)

    async def registerrole(self, ctx: Context, role_id: int):
        guild_id_str = str(ctx.guild.id)
        channel = ctx.channel
        role: discord.Role = discord.utils.get(ctx.guild.roles, id=role_id)
        if type(role) is not discord.Role:
            await channel.send("Invalid role.")
            return

        guild_json_file_read = open("data/guilds.json", "r")
        data = json.load(guild_json_file_read)
        if guild_id_str not in data:
            data[guild_id_str] = {}

        data[guild_id_str]["verified_role"] = role.id

        guild_json_file_write = open("data/guilds.json", "w")
        json.dump(data, guild_json_file_write)
        guild_json_file_read.close()
        guild_json_file_write.close()

        await channel.send(f"Registered `{role.name}` as verified role")

    async def registerreadme(self, ctx: Context):
        guild_id_str = str(ctx.guild.id)
        channel = ctx.channel
        msg = ctx.message

        guild_json_file_read = open("data/guilds.json", "r")
        data = json.load(guild_json_file_read)
        if guild_id_str not in data:
            data[guild_id_str] = {}

        data[guild_id_str]["readme_channel_id"] = msg.channel.id

        guild_json_file_write = open("data/guilds.json", "w")
        json.dump(data, guild_json_file_write)
        guild_json_file_read.close()
        guild_json_file_write.close()

        await channel.send(f"Registered `id:{msg.channel.id}` as README channel")


async def setup(bot: Bot) -> None:
    await bot.add_cog(Register(bot))

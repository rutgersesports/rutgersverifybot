from collections import defaultdict

import hikari
import lightbulb
import miru
import requests

from src.database.firebase import is_agreement_channel, has_agreement_roles
from src.commands.modals import SelectMenu, HubMenu
from src.commands.configs import MainMenu

plugin = lightbulb.Plugin("slash_plugin")


@plugin.command()
@lightbulb.add_checks(
    lightbulb.checks.guild_only,
    lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
)
@lightbulb.set_help(
    "Configure all of your server settings from inside /config!\n"
    "If you have any issues, contact xposea#0001",
    docstring=False,
)
@lightbulb.command(
    name="config", description="Configure this server's CoolCat settings"
)
@lightbulb.implements(lightbulb.SlashCommand)
async def config(ctx: lightbulb.SlashContext) -> None:
    me = await ctx.bot.rest.fetch_user(193736005239439360)
    view = MainMenu(author=ctx.author, timeout=600)
    embed = (
        hikari.Embed(
            title="CoolCat Configuration Menu",
            description="Configure your CoolCat server settings here!\n"
            r"If there are any issues, contact me for help /ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xFFFFFF,
        )
        .set_thumbnail(plugin.bot.get_me().avatar_url)
        .set_footer(
            text=f"Created by {me.username}#{me.discriminator}", icon=me.avatar_url
        )
    )
    message = await ctx.respond(embed, components=view.build())
    await view.start(message)


@plugin.command()
@lightbulb.add_checks(
    lightbulb.checks.guild_only,
    lightbulb.Check(is_agreement_channel),
    lightbulb.Check(has_agreement_roles),
)
@lightbulb.set_help(
    "This command will start the verification process for a user! This requires an agreement channel to"
    " be set, as well as any agreement roles! Please make sure users can type in the agreement "
    "channel!",
    docstring=False,
)
@lightbulb.command(name="agree", description="Start the verification process.")
@lightbulb.implements(lightbulb.SlashCommand)
async def agree(ctx: lightbulb.SlashContext) -> None:
    try:
        db_guild = plugin.bot.guilds[ctx.guild_id]
    except KeyError:
        return
    if not db_guild:
        return
    try:
        all_roles = db_guild["all_roles"]
    except KeyError:
        await ctx.respond(
            "This server has not set up their agreement roles. This shouldn't happen. Contact xposea#0001 for help."
        )
        return
    view = miru.View()
    view.add_item(
        SelectMenu(
            options=[miru.SelectOption(label=k) for k in all_roles.keys()][::-1],
            db_guild=db_guild,
        )
    )
    message = await ctx.respond(
        "Select your role:",
        components=view.build(),
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await view.start(message)
    await view.wait()


@plugin.command()
@lightbulb.option(
    name="scope",
    description="The scope of information to find",
    type=str,
    required=True,
    choices=["current", "all"],
)
@lightbulb.set_help(
    "Use this command to get some info about the servers CoolCat is in! Choosing 'all' as the scope "
    "will tell you all the servers CoolCat is in, while choosing 'current' will tell you about the "
    "server the command is used in.",
    docstring=False,
)
@lightbulb.command(
    name="server_info",
    description="Shows all the servers that CoolCat is in.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def server_info(ctx: lightbulb.SlashContext):
    if ctx.options.scope == "current":
        await ctx.respond(
            "Not implemented yet, this will show all config options soon",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    servers = plugin.bot.cache.get_available_guilds_view().values()
    await ctx.respond(
        f"CoolCat bot is in the following servers:\n"
        f"{', '.join([guild.name for guild in servers])}\n"
        f"Total server count: {len(servers)}",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


# Creates an invite for every server that has it enabled
@plugin.command()
@lightbulb.set_help(
    "Use this command to go from one server to another!\n"
    "If you'd like to disable this feature, use the /allow_invites command!",
    docstring=False,
)
@lightbulb.command(
    name="server_hub",
    description="Creates invites for all the servers CoolCat is in!",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def server_hub(ctx: lightbulb.SlashContext):
    guilds = plugin.bot.cache.get_available_guilds_view().values()
    available_guilds = defaultdict()
    db_guilds = plugin.bot.guilds
    if not db_guilds:
        await ctx.respond(
            "There are no servers to hub to.",
            components=[],
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    for guild in guilds:
        try:
            status = db_guilds[guild.id]["allow_invites"]
        except KeyError:
            plugin.bot.db.child("guilds").child(guild.id).child("allow_invites").set(
                True
            )
            plugin.bot.guilds[guild.id]["allow_invites"] = True
            status = True
        if status:
            available_guilds[guild.id] = guild
    if len(available_guilds) == 0:
        await ctx.respond(
            "There are no servers to hub to.",
            components=[],
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    view = miru.View()
    view.add_item(
        HubMenu(
            options=[
                miru.SelectOption(label=guild.name, value=str(guild_id))
                for guild_id, guild in available_guilds.items()
            ],
            guilds=available_guilds,
        )
    )
    message = await ctx.respond(
        "Select a server to go to!:",
        components=view.build(),
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await view.start(message)
    await view.wait()


# On_error used to check if people are missing permissions for slash commands, will change to modal system soon tm
@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.MissingRequiredPermission):
        await event.context.respond(
            f"You do not have permissions to use `{event.context.command.name}`.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    elif isinstance(event.exception, lightbulb.CheckFailure):
        await event.context.respond(event.exception, flags=hikari.MessageFlag.EPHEMERAL)
    else:
        pass


# Fun little on ping message
@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_ping(event: hikari.GuildMessageCreateEvent):
    if event.content is None:
        return
    if not event.is_human:
        return
    if plugin.bot.get_me().mention not in event.content:
        return
    await event.message.respond(
        f"meow /ᐠ۪. ̱ . ۪ᐟ\\\\ﾉ",
        attachment=hikari.Bytes(
            requests.get(
                requests.get(
                    "https://api.thecatapi.com/v1/images/search?format=json&type=jpg"
                ).json()[0]["url"]
            ).content,
            "meow.png",
        ),
        # ,
        # attachment=hikari.Bytes(
        #     requests.get("https://cataas.com/cat/cute").content, "meow.png"
        # ),
    )


# Custom help command, needs lots of fine-tuning.
class CustomHelp(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, context):
        print(self.bot.slash_commands.items())
        commands = "\n".join(self.bot.slash_commands.keys())
        embed = (
            hikari.Embed(
                title="==== Bot Help ====",
                description=f"A verification bot created for Rutgers Esports!\n\n"
                f"For more information:\n\n /help [command|category]\n\n"
                f"If there are still issues, please contact xposea#0001 on discord.\n\n"
                f"Available commands:**\n{commands}**",
                color=0x315399,
            )
            .set_footer(
                f"Requested by {context.author.username}{context.author.discriminator}",
                icon=context.author.avatar_url,
            )
            .set_thumbnail(plugin.bot.get_me().avatar_url)
        )
        await context.respond(embed=embed)

    async def send_plugin_help(self, context, plg):
        await context.respond("Not yet implemented")

    async def send_command_help(self, context, command):
        if command.name == "help":
            await context.respond(
                r"Oh, so you're a real funny guy huh? A real comedian over here. /ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
            )
            return
        embed = (
            hikari.Embed(
                title="==== Bot Help ====",
                description=f"**{command.name}**:\n\n{command.get_help(context)}",
                color=0x315399,
            )
            .set_footer(
                f"Requested by {context.author.username}{context.author.discriminator}",
                icon=context.author.avatar_url,
            )
            .set_thumbnail(plugin.bot.get_me().avatar_url)
        )
        await context.respond(embed=embed)

    async def send_group_help(self, context, group):
        pass

    async def object_not_found(self, context, obj):
        await context.respond(r"This command was not found /ᐠ۪. ̱ . ۪ᐟ\\ﾉ")


# Loads the plugin into the bot, used for separating commands into different files
def load(bot: lightbulb.BotApp):
    bot.help_command = CustomHelp(bot)
    bot.add_plugin(plugin)

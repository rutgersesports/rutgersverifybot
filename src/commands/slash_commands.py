from collections import defaultdict
from datetime import timedelta

import hikari
import lightbulb
import miru

from src.database.firebase import is_agreement_channel, has_agreement_roles, db
from src.commands.modals import SelectMenu, DeleteMenu, HubMenu

plugin = lightbulb.Plugin("slash_plugin")


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.set_help(
    "Use this command in the channel you wish to make the agreement channel of the server. Please make "
    "sure that users that have just joined the server can type here, so that they can use /agree to get"
    " their roles! You can later remove people's ability to type in the agreement channel using a join"
    " role!",
    docstring=False,
)
@lightbulb.command(
    name="set_agreement_channel",
    description="Sets the agreement channel of the server.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_agreement_channel(ctx: lightbulb.SlashContext) -> None:
    current = (
        db.child("guilds").child(ctx.guild_id).child("agreement_channel").get().val()
    )
    if current == ctx.channel_id:
        await ctx.respond(
            f"{ctx.get_channel().mention} is already the agreement channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    db.child("guilds").child(ctx.guild_id).child("agreement_channel").set(
        ctx.channel_id
    )
    await ctx.respond(
        f"{ctx.get_channel().mention} has been set to {ctx.get_guild().name}'s agreement channel",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.set_help(
    "Use this command in the channel you wish to set as the moderation channel of the server! This will"
    "have the bot send messages about when users delete or edit their messages, including what the old "
    "message used to be.",
    docstring=False,
)
@lightbulb.command(
    name="set_moderation_channel",
    description="Sets the moderation channel of the server.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_moderation_channel(ctx: lightbulb.SlashContext) -> None:
    current = (
        db.child("guilds").child(ctx.guild_id).child("moderation_channel").get().val()
    )
    if current == ctx.channel_id:
        await ctx.respond(
            f"{ctx.get_channel().mention} is already the moderation channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    db.child("guilds").child(ctx.guild_id).child("moderation_channel").set(
        ctx.channel_id
    )
    await ctx.respond(
        f"{ctx.get_channel().mention} has been set to {ctx.get_guild().name}'s moderation channel",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.option(
    name="role3",
    description="The role to add to this server's NetID roles.",
    type=hikari.Role,
    required=False,
)
@lightbulb.option(
    name="role2",
    description="The role to add to this server's NetID roles.",
    type=hikari.Role,
    required=False,
)
@lightbulb.option(
    name="role",
    description="The role to add to this server's NetID roles.",
    type=hikari.Role,
    required=True,
)
@lightbulb.set_help(
    "Use this command to add roles to the guest roles of the server!\n"
    "These do require NetID verification and will be given after a user verifies with Scarletmail.",
    docstring=False,
)
@lightbulb.command(
    name="set_netid_roles", description="Sets the agreement roles that require NetID."
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_netid_roles(ctx: lightbulb.SlashContext) -> None:
    if (
        roles := db.child("guilds").child(ctx.guild_id).child("all_roles").get().val()
    ) is None:
        roles = []
    else:
        roles = roles.values()
    if (
        join_roles := db.child("guilds")
        .child(ctx.guild_id)
        .child("join_roles")
        .get()
        .val()
    ) is None:
        join_roles = []
    else:
        join_roles = join_roles.values()
    possibleRoles = [
        v[1]
        for v in ctx.options.items()
        if v[1] is not None and v[1].id not in roles and v[1].id not in join_roles
    ]
    names = []
    for role in possibleRoles:
        db.child("guilds").child(ctx.guild_id).child("netid_roles").child(
            role.name
        ).set(role.id)
        db.child("guilds").child(ctx.guild_id).child("all_roles").child(role.name).set(
            role.id
        )
        names.append(role.mention)
    final = ", ".join(names)
    response = f'{final} {"has" if len([possibleRoles]) == 1 else "have"} been added to the NetID roles.'

    await ctx.respond(
        f"{response} "
        if possibleRoles != []
        else "All roles already belong to an agreement group.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.option(
    name="role3",
    description="The role to add to this server's guest roles.",
    type=hikari.Role,
    required=False,
)
@lightbulb.option(
    name="role2",
    description="The role to add to this server's guest roles.",
    type=hikari.Role,
    required=False,
)
@lightbulb.option(
    name="role",
    description="The role to add to this server's guest roles.",
    type=hikari.Role,
    required=True,
)
@lightbulb.set_help(
    "Use this command to add roles to the guest roles of the server!\n"
    "These do not require NetID verification and will be given automatically.",
    docstring=False,
)
@lightbulb.command(
    name="set_guest_roles",
    description="Sets the agreement roles that don't require NetID.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_guest_roles(ctx: lightbulb.SlashContext) -> None:
    if (
        roles := db.child("guilds").child(ctx.guild_id).child("all_roles").get().val()
    ) is None:
        roles = []
    else:
        roles = roles.values()
    if (
        join_roles := db.child("guilds")
        .child(ctx.guild_id)
        .child("join_roles")
        .get()
        .val()
    ) is None:
        join_roles = []
    else:
        join_roles = join_roles.values()
    possibleRoles = [
        v[1]
        for v in ctx.options.items()
        if v[1] is not None and v[1].id not in roles and v[1].id not in join_roles
    ]
    names = []
    for role in possibleRoles:
        db.child("guilds").child(ctx.guild_id).child("guest_roles").child(
            role.name
        ).set(role.id)
        db.child("guilds").child(ctx.guild_id).child("all_roles").child(role.name).set(
            role.id
        )
        names.append(role.mention)
    final = ", ".join(names)
    response = f'{final} {"has" if len([possibleRoles]) == 1 else "have"} been added to the guest roles.'

    await ctx.respond(
        f"{response} "
        if possibleRoles != []
        else "All roles already belong to an agreement group.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


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
    all_roles_list = (
        db.child("guilds").child(ctx.guild_id).child("all_roles").get().val()
    )
    netid_roles = (
        db.child("guilds").child(ctx.guild_id).child("netid_roles").get().val()
    )
    if netid_roles is None:
        netid_roles = []
    else:
        netid_roles = netid_roles.keys()
    view = miru.View()
    view.add_item(
        SelectMenu(
            options=[miru.SelectOption(label=k) for k in all_roles_list.keys()][::-1],
            netid_roles=netid_roles,
            all_roles_list=all_roles_list,
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
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.set_help(
    "Use this command to remove either a NetID role, a guest role, or a join role from a server!",
    docstring=False,
)
@lightbulb.command(
    name="delete_agreement_role",
    description="Deletes a role from the server's agreement roles.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def delete_agreement_role(ctx: lightbulb.SlashContext) -> None:
    all_roles_list = (
        db.child("guilds").child(ctx.guild_id).child("all_roles").get().val()
    )
    if (
        join_roles := db.child("guilds")
        .child(ctx.guild_id)
        .child("join_roles")
        .get()
        .val()
    ) is None:
        join_roles = []
    else:
        join_roles = join_roles.keys()
    if all_roles_list is None:
        all_roles_list = []
    else:
        all_roles_list = all_roles_list.keys()
    if all_roles_list == [] and join_roles == []:
        await ctx.respond(
            "There are no agreement roles set for this server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    all_roles_list = list(join_roles) + list(all_roles_list)
    netid_roles = (
        db.child("guilds").child(ctx.guild_id).child("netid_roles").get().val()
    )
    if netid_roles is None:
        netid_roles = []
    else:
        netid_roles = netid_roles.keys()
    view = miru.View()
    view.add_item(
        DeleteMenu(
            options=[miru.SelectOption(label=k) for k in all_roles_list][::-1],
            netid_roles=netid_roles,
            join_roles=join_roles,
        )
    )
    message = await ctx.respond(
        "Select the role to remove:",
        components=view.build(),
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await view.start(message)
    await view.wait()


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.option(
    name="role3",
    description="The role to add to this server's join roles.",
    type=hikari.Role,
    required=False,
)
@lightbulb.option(
    name="role2",
    description="The role to add to this server's join roles.",
    type=hikari.Role,
    required=False,
)
@lightbulb.option(
    name="role",
    description="The role to add to this server's join roles.",
    type=hikari.Role,
    required=True,
)
@lightbulb.set_help(
    "Use this command to add roles to the join roles of the server!\n"
    "These are added after verification and are typically used to change the permissions of a user.",
    docstring=False,
)
@lightbulb.command(
    name="set_join_roles",
    description="Sets the join roles that are added automatically.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_join_roles(ctx: lightbulb.SlashContext) -> None:
    if (
        agreement_roles := db.child("guilds")
        .child(ctx.guild_id)
        .child("all_roles")
        .get()
        .val()
    ) is None:
        agreement_roles = []
    else:
        agreement_roles = agreement_roles.values()
    if (
        roles := db.child("guilds").child(ctx.guild_id).child("join_roles").get().val()
    ) is None:
        roles = []
    else:
        roles = roles.values()
    possibleRoles = [
        v[1]
        for v in ctx.options.items()
        if v[1] is not None and v[1].id not in roles and v[1].id not in agreement_roles
    ]
    names = []
    for role in possibleRoles:
        db.child("guilds").child(ctx.guild_id).child("join_roles").child(role.name).set(
            role.id
        )
        names.append(role.mention)
    final = ", ".join(names)
    response = f'{final} {"has" if len([possibleRoles]) == 1 else "have"} been added to the join roles.'

    await ctx.respond(
        f"{response} "
        if possibleRoles != []
        else "All roles already belong to an agreement group.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


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


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.set_help(
    "Use this command in the channel you want CoolCat to send welcome messages in!",
    docstring=False,
)
@lightbulb.command(
    name="set_welcome_channel",
    description="Sets the welcome channel of this server.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_welcome_channel(ctx: lightbulb.SlashContext):
    current = (
        db.child("guilds").child(ctx.guild_id).child("welcome_channel").get().val()
    )
    if current == ctx.channel_id:
        await ctx.respond(
            f"{ctx.get_channel().mention} is already the welcome channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    db.child("guilds").child(ctx.guild_id).child("welcome_channel").set(ctx.channel_id)
    await ctx.respond(
        f"{ctx.get_channel().mention} has been set to {ctx.get_guild().name}'s welcome channel",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.option(
    name="message",
    description="The message to welcome members with! Use {user} to mention the user!",
    type=str,
    required=True,
)
@lightbulb.set_help(
    'This command will set the welcome message of the server to the "message" param that is passed '
    "in. If you use {user} in the welcome message, it will be replaced with the member's name.",
    docstring=False,
)
@lightbulb.command(
    name="set_welcome_message",
    description="Sets the welcome message of this server.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_welcome_message(ctx: lightbulb.SlashContext):
    current = (
        db.child("guilds").child(ctx.guild_id).child("welcome_channel").get().val()
    )
    if current is None:
        await ctx.respond(
            "There is no welcome channel set! Until one is added, no welcome messages will be sent."
        )
    db.child("guilds").child(ctx.guild_id).child("welcome_message").set(
        ctx.options.message
    )
    await ctx.respond(
        f"{ctx.get_guild().name}'s welcome message has been set!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.option(
    name="status",
    description="Choose the welcome message status",
    type=str,
    required=True,
    choices=["Enabled", "Disabled"],
)
@lightbulb.set_help(
    "Use this command to either entirely enable or disable welcome messages!",
    docstring=False,
)
@lightbulb.command(
    name="welcome_status",
    description="Enables or disabled welcome messages.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def welcome_status(ctx: lightbulb.SlashContext):
    db.child("guilds").child(ctx.guild_id).child("welcome_status").set(
        ctx.options.status
    )
    await ctx.respond(
        f"{ctx.get_guild().name}'s welcome status has been set to [{ctx.options.status}]!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.option(
    name="status",
    description="Choose the welcome message status",
    type=bool,
    required=True,
    choices=[True, False],
)
@lightbulb.set_help(
    "Use this command to allow or deny CoolCat's server invite system!",
    docstring=False,
)
@lightbulb.command(
    name="allow_invites",
    description="Enables or disabled the server hub feature.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def welcome_status(ctx: lightbulb.SlashContext):
    db.child("guilds").child(ctx.guild_id).child("allow_invites").set(
        ctx.options.status
    )
    await ctx.respond(
        f"{ctx.get_guild().name}'s invite status has been set to [{ctx.options.status}]!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


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
    guild_invites = defaultdict()
    for guild in guilds:
        status = db.child("guilds").child(guild.id).child("allow_invites").get().val()
        if status is None:
            db.child("guilds").child(guild.id).child("allow_invites").set(True)
        elif status is False:
            guild_invites[str(guild.id)] = None
            continue
        channel = guild.system_channel_id
        if channel is None:
            channel = guild.rules_channel_id
        if channel is None:
            guild_invites[str(guild.id)] = None
            continue
        try:
            invite = await plugin.bot.rest.create_invite(
                channel, max_uses=1, max_age=timedelta(minutes=5)
            )
        except hikari.HikariError:
            invite = None
        guild_invites[str(guild.id)] = invite
    available_guilds = [
        guild for guild in guilds if guild_invites[str(guild.id)] is not None
    ][::-1]
    if len(available_guilds) is 0:
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
                miru.SelectOption(label=guild.name, value=str(guild.id))
                for guild in available_guilds
            ],
            guilds=guild_invites,
        )
    )
    message = await ctx.respond(
        "Select a server to go to!:",
        components=view.build(),
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await view.start(message)
    await view.wait()


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.MissingRequiredPermission):
        await event.context.respond(
            f"You do not have permissions to use `{event.context.command.name}`.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    elif isinstance(event.exception, lightbulb.CheckFailure):
        await event.context.respond(event.exception, flags=hikari.MessageFlag.EPHEMERAL)


@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_ping(event: hikari.GuildMessageCreateEvent):
    if event.content is None:
        return
    if not event.is_human:
        return
    if plugin.bot.get_me().mention not in event.content:
        return
    await event.message.respond(r"meow /ᐠ۪. ̱ . ۪ᐟ\\ﾉ")


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


def load(bot: lightbulb.BotApp):
    bot.help_command = CustomHelp(bot)
    bot.add_plugin(plugin)

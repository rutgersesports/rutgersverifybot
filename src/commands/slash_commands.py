import hikari
import lightbulb
import miru

from src.database.firebase import is_agreement_channel, has_agreement_roles, db
from src.commands.verify import SelectMenu, DeleteMenu

plugin = lightbulb.Plugin("slash_plugin")


@plugin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD),
    lightbulb.checks.guild_only,
)
@lightbulb.command(
    name="set_agreement_channel",
    description="Sets the agreement channel of the server.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_agreement_channel(ctx: lightbulb.SlashContext) -> None:
    current = (
        db.child("guilds")
        .child(ctx.guild_id)
        .child("agreement_channel")
        .get(ctx.channel_id)
        .val()
    )
    if current == ctx.channel_id:
        await ctx.respond(
            f"{ctx.get_channel().mention} is already the agreement channel."
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
@lightbulb.command(
    name="set_moderation_channel",
    description="Sets the moderation channel of the server.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_moderation_channel(ctx: lightbulb.SlashContext) -> None:
    current = (
        db.child("guilds")
        .child(ctx.guild_id)
        .child("moderation_channel")
        .get(ctx.channel_id)
        .val()
    )
    if current == ctx.channel_id:
        await ctx.respond(
            f"{ctx.get_channel().mention} is already the moderation channel."
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
    possibleRoles = [
        v[1] for v in ctx.options.items() if v[1] is not None and v[1].id not in roles
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
    possibleRoles = [
        v[1] for v in ctx.options.items() if v[1] is not None and v[1].id not in roles
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
@lightbulb.command(
    name="delete_agreement_role",
    description="Deletes a role from the server's agreement roles.",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def delete_agreement_role(ctx: lightbulb.SlashContext) -> None:
    all_roles_list = (
        db.child("guilds").child(ctx.guild_id).child("all_roles").get().val()
    )
    if all_roles_list is None:
        await ctx.respond(
            "There are no agreement roles set for this server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    else:
        all_roles_list = all_roles_list.keys()
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
        )
    )
    message = await ctx.respond(
        "Select the role to remove:",
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


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)

import hikari
import lightbulb
import src.database.firebase as fb

plugin = lightbulb.Plugin("moderation_plugin")
plugin.add_checks(
    lightbulb.Check(fb.has_moderation_channel),
    lightbulb.checks.bot_has_channel_permissions(hikari.Permissions.VIEW_CHANNEL),
)


@plugin.listener(hikari.GuildMessageUpdateEvent)
async def message_edit(event: hikari.GuildMessageUpdateEvent) -> None:
    if isinstance(event.author, hikari.UndefinedType):
        return
    if (old := event.old_message) is None:
        old = "This message is too old to track. - CoolCat"
    if event.author.is_bot:
        return
    try:
        moderation_channel = plugin.bot.guilds[event.guild_id]["moderation_channel"]
    except KeyError:
        return
    if not moderation_channel:
        return
    user = event.member or plugin.bot.cache.get_member(event.guild_id, event.author_id)
    embed = (
        hikari.Embed(
            title="Message has been edited by:",
            description=f"<@{user.id}>\n\n"
            f"**Old message content:**\n{old.content}\n"
            f"\n**New message content:**\n{event.message.content}\n\n"
            f"**In channel:**\n"
            f"{event.get_channel().mention}",
            timestamp=event.message.edited_timestamp,
            color=0xFCD203,
        )
        .set_thumbnail(event.author.avatar_url)
        .set_footer(text=(me := plugin.bot.get_me()).username, icon=me.avatar_url)
    )
    await plugin.bot.rest.create_message(
        moderation_channel, embed=embed, attachments=event.message.attachments
    )


@plugin.listener(hikari.GuildMessageDeleteEvent)
async def message_delete(event: hikari.GuildMessageDeleteEvent):
    try:
        moderation_channel = plugin.bot.guilds[event.guild_id]["moderation_channel"]
    except KeyError:
        return
    except TypeError:
        return
    if not moderation_channel:
        return
    if (message := event.old_message) is None:
        # await plugin.bot.rest.create_message(
        #     moderation_channel,
        #     "A message was deleted, but it was sent too long ago to track",
        # )
        return
    if message.author.is_bot:
        return
    user = event.old_message.member or plugin.bot.cache.get_member(
        event.guild_id, event.old_message.author.id
    )
    guild = event.get_guild()
    if not guild:
        return
    if guild.owner_id == user.id:
        return
    else:
        guild_roles = guild.get_roles()
        member_roles = list(
            filter(lambda r: r.id in user.role_ids, guild_roles.values())
        )
        permissions: hikari.Permissions = guild_roles[
            guild.id
        ].permissions  # Start with @everyone perms

        for role in member_roles:
            permissions |= role.permissions
    if permissions & hikari.Permissions.ADMINISTRATOR:
        return
    if permissions & hikari.Permissions.MANAGE_GUILD == hikari.Permissions.MANAGE_GUILD:
        return

    embed = (
        hikari.Embed(
            title="A message has been deleted! It was written by:",
            description=f"<@{user.id}>\n\n"
            f"**Deleted message content:**\n{message.content}\n"
            f"\n**In channel:**\n"
            f"{event.get_channel().mention}",
            timestamp=message.timestamp,
            color=0xD9133C,
        )
        .set_thumbnail(event.old_message.author.avatar_url)
        .set_footer(text=(me := plugin.bot.get_me()).username, icon=me.avatar_url)
    )
    await plugin.bot.rest.create_message(
        moderation_channel, embed=embed, attachments=event.old_message.attachments
    )


@plugin.listener(hikari.GuildMessageCreateEvent)
async def agreement_channel_delete(event: hikari.GuildMessageCreateEvent):
    if not event.is_human:
        return
    try:
        agreement_channel = plugin.bot.guilds[event.guild_id]["agreement_channel"]
    except KeyError:
        return
    except TypeError:
        return
    if agreement_channel is None:
        return
    if not event.channel_id == agreement_channel:
        return
    if (
        not lightbulb.utils.permissions.permissions_for(event.member)
        & hikari.Permissions.MANAGE_GUILD
        == hikari.Permissions.MANAGE_GUILD
    ):
        await event.message.delete()


@plugin.listener(hikari.MemberCreateEvent)
async def welcome_message_send(event: hikari.MemberCreateEvent):
    try:
        db_guild = plugin.bot.guilds[event.guild_id]
    except KeyError:
        return
    try:
        status = db_guild["welcome_status"]
    except KeyError:
        plugin.bot.db.child("guilds").child(event.guild_id).child("welcome_status").set(
            "Enabled"
        )
        db_guild["welcome_status"] = "Enabled"
        status = "Enabled"
    if status == "Disabled":
        return
    try:
        channel = db_guild["welcome_channel"]
    except KeyError:
        return
    try:
        message = db_guild["welcome_message"]
    except KeyError:
        return
    if message is None:
        return
    user = event.member or plugin.bot.cache.get_member(event.guild_id, event.user_id)
    await plugin.bot.rest.create_message(
        channel,
        message.replace("{user}", f"<@{user.id}>").replace(
            "{name}", f"{user.display_name}"
        ),
    )


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)

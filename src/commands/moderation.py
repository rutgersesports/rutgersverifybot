import hikari
import lightbulb
from src.database import firebase as fb

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
    moderation_channel = (
        fb.db.child("guilds")
        .child(event.guild_id)
        .child("moderation_channel")
        .get()
        .val()
    )
    if moderation_channel is None:
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
    moderation_channel = (
        fb.db.child("guilds")
        .child(event.guild_id)
        .child("moderation_channel")
        .get()
        .val()
    )
    if moderation_channel is None:
        return
    if (message := event.old_message) is None:
        # await plugin.bot.rest.create_message(
        #     moderation_channel,
        #     "A message was deleted, but it was sent too long ago to track",
        # )
        return
    if message.author.is_bot:
        return
    user = event.old_message.author or plugin.bot.cache.get_member(
        event.guild_id, event.old_message.author.id
    )
    embed = (
        hikari.Embed(
            title="Message has been deleted by:",
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
    agreement_channel = (
        fb.db.child("guilds")
        .child(event.guild_id)
        .child("agreement_channel")
        .get()
        .val()
    )
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
    db_guild = fb.db.child("guilds").child(event.guild_id).get().val()
    try:
        status = db_guild["welcome_status"]
    except KeyError:
        fb.db.child("guilds").child(event.guild_id).child("welcome_status").set(
            "Enabled"
        )
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
        channel, message.replace("{user}", f"<@{user.id}>")
    )


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)

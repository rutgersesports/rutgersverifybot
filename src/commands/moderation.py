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
    embed = (
        hikari.Embed(
            title="Message has been edited by:",
            description=f"{event.author.mention}\n\n"
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
    await plugin.bot.rest.create_message(moderation_channel, embed=embed, attachments=event.message.attachments)


@plugin.listener(hikari.GuildMessageDeleteEvent)
async def message_delete(event: hikari.GuildMessageDeleteEvent):
    moderation_channel = (
        fb.db.child("guilds")
        .child(event.guild_id)
        .child("moderation_channel")
        .get()
        .val()
    )
    if (message := event.old_message) is None:
        await plugin.bot.rest.create_message(
            moderation_channel,
            "A message was deleted, but it was sent too long ago to track",
        )
        return
    if message.author.is_bot:
        return
    deleter = message.author
    embed = (
        hikari.Embed(
            title="Message has been deleted by:",
            description=f"{deleter.mention}\n\n"
            f"**Deleted message content:**\n{message.content}\n"
            f"\n**In channel:**\n"
            f"{event.get_channel().mention}",
            timestamp=message.timestamp,
            color=0xD9133C,

        )
        .set_thumbnail(deleter.avatar_url)
        .set_footer(text=(me := plugin.bot.get_me()).username, icon=me.avatar_url)
    )
    await plugin.bot.rest.create_message(moderation_channel, embed=embed, attachments=event.old_message.attachments)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)

import asyncio
import os

from random import randrange
import dotenv
import hikari
import src.database.Firebase as fb
from src.database.Firebase import db

dotenv.load_dotenv()
bot = hikari.GatewayBot(token=os.getenv("token"), intents=hikari.Intents.ALL)


@bot.listen()
async def setAgreementChannel(event: hikari.GuildMessageCreateEvent):
    if not event.content == f"{await fb.getPrefix(event.guild_id)}setAgreementChannel":
        return
    roles = await event.member.fetch_roles()
    permissions = hikari.Permissions.NONE
    for role in roles:
        permissions |= role.permissions
    if not await checkPerms(event.member, event.get_guild()):
        await event.get_channel().send(
            "You do not have the necessary permissions to do this."
        )
        return
    db.child("guilds").child(f"{event.guild_id}").child("agreementChannel").set(
        event.channel_id
    )
    await event.get_channel().send(
        f"{event.get_channel().name} has been set to {event.get_guild().name}'s agreement channel"
    )


@bot.listen()
async def setAgreementRoles(event: hikari.GuildMessageCreateEvent):
    if f"{await fb.getPrefix(event.guild_id)}setNetIDRoles" not in event.content:
        return
    if not await checkPerms(event.member, event.get_guild()):
        await event.get_channel().send(
            "You do not have the necessary permissions to do this."
        )
        return
    if event.content == f"{await fb.getPrefix(event.guild_id)}setNetIDRoles":
        await event.get_channel().send(
            "Please ping the role you'd like to add to the list."
        )
        return
    else:
        try:
            currentRoles = (
                db.child("guilds")
                .child(f"{event.guild_id}")
                .child("NetIDRoles")
                .get()
                .val()
                .values()
            )
        except AttributeError:
            db.child("guilds").child(f"{event.guild_id}").update({"NetIDRoles": []})
            currentRoles = (
                db.child("guilds").child(f"{event.guild_id}").child("NetIDRoles").get()
            )
        roleMentions = [
            event.get_guild().get_role(int(id))
            for id in event.message.role_mention_ids
            if db.child("guilds")
            .child(f"{event.guild_id}")
            .child("NetIDRoles")
            .get()
            .val()
            is None
            or int(id)
            not in db.child("guilds")
            .child(f"{event.guild_id}")
            .child("NetIDRoles")
            .get()
            .val()
            .values()
        ]
        for v in roleMentions:
            db.child("guilds").child(f"{event.guild_id}").child("NetIDRoles").push(v.id)
        if not roleMentions:
            await event.get_channel().send(
                "All mentioned roles are already NetID roles"
            )
            return
        await event.get_channel().send(
            f"{[v.name for v in roleMentions]} has been added to {event.get_guild().name}'s NetID roles."
        )


async def checkPerms(mem: hikari.Member, server: hikari.Guild) -> bool:
    roles = await mem.fetch_roles()
    permissions = hikari.Permissions.NONE
    for role in roles:
        permissions |= role.permissions
    if (
        not permissions & hikari.Permissions.MANAGE_GUILD
        == hikari.Permissions.MANAGE_GUILD
        and not await server.fetch_owner() == mem
    ):
        return False
    return True


# Split into separate commands files for ease of access soon
# @bot.listen()
# async def count(event: hikari.GuildMessageCreateEvent) -> None:
#     if not event.is_human:
#         return
#     await fb.place_msg(event)


# @bot.listen()
# async def join(event: hikari.MemberCreateEvent) -> None:
#     if event.user.is_bot:
#         return
#     print("here")
#     await verification(event.user)


async def verification(event: hikari.GuildMessageCreateEvent):
    u = event.member
    agreementRoles = fb.getAgreementRoles(event.guild_id)
    try:
        roles = agreementRoles.val().values()
    except AttributeError:
        await u.send(
            "This server has not set up its agreement roles yet. Please inform an admin for help."
        )
        return
    await fb.checkEmptyOrMia(u.id)
    if not db.child("users").child(f"{u.id}").child("verified").get().val():
        await u.send(
            f"Please enter the name of the role you want to add. Roles are: {roles}"
        )
        try:
            AccType = await bot.wait_for(
                hikari.DMMessageCreateEvent,
                timeout=300,
                predicate=lambda e: e.author_id == u.id
                and (
                    e.content == "Rutgers Student"
                    or e.content == "Alumni"
                    or e.content == "Guest"
                ),
            )
            if AccType.content == "Guest":
                await u.send("fill")
            else:
                await u.send("Enter your NetID")
            netid = await bot.wait_for(
                hikari.DMMessageCreateEvent,
                # How long to wait for
                timeout=300,
                # The event only matches if this returns True
                predicate=lambda e: (
                    (
                        db.child("netIDs").get().val() is None
                        or e.content.lower()
                        not in db.child("netIDs").get().val().values()
                    )
                    and e.author_id == u.id
                    and e.content.isalnum()
                    and len(e.content) < 10
                )
                or e.content == os.getenv("skipcode"),
            )

            await u.send(
                "You are not verified, please check your email for the verification code"
            )
            if netid.content != os.getenv("skipcode"):
                await fb.sendEmail(netid)
            else:
                await u.send(
                    db.child("users").child(f"{u.id}").child("ver_code").get().val()
                )
            await bot.wait_for(
                hikari.DMMessageCreateEvent,
                # How long to wait for
                timeout=300,
                # The event only matches if this returns True
                predicate=lambda e: e.author_id == u.id
                and e.content.isdigit()
                and len(e.content) == 6
                and fb.checkVercode(int(e.content), e.author_id),
            )
            await u.send("You are now verified! Have fun :)")
            db.child("users").child(f"{u.id}").update(
                {"netID": f"{netid.content.lower()}"}
            )
            db.child("netIDs").push(f"{netid.content.lower()}")
        except asyncio.TimeoutError:
            await u.send(
                'Your session has timed out. Please respond "Retry" to retry the verification process.'
            )
    else:
        await u.send("You are already verified! Have fun :)")


# @bot.listen()
# async def retryVerification(event: hikari.DMMessageCreateEvent):
#     if not event.is_human:
#         return None
#     if event.content.lower() == "retry":
#         db.child("users").child(f"{event.author_id}").child("ver_code").set(
#             random.randrange(100000, 999999)
#         )
#         await verification(event.author)


@bot.listen()
async def botJoin(event: hikari.GuildJoinEvent):
    db.child("guilds").child(f"{event.guild_id}").child("prefix").set("!")


@bot.listen()
async def userAgree(event: hikari.GuildMessageCreateEvent):
    gID = event.guild_id
    prefix = await fb.getPrefix(gID)
    if not event.content == f"{prefix}agree":
        return

    if (
        agreementChannel := db.child("guilds")
        .child(f"{gID}")
        .child("agreementChannel")
        .get()
        .val()
    ) is None:
        await event.get_channel().send(
            "There is no agreement channel configured for this server. Please configure "
            f"this to be an agreement channel using {prefix}setAgreementChannel"
        )
        return

    elif event.channel_id != agreementChannel:
        await event.get_channel().send(
            "This is not the agreement channel. If you think it is an error, please ask an "
            f"admin to reconfigure it using {prefix}setAgreementChannel"
        )
        return
    try:
        await event.author.send("Hello!")
    except hikari.ForbiddenError:
        await event.get_channel().send(
            "There was an error sending you a DM! Please check your DM settings in the "
            "Privacy & Security tab"
        )
        with open("src/environ/PrivacySetting.png", "rb") as image:
            f = image.read()
            b = bytearray(f)
        await event.get_channel().send(hikari.Bytes(b, "PrivacySetting.png"))
    else:
        db.child("users").child(f"{event.author_id}").child("ver_code").set(
            randrange(100000, 999999)
        )
        await verification(event)

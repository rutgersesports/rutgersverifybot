# from random import randrange
# import hikari
# import src.database.firebase as fb
# from src.database.firebase import db
# import lightbulb
# import src.commands.actions as actions
#
# plugin = lightbulb.Plugin("prefix_plugin")
#
#
# @plugin.listener(hikari.GuildMessageCreateEvent)
# async def set_agreement_roles(event: hikari.GuildMessageCreateEvent):
#     if not event.content == f"{await fb.get_prefix(event.guild_id)}set_agreement_roles":
#         return
#     roles = await event.member.fetch_roles()
#     permissions = hikari.Permissions.NONE
#     for role in roles:
#         permissions |= role.permissions
#     if not await actions.check_perms(event.member, event.get_guild()):
#         await event.get_channel().send(
#             "You do not have the necessary permissions to do this."
#         )
#         return
#     db.child("guilds").child(f"{event.guild_id}").child("agreementChannel").set(
#         event.channel_id
#     )
#     await event.get_channel().send(
#         f"{event.get_channel().name} has been set to {event.get_guild().name}'s agreement channel"
#     )
#
#
# @plugin.listener(hikari.GuildMessageCreateEvent)
# async def setAgreementRoles(event: hikari.GuildMessageCreateEvent):
#     if f"{await fb.get_prefix(event.guild_id)}set_netid_roles" not in event.content:
#         return
#     if not await actions.check_perms(event.member, event.get_guild()):
#         await event.get_channel().send(
#             "You do not have the necessary permissions to do this."
#         )
#         return
#     if event.content == f"{await fb.get_prefix(event.guild_id)}set_netid_roles":
#         await event.get_channel().send(
#             "Please ping the role you'd like to add to the list."
#         )
#         return
#     else:
#         try:
#             (
#                 db.child("guilds")
#                 .child(f"{event.guild_id}")
#                 .child("NetIDRoles")
#                 .get()
#                 .val()
#                 .values()
#             )
#         except AttributeError:
#             db.child("guilds").child(f"{event.guild_id}").update({"NetIDRoles": []})
#             (
#                 db.child("guilds").child(f"{event.guild_id}").child("NetIDRoles").get()
#             )
#         roleMentions = [
#             event.get_guild().get_role(int(role_id))
#             for role_id in event.message.role_mention_ids
#             if db.child("guilds")
#             .child(f"{event.guild_id}")
#             .child("NetIDRoles")
#             .get()
#             .val()
#             is None
#             or int(role_id)
#             not in db.child("guilds")
#             .child(f"{event.guild_id}")
#             .child("NetIDRoles")
#             .get()
#             .val()
#             .values()
#         ]
#         for v in roleMentions:
#             db.child("guilds").child(f"{event.guild_id}").child("NetIDRoles").child(
#                 f"{v.name}"
#             ).set(v.id)
#         if not roleMentions:
#             await event.get_channel().send(
#                 "All mentioned roles are already NetID roles"
#             )
#             return
#         await event.get_channel().send(
#             f"{', '.join([v.name for v in roleMentions])} has been added to {event.get_guild().name}'s NetID roles."
#         )
#
#
# # Split into separate commands files for ease of access soon
# # @bot.listen()
# # async def count(event: hikari.GuildMessageCreateEvent) -> None:
# #     if not event.is_human:
# #         return
# #     await fb.place_msg(event)
#
#
# # @bot.listen()
# # async def join(event: hikari.MemberCreateEvent) -> None:
# #     if event.user.is_bot:
# #         return
# #     print("here")
# #     await verification(event.user)
#
#
# # @bot.listen()
# # async def retryVerification(event: hikari.DMMessageCreateEvent):
# #     if not event.is_human:
# #         return None
# #     if event.content.lower() == "retry":
# #         db.child("users").child(f"{event.author_id}").child("ver_code").set(
# #             random.randrange(100000, 999999)
# #         )
# #         await verification(event.author)
#
#
# @plugin.listener(hikari.GuildJoinEvent)
# async def botJoin(event: hikari.GuildJoinEvent):
#     db.child("guilds").child(f"{event.guild_id}").child("prefix").set("!")
#
#
# @plugin.listener(hikari.GuildMessageCreateEvent)
# async def userAgree(event: hikari.GuildMessageCreateEvent):
#     gID = event.guild_id
#     prefix = await fb.get_prefix(gID)
#     if not event.content == f"{prefix}agree":
#         return
#
#     if (
#         agreementChannel := db.child("guilds")
#         .child(f"{gID}")
#         .child("agreementChannel")
#         .get()
#         .val()
#     ) is None:
#         await event.get_channel().send(
#             "There is no agreement channel configured for this server. Please configure "
#             f"this to be an agreement channel using {prefix}set_agreement_roles"
#         )
#         return
#
#     elif event.channel_id != agreementChannel:
#         await event.get_channel().send(
#             "This is not the agreement channel. If you think it is an error, please ask an "
#             f"admin to reconfigure it using {prefix}set_agreement_roles"
#         )
#         return
#     try:
#         await event.author.send("Hello!")
#     except hikari.ForbiddenError:
#         await event.get_channel().send(
#             "There was an error sending you a DM! Please check your DM settings in the "
#             "Privacy & Security tab"
#         )
#         # with open("privacy_setting.png", "rb") as image:
#         #     f = image.read()
#         #     b = bytearray(f)
#         # await event.get_channel().send(hikari.Bytes(b, "privacy_setting.png"))
#         # image.close()
#     else:
#         db.child("users").child(f"{event.author_id}").child("ver_code").set(
#             randrange(100000, 999999)
#         )
#         await actions.verification(event, plugin)
#
#
# def load(bot: lightbulb.BotApp):
#     bot.add_plugin(plugin)

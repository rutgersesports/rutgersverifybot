# import hikari
# from random import randrange
#
# from src.database.Firebase import db, getPrefix
# from Commands import bot, verification
#
#
# @bot.listen()
# async def userAgree(event: hikari.GuildMessageCreateEvent):
#     gID = event.guild_id
#     prefix = await getPrefix(gID)
#     if not event.content == f'{prefix}agree':
#         return
#
#     if (agreementChannel := db.child('guilds').child(f'{gID}').child('agreementChannel').get().val()) is None:
#         await event.get_channel().send("There is no agreement channel configured for this server. Please configure "
#                                        f"this to be an agreement channel using {prefix}setAgreementChannel")
#         return
#
#     elif event.channel_id != agreementChannel:
#         await event.get_channel().send("This is not the agreement channel. If you think it is an error, please ask an "
#                                        f"admin to reconfigure it using {prefix}setAgreementChannel")
#         return
#     try:
#         await event.author.send("Hello!")
#     except hikari.ForbiddenError:
#         await event.get_channel().send("There was an error sending you a DM! Please check your DM settings in the "
#                                        "Privacy & Security tab")
#         with open("src/environ/PrivacySetting.png", "rb") as image:
#             f = image.read()
#             b = bytearray(f)
#         await event.get_channel().send(hikari.Bytes(b, "PrivacySetting.png"))
#     else:
#         db.child("users").child(f"{event.author_id}").child("ver_code").set(
#                          randrange(100000, 999999))
#         await verification(event)

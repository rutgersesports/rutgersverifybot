# import asyncio
# import os
#
# import hikari
# import lightbulb
#
# import src.database.firebase as fb
# from src.database.firebase import db
#
#
# async def verification(event: hikari.GuildMessageCreateEvent, plugin: lightbulb.Plugin):
#     u = event.member
#     agreement_roles = fb.get_agreement_roles(event.guild_id)
#     try:
#         roles = [v for v in agreement_roles.val()]
#     except AttributeError:
#         await u.send(
#             "This server has not set up its agreement roles yet. Please inform an admin for help."
#         )
#         return
#     await fb.check_empty_or_mia(u.id)
#     if not db.child("users").child(f"{u.id}").child("verified").get().val():
#         await u.send(
#             f"Please enter the name of the role you want to add. Roles are: {', '.join(roles)}"
#         )
#         try:
#             AccType = await plugin.bot.wait_for(
#                 hikari.DMMessageCreateEvent,
#                 timeout=300,
#                 predicate=lambda e: e.author_id == u.id
#                 and (
#                     e.content == "Rutgers Student"
#                     or e.content == "Alumni"
#                     or e.content == "Guest"
#                 ),
#             )
#             if AccType.content == "Guest":
#                 await u.send("fill")
#             else:
#                 await u.send("Enter your NetID")
#             netid = await plugin.bot.wait_for(
#                 hikari.DMMessageCreateEvent,
#                 # How long to wait for
#                 timeout=300,
#                 # The event only matches if this returns True
#                 predicate=lambda e: (
#                     (
#                         db.child("netIDs").get().val() is None
#                         or e.content.lower()
#                         not in db.child("netIDs").get().val().values()
#                     )
#                     and e.author_id == u.id
#                     and e.content.isalnum()
#                     and len(e.content) < 10
#                 )
#                 or e.content == os.getenv("skipcode"),
#             )
#
#             await u.send(
#                 "You are not verified, please check your email for the verification code"
#             )
#             if netid.content != os.getenv("skipcode"):
#                 await fb.send_email(netid)
#             else:
#                 await u.send(
#                     db.child("users").child(f"{u.id}").child("ver_code").get().val()
#                 )
#             await plugin.bot.wait_for(
#                 hikari.DMMessageCreateEvent,
#                 # How long to wait for
#                 timeout=300,
#                 # The event only matches if this returns True
#                 predicate=lambda e: e.author_id == u.id
#                 and e.content.isdigit()
#                 and len(e.content) == 6
#                 and fb.check_vercode(int(e.content), e.author_id),
#             )
#             await u.send("You are now verified! Have fun :)")
#             db.child("users").child(f"{u.id}").update(
#                 {"netID": f"{netid.content.lower()}"}
#             )
#             db.child("netIDs").push(f"{netid.content.lower()}")
#         except asyncio.TimeoutError:
#             await u.send(
#                 "Your session has timed out. Please retry the verification process."
#             )
#     else:
#         await u.send("You are already verified! Have fun :)")
#
#
# async def check_perms(mem: hikari.Member, server: hikari.Guild) -> bool:
#     roles = await mem.fetch_roles()
#     permissions = hikari.Permissions.NONE
#     for role in roles:
#         permissions |= role.permissions
#     return not (
#         not permissions & hikari.Permissions.MANAGE_GUILD
#         == hikari.Permissions.MANAGE_GUILD
#         and not await server.fetch_owner() == mem
#     )

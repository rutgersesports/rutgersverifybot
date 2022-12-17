# # Function to keep track of message chains
# @plugin.listener(hikari.GuildMessageCreateEvent)
# async def track_message_chain(event: hikari.GuildMessageCreateEvent):
#     # Get the guild ID, channel ID, user ID and message content
#     guild_id = event.guild_id
#     channel_id = event.channel_id
#     author = event.author_id
#     content = event.message_id
#
#
#
#     # Declare variables
#     usersInChain =  db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('usersInChain').get()
#     prevmsg = db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('previous_message').get().val()
#     counter = 0
#
#     # If db does not have preivous meesage recorded AND no user is in the chain, record it to db
#     if db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('previous_message') is None \
#             and len(db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('usersInChain')) == 0:
#
#         db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('usersInChain').push(author)
#         db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('previous_message').set(
#             content)
#         counter += 1
#
#     # CASE COVERING THE START OF A CHAIN. If the current content matches the previous message, and the user who sent
#     # the message is in NOT the chain user list, start the chain if the counter is <= 2.
#     elif db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('previous_message') == content \
#             and author not in db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child(
#         'usersInChain') and \
#             counter <= 2:
#
#         usersInChain.push(author)
#
#         # Add number 1 emoji to previous message
#
#         setting = f'U0000003{counter}'
#         setting = (f"\{setting}\U0000FE0F\U000020E3")
#
#         await prevmsg.add_reaction(setting.encode('raw-unicode-escape').decode('unicode-escape'))
#
#         # Add number 2 moji to current message
#         await plugin.bot.cache.get_message(content).add_reaction(setting.encode('raw-unicode-escape').decode('unicode-escape'))
#
#     # CASE COVERING CONTINUATION OF A CHAIN SIZE LESS THAN 10. If the current content matches the previous message,
#     # and the user who sent the message is in NOT the chain user list, add a reaction if counter is under two digits.
#     elif db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('previous_message') == content \
#             and author not in db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child(
#         'usersInChain') and \
#             2 < counter < 10:
#
#         usersInChain.push(author)
#
#         setting = f'U0000003{counter}'
#         setting = (f"\{setting}\U0000FE0F\U000020E3")
#
#         await plugin.bot.cache.get_message(content).add_reaction(setting.encode('raw-unicode-escape').decode('unicode-escape'))
#         counter += 1
#
#     # CASE COVERING CONTINUATION OF A CHAIN SIZE GREATER THAN 10 If the current content matches the previous message,
#     # and the user who sent the message is in NOT the chain user list Split the digits of the chain counter into
#     # isolated number per digit, and add reaction of those respective digits in order.
#     elif db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('previous_message') == content \
#             and author not in db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child(
#         'usersInChain') and \
#             counter >= 10:
#
#         usersInChain.push(author)
#
#         digits = [(counter // (10 ** i)) % 10 for i in range(math.ceil(math.log(counter, 10)), -1, -1)][
#                  bool(math.log(counter, 10) % 1):]
#
#         if fb.is_duplicate(digits):
#
#             await plugin.bot.cache.get_message(content).add_reaction("\U0001F522")
#             counter += 1
#         else:
#             for x in digits:
#                 setting = f'U0000003{x}'
#                 setting = f"\{setting}\U0000FE0F\U000020E3"
#
#                 await plugin.bot.cache.get_message(content).add_reaction(setting.encode('raw-unicode-escape').decode('unicode-escape'))
#                 counter += 1
#
#     # BREAK THE CHAIN, RESET ALL COUNTERS!!
#     else:
#         counter = 0
#
#         db.child('guilds').child(f'{guild_id}').child('channels').child(channel_id).child('usersInChain').set([])
#
#         await plugin.bot.cache.get_message(content).add_reaction("\U0001F621")


# async def is_duplicate(anylist):
#     if type(anylist) != 'list':
#         return "Error. Passed parameter is Not a list"
#     if len(anylist) != len(set(anylist)):
#         return True
#     else:
#         return False

# async def place_msg(event: hikari.GuildMessageCreateEvent):
#     if not event.is_human:
#         return
#     await checkEmptyOrMia(event.author_id)
#     # try:
#     msg_count = (
#         db.child("users").child(f"{event.author_id}").child("msg_count").get().val()
#     )
#     db.child("users").child(f"{event.author_id}").update({"msg_count": msg_count + 1})
#     msg_count += 1

# BUGGED AND CANNOT FIX, PYREBASE ISSUE
# except TypeError:
#     db.update({"msg_count": 1})
#     # db.update({"msg_count": 0})
#     msg_count = (
#         db.child("users").child(f"{event.author_id}").child("msg_count").get().val()
#     )
# db.child("users").child(f"{event.author_id}").child("msgs").child(
#     f'key{msg_count}').set(event.content)

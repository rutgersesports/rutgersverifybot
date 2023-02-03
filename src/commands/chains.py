import hikari
import lightbulb

plugin = lightbulb.Plugin("chains_plugin")
chain_dict = {
    "0": "0️⃣",
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
    "5": "5️⃣",
    "6": "6️⃣",
    "7": "7️⃣",
    "8": "8️⃣",
    "9": "9️⃣",
}


@plugin.listener(hikari.GuildMessageCreateEvent)
async def chains(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human:
        return
    try:
        db_chain = plugin.bot.guilds[event.guild_id]["chains"]
    except KeyError:
        plugin.bot.guilds[event.guild_id]["chains"] = {}
        db_chain = plugin.bot.guilds[event.guild_id]["chains"]
    try:
        allow_chains = db_chain["allow_chains"]
    except KeyError:
        db_chain["allow_chains"] = False
        allow_chains = False
    if not allow_chains:
        return
    try:
        channel = db_chain[event.channel_id]
    except KeyError:
        channel = {}
        db_chain[event.channel_id] = channel
    try:
        message = channel["message"]
    except KeyError:
        try:
            chain_num = len(channel["users"])
        except KeyError as e:
            chain_num = 1
        channel["message"] = event.message.content
        channel["users"] = [event.author_id]
        plugin.bot.db.child("guilds").child(event.guild_id).child("chains").set(
            db_chain
        )
        if chain_num > 1:
            await event.message.add_reaction("😾")
        return
    if message != event.message.content:
        try:
            chain_num = len(channel["users"])
        except KeyError:
            chain_num = 1
        channel["message"] = event.message.content
        channel["users"] = [event.author_id]
        plugin.bot.db.child("guilds").child(event.guild_id).child("chains").set(
            db_chain
        )
        if chain_num > 1:
            await event.message.add_reaction("😾")
        return
    if event.author_id in channel["users"]:
        try:
            chain_num = len(channel["users"])
        except KeyError:
            chain_num = 1
        channel["message"] = event.message.content
        channel["users"] = [event.author_id]
        plugin.bot.db.child("guilds").child(event.guild_id).child("chains").set(
            db_chain
        )
        if chain_num > 1:
            await event.message.add_reaction("😾")
        return
    chain_num = len(channel["users"])
    channel["users"].append(event.author_id)
    plugin.bot.db.child("guilds").child(event.guild_id).child("chains").set(db_chain)
    if chain_num > 100:
        await event.message.add_reaction("💯")
        chain_num -= 100
    if not chain_num:
        return
    if not chain_num % 11:
        await event.message.add_reaction("🔢")
        return
    for char in str(chain_num):
        await event.message.add_reaction(chain_dict[char])


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)

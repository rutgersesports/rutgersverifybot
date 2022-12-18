from src import bot

# @bot.listen() async def botJoinServer(event: hikari.GuildJoinEvent) -> None: overwrite =
# hikari.PermissionOverwrite( id=event.guild_id, type=hikari.PermissionOverwriteType.MEMBER,
# allow=( hikari.Permissions.NONE ), ) channel = await event.guild.create_news_channel(name="CoolCatConfig",
# position=0, topic="This channel with both serve as config and updates for the " "CoolCat Bot ",
# permission_overwrites=overwrite) db.db.child('guilds').child(f'{event.guild_id}').child('updates').set(f'{
# channel.id}') await channel.send("src")


def main():
    bot.run()


if __name__ == "__main__":
    main()

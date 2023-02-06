import json
from os import getenv, name as osname
import hikari
import miru
import dotenv
import pyrebase
import lightbulb


class NewBot(lightbulb.BotApp):
    def __init__(self) -> None:
        self.guilds = {}
        self.users = {}
        self.verified_netids = {}
        dotenv.load_dotenv()
        self.db = pyrebase.initialize_app(
            {
                "apiKey": getenv("apiKey"),
                "authDomain": getenv("authDomain"),
                "databaseURL": getenv("databaseURL"),
                "projectId": getenv("projectId"),
                "storageBucket": getenv("storageBucket"),
                "messagingSenderId": getenv("messagingSenderId"),
                "appId": getenv("appId"),
                "measurementId": getenv("measurementId"),
                "serviceAccount": json.loads(getenv("auth")),
            }
        ).database()
        super().__init__(
            getenv("token"),
            intents=hikari.Intents.ALL,
            help_slash_command=True,
            cache_settings=hikari.impl.CacheSettings(
                max_messages=1000, components=hikari.api.CacheComponents.ALL
            ),
        )

    def run(self, *args, **kwargs) -> None:
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        # self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        # self.event_manager.subscribe(hikari.ShardConnectedEvent, self.on_connected)
        # self.event_manager.subscribe(hikari.ShardDisconnectedEvent, self.on_disconnected)

        if osname != "nt":
            import uvloop

            uvloop.install()
        miru.install(self)
        super().run(
            activity=hikari.Activity(
                name="the air guitar championship",
                type=hikari.ActivityType.COMPETING,
            ),
            # asyncio_debug=True,
            # coroutine_tracking_depth=20,
        )

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        print("Connecting to Firebase")
        # await self.db.connect()
        print("Connected to Firebase")
        self.load_extensions(
            "src.commands.moderation",
            "src.commands.slash_commands",
            "src.commands.chains",
        )

    async def on_started(self, _: hikari.StartedEvent) -> None:
        for guild in await self.rest.fetch_my_guilds():
            self.guilds[guild.id] = self.db.child("guilds").child(guild.id).get().val()
            if not self.guilds[guild.id]:
                self.guilds[guild.id] = {}
        self.users = self.db.child("users").get().val()
        self.verified_netids = self.db.child("verified_netids").get().val()
        if not self.users:
            self.users = {}
        if not self.verified_netids:
            self.verified_netids = {}

import asyncio
import re

import hikari
import miru
from src.commands import menu_commands as mc


class MainMenu(miru.View):
    def __init__(self, author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(CloseMenu(author))
        self.author = author

    @miru.select(
        placeholder="Choose a setting to configure:",
        options=[
            miru.SelectOption(
                label="Agreement Config",
                description="Configure agreement roles and channels",
            ),
            miru.SelectOption(
                label="Welcome Config",
                description="Create and set custom welcome messages",
            ),
            miru.SelectOption(
                label="Moderation Config",
                description="Configure moderation channel settings",
            ),
        ],
    )
    async def select_config(self, select: miru.Select, ctx: miru.Context) -> None:
        if ctx.author != self.author:
            return
        match select.values[0]:
            case "Agreement Config":
                embed = self.message.embeds[0]
                embed.description = (
                    "Set up your agreement roles, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                embed.title = "CoolCat Agreement Configuration"
                embed.color = 0xF8B195
                view = AgreementMenu(self.author, timeout=600)
                message = await ctx.edit_response(
                    content=None, embed=embed, components=view.build()
                )
                await view.start(message)
            case "Welcome Config":
                embed = self.message.embeds[0]
                embed.description = (
                    "Set up your welcome messages, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                embed.title = "CoolCat Welcome Configuration"
                embed.color = 0xF67280
                view = WelcomeMenu(self.author, timeout=600)
                message = await ctx.edit_response(
                    content=None, embed=embed, components=view.build()
                )
                await view.start(message)
            case "Moderation Config":
                embed = self.message.embeds[0]
                embed.description = (
                    "Set up your moderation channel and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                embed.title = "CoolCat Moderation Configuration"
                embed.color = 0xC06C84
                view = ModerationMenu(self.author, timeout=600)
                message = await ctx.edit_response(
                    content=None, embed=embed, components=view.build()
                )
                await view.start(message)


class ModerationMenu(miru.View):
    def __init__(self, author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(MainMenuButton(author))
        self.add_item(CloseMenu(author))
        self.author = author

    @miru.select(
        placeholder="Moderation Settings",
        options=[
            miru.SelectOption(
                label="Enable/Disable CoolCat Server invites",
                description="Turn off CoolCat's built-in server hub feature",
            ),
            miru.SelectOption(
                label="Set Moderation Channel",
                description="Set the channel that CoolCat sends chat logs in",
            ),
            miru.SelectOption(
                label="Enable/Disable chains",
                description="Allow CoolCat to count 'chained messages' in chat",
            ),
        ],
    )
    async def moderation_channel(self, select: miru.Select, ctx: miru.Context) -> None:
        if ctx.author != self.author:
            return
        embed = self.message.embeds[0]
        match select.values[0]:
            case "Enable/Disable CoolCat Server invites":
                self.add_item(EnableHubButton(self.author))
                self.add_item(DisableHubButton(self.author))
                self.add_item(ModerationMenuButton(self.author))
                embed.description = (
                    "Opt in or out of CoolCat's server hub\nr" r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                await ctx.edit_response(content=None, embed=embed, components=self[1:])
            case "Set Moderation Channel":
                self.add_item(ModerationMenuButton(self.author))
                embed.description = (
                    "Ping the channel you'd like to make the Moderation channel!\n"
                    "This is where you'll see edited messages, deleted messages, "
                    "as well as kick/ban notes"
                )
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
                try:
                    event = await ctx.bot.event_manager.wait_for(
                        hikari.GuildMessageCreateEvent,
                        # How long to wait for
                        timeout=60,
                        # The event only matches if this returns True
                        predicate=lambda e: e.message.author == ctx.author
                        and bool(re.search("^<#([0-9]+)>[ \t]*$", e.message.content)),
                    )
                except asyncio.CancelledError:
                    return
                except asyncio.TimeoutError:
                    return
                try:
                    channel = await ctx.bot.rest.fetch_channel(
                        int(re.sub("[^0-9+]", "", event.message.content))
                    )
                except hikari.BadRequestError:
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                except hikari.NotFoundError:
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                await event.message.delete()
                if not isinstance(
                    channel,
                    hikari.GuildTextChannel,
                ):
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                ctx.bot.guilds[ctx.guild_id]["moderation_channel"] = channel.id
                ctx.bot.db.child("guilds").child(ctx.guild_id).child(
                    "moderation_channel"
                ).set(channel.id)
                self.stop()
                view = ModerationMenu(self.author, timeout=600)
                embed.description = (
                    "Set up your moderation channel and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                message = await ctx.edit_response(
                    f"{channel.mention} has been set to this server's moderation channel",
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)
            case "Enable/Disable chains":
                self.add_item(EnableChainButton(self.author))
                self.add_item(DisableChainButton(self.author))
                self.add_item(ModerationMenuButton(self.author))
                embed.description = (
                    "Enable CoolCat's chain counting in chat\nr" r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                await ctx.edit_response(content=None, embed=embed, components=self[1:])


class AgreementMenu(miru.View):
    def __init__(self, author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(MainMenuButton(author))
        self.add_item(CloseMenu(author))
        self.author = author

    @miru.select(
        placeholder="Agreement Settings",
        options=[
            miru.SelectOption(
                label="Add NetID Roles",
                description="Add agreement roles that require NetID verification",
            ),
            miru.SelectOption(
                label="Add Guest Roles",
                description="Configure agreement roles that don't require NetID verification",
            ),
            miru.SelectOption(
                label="Add Join Roles",
                description="Configure agreement roles given automatically after verification",
            ),
            miru.SelectOption(
                label="Set Agreement Channel",
                description="Set the channel you want users to agree in",
            ),
            miru.SelectOption(
                label="Remove NetID Roles",
                description="Remove existing roles from the server's NetID roles",
            ),
            miru.SelectOption(
                label="Remove Guest Roles",
                description="Remove existing roles from the server's NetID roles",
            ),
            miru.SelectOption(
                label="Remove Join Roles",
                description="Remove existing roles from the server's NetID roles",
            ),
        ],
    )
    async def agreement_channel(self, select: miru.Select, ctx: miru.Context) -> None:
        if ctx.author != self.author:
            return
        embed = self.message.embeds[0]
        match select.values[0]:
            case "Remove NetID Roles":
                try:
                    db_guild = ctx.bot.guilds[ctx.guild_id]
                except KeyError:
                    return
                if not db_guild:
                    return
                try:
                    netid_roles = db_guild["netid_roles"]
                except KeyError:
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "There are no NetID roles to remove", components=view.build()
                    )
                    await view.start(message)
                    return
                self.stop()
                view = miru.View()
                view.add_item(
                    RolesView(
                        options=[
                            miru.SelectOption(label=name) for name in netid_roles.keys()
                        ],
                        roles_dict=netid_roles,
                        result_function=mc.remove_netid_role,
                        author=self.author,
                    )
                )
                view.add_item(MainMenuButton(self.author))
                view.add_item(CloseMenu(self.author))
                view.add_item(AgreementMenuButton(self.author))
                embed.description = "Select the role to remove:"
                message = await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)
                await view.wait()

            case "Remove Guest Roles":
                try:
                    db_guild = ctx.bot.guilds[ctx.guild_id]
                except KeyError:
                    return
                if not db_guild:
                    return
                try:
                    guest_roles = db_guild["guest_roles"]
                except KeyError:
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "There are no Guest roles to remove", components=view.build()
                    )
                    await view.start(message)
                    return
                self.stop()
                view = miru.View()
                view.add_item(
                    RolesView(
                        options=[
                            miru.SelectOption(label=name) for name in guest_roles.keys()
                        ],
                        roles_dict=guest_roles,
                        result_function=mc.remove_guest_role,
                        author=self.author,
                    )
                )
                view.add_item(MainMenuButton(self.author))
                view.add_item(CloseMenu(self.author))
                view.add_item(AgreementMenuButton(self.author))
                embed.description = "Select the role to remove:"
                message = await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)
                await view.wait()

            case "Remove Join Roles":
                try:
                    db_guild = ctx.bot.guilds[ctx.guild_id]
                except KeyError:
                    return
                if not db_guild:
                    return
                try:
                    join_roles = db_guild["join_roles"]
                except KeyError:
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "There are no Join roles to remove", components=view.build()
                    )
                    await view.start(message)
                    return
                self.stop()
                view = miru.View()
                view.add_item(
                    RolesView(
                        options=[
                            miru.SelectOption(label=name) for name in join_roles.keys()
                        ],
                        roles_dict=join_roles,
                        result_function=mc.remove_join_role,
                        author=self.author,
                    )
                )
                view.add_item(MainMenuButton(self.author))
                view.add_item(CloseMenu(self.author))
                view.add_item(AgreementMenuButton(self.author))
                embed.description = "Select the role to remove:"
                message = await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)

            case "Add NetID Roles":
                self.add_item(AgreementMenuButton(self.author))
                embed.description = (
                    "Ping the roles you'd like to add to add to the NetID Roles"
                )
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
                try:
                    event = await ctx.bot.event_manager.wait_for(
                        hikari.GuildMessageCreateEvent,
                        # How long to wait for
                        timeout=60,
                        # The event only matches if this returns True
                        predicate=lambda e: e.message.author == ctx.author
                        and e.message.role_mention_ids,
                    )
                except asyncio.TimeoutError:
                    return
                except asyncio.CancelledError:
                    return
                roles = event.message.get_role_mentions()
                await event.message.delete()
                try:
                    db_guild = ctx.bot.guilds[ctx.guild_id]
                except KeyError:
                    db_guild = {}
                if not db_guild:
                    db_guild = {}
                try:
                    agreement_roles = db_guild["all_roles"]
                except KeyError:
                    agreement_roles = {}
                try:
                    join_roles = db_guild["join_roles"]
                except KeyError:
                    join_roles = {}
                possibleRoles = [
                    role
                    for role in roles.values()
                    if role is not None
                    and role.id not in agreement_roles.values()
                    and role.id not in join_roles.values()
                ]
                names = []
                try:
                    netid_roles = db_guild["netid_roles"]
                except KeyError:
                    netid_roles = {}
                for role in possibleRoles:
                    agreement_roles[role.name] = role.id
                    netid_roles[role.name] = role.id
                    names.append(role.mention)
                ctx.bot.guilds[ctx.guild_id]["netid_roles"] = netid_roles
                ctx.bot.guilds[ctx.guild_id]["all_roles"] = agreement_roles
                ctx.bot.db.child("guilds").child(ctx.guild_id).child("netid_roles").set(
                    netid_roles
                )
                ctx.bot.db.child("guilds").child(ctx.guild_id).child("all_roles").set(
                    agreement_roles
                )
                final = ", ".join(names)
                response = f'{final} {"has" if len([possibleRoles]) == 1 else "have"} been added to the NetID roles.'

                self.stop()
                view = AgreementMenu(self.author, timeout=600)
                embed.description = (
                    "Set up your agreement roles, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                message = await ctx.edit_response(
                    f"{response} "
                    if possibleRoles != []
                    else "All roles already belong to an agreement group.",
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)

            case "Add Guest Roles":
                self.add_item(AgreementMenuButton(self.author))
                embed.description = (
                    "Ping the roles you'd like to add to add to the Guest Roles"
                )
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
                try:
                    event = await ctx.bot.event_manager.wait_for(
                        hikari.GuildMessageCreateEvent,
                        # How long to wait for
                        timeout=60,
                        # The event only matches if this returns True
                        predicate=lambda e: e.message.author == ctx.author
                        and e.message.role_mention_ids,
                    )
                except asyncio.CancelledError:
                    return
                except asyncio.TimeoutError:
                    return
                roles = event.message.get_role_mentions()
                await event.message.delete()
                try:
                    db_guild = ctx.bot.guilds[ctx.guild_id]
                except KeyError:
                    db_guild = {}
                if not db_guild:
                    db_guild = {}
                try:
                    agreement_roles = db_guild["all_roles"]
                except KeyError:
                    agreement_roles = {}
                try:
                    join_roles = db_guild["join_roles"]
                except KeyError:
                    join_roles = {}
                possibleRoles = [
                    role
                    for role in roles.values()
                    if role is not None
                    and role.id not in agreement_roles.values()
                    and role.id not in join_roles.values()
                ]
                names = []
                try:
                    guest_roles = db_guild["guest_roles"]
                except KeyError:
                    guest_roles = {}
                for role in possibleRoles:
                    agreement_roles[role.name] = role.id
                    guest_roles[role.name] = role.id
                    names.append(role.mention)
                    ctx.bot.guilds[ctx.guild_id]["guest_roles"] = guest_roles
                    ctx.bot.guilds[ctx.guild_id]["all_roles"] = agreement_roles
                ctx.bot.db.child("guilds").child(ctx.guild_id).child("guest_roles").set(
                    guest_roles
                )
                ctx.bot.db.child("guilds").child(ctx.guild_id).child("all_roles").set(
                    agreement_roles
                )
                final = ", ".join(names)
                response = f'{final} {"has" if len([possibleRoles]) == 1 else "have"} been added to the Guest roles.'

                self.stop()
                view = AgreementMenu(self.author, timeout=600)
                embed.description = (
                    "Set up your agreement roles, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                message = await ctx.edit_response(
                    f"{response} "
                    if possibleRoles != []
                    else "All roles already belong to an agreement group.",
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)

            case "Add Join Roles":
                self.add_item(AgreementMenuButton(self.author))
                embed.description = (
                    "Ping the roles you'd like to add to add to the Join Roles"
                )
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
                try:
                    event = await ctx.bot.event_manager.wait_for(
                        hikari.GuildMessageCreateEvent,
                        # How long to wait for
                        timeout=60,
                        # The event only matches if this returns True
                        predicate=lambda e: e.message.author == ctx.author
                        and e.message.role_mention_ids,
                    )
                except asyncio.CancelledError:
                    return
                except asyncio.TimeoutError:
                    return
                roles = event.message.get_role_mentions()
                await event.message.delete()
                try:
                    db_guild = ctx.bot.guilds[ctx.guild_id]
                except KeyError:
                    db_guild = {}
                if not db_guild:
                    db_guild = {}
                try:
                    agreement_roles = db_guild["all_roles"]
                except KeyError:
                    agreement_roles = {}
                try:
                    join_roles = db_guild["join_roles"]
                except KeyError:
                    join_roles = {}
                possibleRoles = [
                    role
                    for role in roles.values()
                    if role is not None
                    and role.id not in agreement_roles.values()
                    and role.id not in join_roles.values()
                ]
                names = []
                for role in possibleRoles:
                    join_roles[role.name] = role.id
                    names.append(role.mention)
                ctx.bot.guilds[ctx.guild_id]["join_roles"] = join_roles
                ctx.bot.db.child("guilds").child(ctx.guild_id).child("join_roles").set(
                    join_roles
                )
                final = ", ".join(names)
                response = f'{final} {"has" if len([possibleRoles]) == 1 else "have"} been added to the Join roles.'

                self.stop()
                view = AgreementMenu(self.author, timeout=600)
                embed.description = (
                    "Set up your agreement roles, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                message = await ctx.edit_response(
                    f"{response} "
                    if possibleRoles != []
                    else "All roles already belong to an agreement group.",
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)

            case "Set Agreement Channel":
                self.add_item(AgreementMenuButton(self.author))
                embed.description = (
                    "Ping the channel you'd like to make the agreement channel!\n"
                    "Please make sure people can type and use slash commands in it.\n"
                )
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
                try:
                    event = await ctx.bot.event_manager.wait_for(
                        hikari.GuildMessageCreateEvent,
                        # How long to wait for
                        timeout=60,
                        # The event only matches if this returns True
                        predicate=lambda e: e.message.author == ctx.author
                        and bool(re.search("^<#([0-9]+)>[ \t]*$", e.message.content)),
                    )
                except asyncio.CancelledError:
                    return
                except asyncio.TimeoutError:
                    return
                try:
                    channel = await ctx.bot.rest.fetch_channel(
                        int(re.sub("[^0-9+]", "", event.message.content))
                    )
                except hikari.BadRequestError:
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                except hikari.NotFoundError:
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                await event.message.delete()
                if not isinstance(
                    channel,
                    hikari.GuildTextChannel,
                ):
                    view = AgreementMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                ctx.bot.guilds[ctx.guild_id]["agreement_channel"] = channel.id
                ctx.bot.db.child("guilds").child(ctx.guild_id).child(
                    "agreement_channel"
                ).set(channel.id)
                self.stop()
                view = AgreementMenu(self.author, timeout=600)
                embed.description = (
                    "Set up your agreement roles, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                message = await ctx.edit_response(
                    f"{channel.mention} has been set to this server's agreement channel",
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)


class RolesView(miru.Select):
    def __init__(
        self, roles_dict: dict, result_function, author, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.roles_dict = roles_dict
        self.result_function = result_function
        self.author = author

    async def callback(self, ctx: miru.Context) -> None:
        if ctx.author != self.author:
            return
        embed = self.view.message.embeds[0]
        await self.result_function(ctx, self.values[0])
        roles = self.roles_dict
        if not roles:
            self.view.stop()
            view = AgreementMenu(self.author, timeout=600)
            message = await ctx.edit_response(
                "There are no roles here to remove", components=view.build()
            )
            await view.start(message)
            return
        self.view.stop()
        roles.pop(self.values[0])
        response = (
            f"{self.values[0]} has been removed from this server's agreement roles"
        )
        if not roles:
            view = AgreementMenu(self.author, timeout=600)
            embed = hikari.Embed(
                title="CoolCat Welcome Configuration",
                description="Set up your welcome messages, channels, and settings here!\n"
                r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
                color=0xF67280,
            )
            message = await ctx.edit_response(
                content=response, embed=embed, components=view.build()
            )
            await view.start(message)
            return
        view = miru.View()
        view.add_item(
            RolesView(
                options=[miru.SelectOption(label=name) for name in roles.keys()],
                roles_dict=roles,
                result_function=self.result_function,
                author=self.author,
            )
        )
        view.add_item(MainMenuButton(self.author))
        view.add_item(CloseMenu(self.author))
        view.add_item(AgreementMenuButton(self.author))
        embed.description = "Select the role to remove:"
        message = await ctx.edit_response(
            content=response,
            embed=embed,
            components=view.build(),
        )
        await view.start(message)
        await view.wait()


class WelcomeMenu(miru.View):
    def __init__(self, author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(MainMenuButton(author))
        self.add_item(CloseMenu(author))
        self.author = author

    @miru.select(
        placeholder="Welcome Channel Setup",
        options=[
            miru.SelectOption(
                label="Enable/Disable Welcome Messages",
                description="Turn on or off custom welcome messages when members join",
            ),
            miru.SelectOption(
                label="Set Welcome Channel",
                description="Set the channel that the custom welcome messages are sent in",
            ),
            miru.SelectOption(
                label="Set Welcome Message",
                description="Set the welcome message the bot will say when members join",
            ),
        ],
    )
    async def welcome_channel(self, select: miru.Select, ctx: miru.Context) -> None:
        if ctx.author != self.author:
            return
        embed = self.message.embeds[0]
        match select.values[0]:
            case "Enable/Disable Welcome Messages":
                self.add_item(EnableButton(self.author))
                self.add_item(DisableButton(self.author))
                self.add_item(WelcomeMenuButton(self.author))
                embed.description = "Enable or disable this server's welcome messages"
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
            case "Set Welcome Channel":
                self.add_item(WelcomeMenuButton(self.author))
                embed.description = (
                    "Ping the channel you'd like to make the welcome channel!"
                )
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
                try:
                    event = await ctx.bot.event_manager.wait_for(
                        hikari.GuildMessageCreateEvent,
                        # How long to wait for
                        timeout=60,
                        # The event only matches if this returns True
                        predicate=lambda e: e.message.author == ctx.author
                        and bool(re.search("^<#([0-9]+)>[ \t]*$", e.message.content)),
                    )
                except asyncio.CancelledError:
                    return
                except asyncio.TimeoutError:
                    return
                try:
                    channel = await ctx.bot.rest.fetch_channel(
                        int(re.sub("[^0-9+]", "", event.message.content))
                    )
                except hikari.BadRequestError:
                    view = WelcomeMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                except hikari.NotFoundError:
                    view = WelcomeMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                await event.message.delete()
                if not isinstance(
                    channel,
                    hikari.GuildTextChannel,
                ):
                    view = WelcomeMenu(self.author, timeout=600)
                    message = await ctx.edit_response(
                        "Please make sure this channel is a text channel",
                        components=view.build(),
                    )
                    await view.start(message)
                    return
                ctx.bot.guilds[ctx.guild_id]["welcome_channel"] = channel.id
                ctx.bot.db.child("guilds").child(ctx.guild_id).child(
                    "welcome_channel"
                ).set(channel.id)
                self.stop()
                view = WelcomeMenu(self.author, timeout=600)
                embed.description = (
                    "Set up your welcome messages, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ"
                )
                message = await ctx.edit_response(
                    content=f"{channel.mention} has been set to this server's welcome channel",
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)
            case "Set Welcome Message":
                self.add_item(WelcomeMenuButton(self.author))
                embed.description = (
                    "Type the welcome message you'd like new members to see!\n"
                    "Use {user} to use the user's mention\n"
                    "Use {name} to use the user's name as text, as there is a bug with pinging at the moment"
                )
                await ctx.edit_response(
                    content=None,
                    embed=embed,
                    components=self[1:],
                )
                try:
                    event = await ctx.bot.event_manager.wait_for(
                        hikari.GuildMessageCreateEvent,
                        # How long to wait for
                        timeout=60,
                        # The event only matches if this returns True
                        predicate=lambda e: e.message.author == ctx.author
                        and e.message.content,
                    )
                except asyncio.CancelledError:
                    return
                except asyncio.TimeoutError:
                    return
                ctx.bot.guilds[ctx.guild_id]["welcome_message"] = event.message.content
                ctx.bot.db.child("guilds").child(ctx.guild_id).child(
                    "welcome_message"
                ).set(event.message.content)
                await event.message.delete()
                self.stop()
                view = WelcomeMenu(self.author, timeout=600)
                embed = hikari.Embed(
                    title="CoolCat Welcome Configuration",
                    description="Set up your welcome messages, channels, and settings here!\n"
                    r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
                    color=0xF67280,
                )
                message = await ctx.edit_response(
                    content=f"{ctx.get_guild().name}'s welcome message has been set!",
                    embed=embed,
                    components=view.build(),
                )
                await view.start(message)


class AgreementMenuButton(miru.Button):
    def __init__(self, author):
        super().__init__(
            emoji="↩️",
            style=hikari.ButtonStyle.SECONDARY,
        )
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        self.view.stop()
        view = AgreementMenu(self.author, timeout=600)
        embed = hikari.Embed(
            title="CoolCat Agreement Configuration",
            description="Set up your agreement roles, channels, and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xF8B195,
        )
        message = await ctx.edit_response(
            content=None, embed=embed, components=view.build()
        )
        await view.start(message)


class WelcomeMenuButton(miru.Button):
    def __init__(self, author):
        super().__init__(
            emoji="↩️",
            style=hikari.ButtonStyle.SECONDARY,
        )
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        self.view.stop()
        embed = hikari.Embed(
            title="CoolCat Welcome Configuration",
            description="Set up your welcome messages, channels, and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xF67280,
        )
        view = WelcomeMenu(self.author, timeout=600)
        message = await ctx.edit_response(
            content=None, embed=embed, components=view.build()
        )
        await view.start(message)


class ModerationMenuButton(miru.Button):
    def __init__(self, author):
        super().__init__(
            emoji="↩️",
            style=hikari.ButtonStyle.SECONDARY,
        )
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        self.view.stop()
        embed = hikari.Embed(
            title="CoolCat moderation Configuration",
            description="Set up your moderation channel and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xC06C84,
        )
        view = ModerationMenu(self.author, timeout=600)
        message = await ctx.edit_response(
            content=None, embed=embed, components=view.build()
        )
        await view.start(message)


class CloseMenu(miru.Button):
    def __init__(self, author):
        super().__init__(label="Close Menu", style=hikari.ButtonStyle.DANGER)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        await ctx.message.delete()
        await ctx.respond(
            "Config Menu has been closed",
            components=[],
            embeds=[],
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        self.view.stop()


class MainMenuButton(miru.Button):
    def __init__(self, author):
        super().__init__(label="Main Menu", style=hikari.ButtonStyle.SECONDARY)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        self.view.stop()
        me = await ctx.bot.rest.fetch_user(193736005239439360)
        view = MainMenu(author=ctx.author, timeout=600)
        embed = (
            hikari.Embed(
                title="CoolCat Configuration Menu",
                description="Configure your CoolCat server settings here!\n"
                r"If there are any issues, contact me for help /ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
                color=0xFFFFFF,
            )
            .set_thumbnail(ctx.bot.get_me().avatar_url)
            .set_footer(
                text=f"Created by {me.username}#{me.discriminator}", icon=me.avatar_url
            )
        )
        message = await ctx.edit_response(
            content=None, embed=embed, components=view.build()
        )
        await view.start(message)


class EnableButton(miru.Button):
    def __init__(self, author):
        super().__init__(label="Enable", style=hikari.ButtonStyle.SUCCESS)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        ctx.bot.guilds[ctx.guild_id]["welcome_status"] = "Enabled"
        ctx.bot.db.child("guilds").child(ctx.guild_id).child("welcome_status").set(
            "Enabled"
        )
        self.view.stop()
        view = WelcomeMenu(self.author, timeout=600)
        embed = hikari.Embed(
            title="CoolCat Welcome Configuration",
            description="Set up your welcome messages, channels, and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xF67280,
        )
        message = await ctx.edit_response(
            f"{ctx.get_guild().name}'s welcome messages have been enabled!",
            embed=embed,
            components=view.build(),
        )
        await view.start(message)


class DisableButton(miru.Button):
    def __init__(self, author):
        super().__init__(label="Disable", style=hikari.ButtonStyle.DANGER)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        ctx.bot.guilds[ctx.guild_id]["welcome_status"] = "Disabled"
        ctx.bot.db.child("guilds").child(ctx.guild_id).child("welcome_status").set(
            "Disabled"
        )
        self.view.stop()
        embed = hikari.Embed(
            title="CoolCat Welcome Configuration",
            description="Set up your welcome messages, channels, and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xF67280,
        )
        view = WelcomeMenu(self.author, timeout=600)
        message = await ctx.edit_response(
            f"{ctx.get_guild().name}'s welcome messages have been disabled!",
            embed=embed,
            components=view.build(),
        )
        await view.start(message)


class EnableHubButton(miru.Button):
    def __init__(self, author):
        super().__init__(label="Enable", style=hikari.ButtonStyle.SUCCESS)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        ctx.bot.guilds[ctx.guild_id]["allow_invites"] = True
        ctx.bot.db.child("guilds").child(ctx.guild_id).child("allow_invites").set(True)
        self.view.stop()
        view = ModerationMenu(self.author, timeout=600)
        embed = hikari.Embed(
            title="CoolCat moderation Configuration",
            description="Set up your moderation channel and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xC06C84,
        )
        message = await ctx.edit_response(
            f"{ctx.get_guild().name} has opted into CoolCat's server hub",
            embed=embed,
            components=view.build(),
        )
        await view.start(message)


class DisableHubButton(miru.Button):
    def __init__(self, author):
        super().__init__(label="Disable", style=hikari.ButtonStyle.DANGER)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        ctx.bot.guilds[ctx.guild_id]["allow_invites"] = False
        ctx.bot.db.child("guilds").child(ctx.guild_id).child("allow_invites").set(False)
        self.view.stop()
        embed = hikari.Embed(
            title="CoolCat moderation Configuration",
            description="Set up your moderation channel and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xC06C84,
        )
        view = ModerationMenu(self.author, timeout=600)
        message = await ctx.edit_response(
            f"{ctx.get_guild().name} has opted out of CoolCat's server hub",
            embed=embed,
            components=view.build(),
        )
        await view.start(message)


class EnableChainButton(miru.Button):
    def __init__(self, author):
        super().__init__(label="Enable", style=hikari.ButtonStyle.SUCCESS)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        try:
            ctx.bot.guilds[ctx.guild_id]["chains"]["allow_chains"] = True
        except KeyError:
            ctx.bot.guilds[ctx.guild_id]["chains"] = {}
            ctx.bot.guilds[ctx.guild_id]["chains"]["allow_chains"] = True
        ctx.bot.db.child("guilds").child(ctx.guild_id).child("chains").child(
            "allow_chains"
        ).set(True)
        self.view.stop()
        view = ModerationMenu(self.author, timeout=600)
        embed = hikari.Embed(
            title="CoolCat moderation Configuration",
            description="Set up your moderation channel and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xC06C84,
        )
        message = await ctx.edit_response(
            f"{ctx.get_guild().name} has enabled CoolCat's chain feature",
            embed=embed,
            components=view.build(),
        )
        await view.start(message)


class DisableChainButton(miru.Button):
    def __init__(self, author):
        super().__init__(label="Disable", style=hikari.ButtonStyle.DANGER)
        self.author = author

    async def callback(self, ctx: miru.ViewContext) -> None:
        if ctx.author != self.author:
            return
        try:
            ctx.bot.guilds[ctx.guild_id]["chains"]["allow_chains"] = False
        except KeyError:
            ctx.bot.guilds[ctx.guild_id]["chains"] = {}
            ctx.bot.guilds[ctx.guild_id]["chains"]["allow_chains"] = False
        ctx.bot.db.child("guilds").child(ctx.guild_id).child("chains").child(
            "allow_chains"
        ).set(False)
        self.view.stop()
        embed = hikari.Embed(
            title="CoolCat moderation Configuration",
            description="Set up your moderation channel and settings here!\n"
            r"/ᐠ۪. ̱ . ۪ᐟ\\ﾉ",
            color=0xC06C84,
        )
        view = ModerationMenu(self.author, timeout=600)
        message = await ctx.edit_response(
            f"{ctx.get_guild().name} has disabled CoolCat's chain feature",
            embed=embed,
            components=view.build(),
        )
        await view.start(message)

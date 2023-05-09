from datetime import timedelta

import hikari
import miru
from src.database import firebase as fb


class HubMenu(miru.Select):
    def __init__(self, guilds, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.guilds = guilds

    async def callback(self, ctx: miru.Context) -> None:
        try:
            guild = self.guilds[int(self.values[0])]
            channel = guild.system_channel_id
            if channel is None:
                channel = guild.rules_channel_id
            if channel is None:
                invite = None
            else:
                try:
                    invite = await ctx.bot.rest.create_invite(
                        channel, max_uses=1, max_age=timedelta(minutes=5)
                    )
                except hikari.HikariError:
                    invite = None
            if invite is None:
                await ctx.edit_response(
                    "This server doesn't allow CoolCat to make invites.", components=[]
                )
                self.view.stop()
                return
            await ctx.edit_response(
                f"Here is an invite to {self.options[0].label}!\n" f"{invite}",
                components=[],
            )
        except hikari.ForbiddenError:
            await ctx.edit_response(
                "This server doesn't allow CoolCat to make invites.", components=[]
            )
        except Exception as e:
            print(repr(e))
            await ctx.edit_response("This should never happen", components=[])
        self.view.stop()


class SelectMenu(miru.Select):
    def __init__(self, db_guild, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db_guild = db_guild

    async def callback(self, ctx: miru.Context) -> None:
        try:
            user = ctx.bot.users[ctx.user.id]
        except KeyError:
            ctx.bot.users[ctx.user.id] = {}
            user = ctx.bot.users[ctx.user.id]
        try:
            if self.values[0] in self.db_guild["guest_roles"]:
                await ctx.edit_response(
                    "You have been verified for a guest role! Have a good time!",
                    components=[],
                )
                user["verification"] = "guest"
                ctx.bot.db.child("users").child(ctx.user.id).child("verification").set(
                    "guest"
                )
                roles_to_del = set((all_roles := self.db_guild["all_roles"].values()))
                role_to_add = all_roles.mapping.get(self.values[0])
                user_roles = set(await ctx.member.fetch_roles())
                final_roles = [
                    role.id for role in user_roles if role.id not in roles_to_del
                ]
                final_roles.append(role_to_add)
                await ctx.member.edit(roles=final_roles)
                self.view.stop()
                await add_join_roles(ctx.bot, ctx.guild_id, ctx.user, self.db_guild)
                return
        except KeyError:
            pass
        try:
            netid = user["netid"]
        except KeyError:
            view = ModalView(self.values[0], self.db_guild)
            message = await ctx.edit_response(
                "Please verify your Net ID below:",
                flags=hikari.MessageFlag.EPHEMERAL,
                components=view,
            )
            await view.start(message)
            return
        except TypeError:
            view = ModalView(self.values[0], self.db_guild)
            message = await ctx.edit_response(
                "Please verify your Net ID below:",
                flags=hikari.MessageFlag.EPHEMERAL,
                components=view,
            )
            await view.start(message)
            return
        await add_netid_role(
            ctx, self.values[0], netid, self.db_guild["all_roles"], True
        )
        self.view.stop()
        await add_join_roles(ctx.bot, ctx.guild_id, ctx.user, self.db_guild)


class ModalView(miru.View):
    def __init__(self, role, db_guild, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.db_guild = db_guild

    @miru.button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, _: miru.Button, ctx: miru.ViewContext) -> None:
        modal = FirstModal(
            title="NetID verification:",
            role=self.role,
            db_guild=self.db_guild,
        )
        await ctx.respond_with_modal(modal)


class FirstModal(miru.Modal):
    def __init__(self, role, db_guild, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.db_guild = db_guild

    netid = miru.TextInput(label="NetID", placeholder="Type your NetID!", required=True)

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        if not (
            self.netid.value.isalnum()
            and not self.netid.value.isdigit()
            and not self.netid.value.isalpha()
        ):
            await ctx.edit_response(
                "Please make sure you're only inputting your NetID!\n"
                "Make sure to use your NetID, not your RutgersID."
            )
        elif not await fb.test_netid(self.bot, self.netid.value.casefold()):
            await ctx.edit_response(
                "This NetID has already been verified. Please try again."
            )
        else:
            view = VercodeView(
                role=self.role,
                netid=self.netid.value.casefold(),
                db_guild=self.db_guild,
            )
            message = await ctx.edit_response(
                "Please check your Rutgers email for the verification code!",
                components=view,
            )
            await view.start(message)
            await fb.send_email(self.bot, self.netid.value, ctx.author.id)


class VercodeView(miru.View):
    def __init__(self, role, db_guild, netid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.netid = netid
        self.db_guild = db_guild

    @miru.button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, _: miru.Button, ctx: miru.ViewContext) -> None:
        modal = SecondModal(
            title="Verification code:",
            role=self.role,
            netid=self.netid,
            db_guild=self.db_guild,
        )
        await ctx.respond_with_modal(modal)


class SecondModal(miru.Modal):
    def __init__(self, role, netid, db_guild, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.netid = netid
        self.db_guild = db_guild

    ver_code = miru.TextInput(
        label="Verification code",
        placeholder="Check your email for the verification code!",
        required=True,
    )

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        if not self.ver_code.value.isdigit():
            await ctx.edit_response("Please make sure you're only inputting digits!")
        elif ctx.bot.users[ctx.user.id]["ver_code"] == int(self.ver_code.value):
            await add_netid_role(
                ctx, self.role, self.netid, self.db_guild["all_roles"], False
            )
            self.stop()
            await add_join_roles(ctx.bot, ctx.guild_id, ctx.user, self.db_guild)
        else:
            await ctx.edit_response(
                "That is not correct! Please try again, or grab a different role."
            )


async def add_netid_role(ctx, role: str, netid: str, all_roles_list, exists: bool):
    await ctx.edit_response(
        "You have been verified for a NetID role! Have a good time!",
        components=[],
    )
    ctx.bot.users[ctx.user.id]["verification"] = "netid"
    ctx.bot.db.child("users").child(ctx.user.id).child("verification").set("netid")
    if netid is not None:
        ctx.bot.users[ctx.user.id]["netid"] = netid
        ctx.bot.db.child("users").child(ctx.user.id).child("netid").set(netid)
    if not exists:
        ctx.bot.db.child("verified_netids").push(netid)
    roles_to_del = set((all_roles := all_roles_list.values()))
    role_to_add = all_roles.mapping.get(role)
    user_roles = set(await ctx.member.fetch_roles())
    final_roles = [role.id for role in user_roles if role.id not in roles_to_del]
    final_roles.append(role_to_add)
    await ctx.member.edit(roles=final_roles)


async def add_join_roles(
    bot: miru.MiruAware, guild_id: int, user: hikari.User, db_guild
):
    try:
        join_roles = db_guild["join_roles"]
    except KeyError:
        return
    if not join_roles:
        return
    for role in join_roles.values():
        await bot.rest.add_role_to_member(guild_id, user, role)

import hikari
import miru
import src.database.firebase as fb


class SelectMenu(miru.Select):
    def __init__(self, netid_roles, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.netid_roles = netid_roles

    async def callback(self, ctx: miru.Context) -> None:
        if self.values[0] not in self.netid_roles:
            await ctx.edit_response(
                "You have been verified for a guest role! Have a good time!",
                components=[],
            )
            fb.db.child("users").child(ctx.user.id).child("verification").set("guest")
            roles_to_del = set(
                fb.db.child("guilds")
                .child(f"{ctx.guild_id}")
                .child("all_roles")
                .get()
                .val()
                .values()
            )
            role_to_add = (
                fb.db.child("guilds")
                .child(f"{ctx.guild_id}")
                .child("all_roles")
                .get()
                .val()
                .values()
                .mapping.get(self.values[0])
            )
            user_roles = set(await ctx.member.fetch_roles())
            final_roles = [
                role.id for role in user_roles if role.id not in roles_to_del
            ]
            final_roles.append(role_to_add)
            await ctx.member.edit(roles=final_roles)
            self.view.stop()
        else:
            view = ModalView(self.values[0])
            message = await ctx.edit_response(
                "Please verify your Net ID below:",
                flags=hikari.MessageFlag.EPHEMERAL,
                components=view,
            )
            await view.start(message)


class DeleteMenu(miru.Select):
    def __init__(self, netid_roles, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.netid_roles = netid_roles

    async def callback(self, ctx: miru.Context) -> None:
        await ctx.edit_response(
            f"{self.values[0]} has been removed from the agreement roles", components=[]
        )
        fb.db.child("guilds").child(ctx.guild_id).child("all_roles").child(
            self.values[0]
        ).remove()
        if self.values[0] in self.netid_roles:
            fb.db.child("guilds").child(ctx.guild_id).child("netid_roles").child(
                self.values[0]
            ).remove()
        else:
            fb.db.child("guilds").child(ctx.guild_id).child("guest_roles").child(
                self.values[0]
            ).remove()
        self.view.stop()


class ModalView(miru.View):
    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role

    @miru.button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, _: miru.Button, ctx: miru.ViewContext) -> None:
        modal = FirstModal(title="NetID verification:", role=self.role)
        await ctx.respond_with_modal(modal)


class VercodeView(miru.View):
    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role

    @miru.button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, _: miru.Button, ctx: miru.ViewContext) -> None:
        modal = SecondModal(title="Verification code:", role=self.role)
        await ctx.respond_with_modal(modal)


class FirstModal(miru.Modal):
    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role

    netid = miru.TextInput(label="NetID", placeholder="Type your NetID!", required=True)

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        if not await fb.test_netid(self.netid.value):
            await ctx.edit_response(
                "This NetID has already been verified. Please try again.", components=[]
            )
            self.stop()
            return
        fb.db.child("users").child(ctx.user.id).child("maybe_netid").set(
            self.netid.value
        )
        view = VercodeView(role=self.role)
        message = await ctx.edit_response(
            "Please check your email for the verification code!", components=view
        )
        await view.start(message)
        await fb.send_email(self.netid.value, ctx.author.id)
        # await fb.send_email(ctx.values, ctx.author.id)


class SecondModal(miru.Modal):
    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role

    ver_code = miru.TextInput(
        label="Verification code",
        placeholder="Check your email for the verification code!",
        required=True,
    )

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        if fb.db.child("users").child(ctx.user.id).child("ver_code").get().val() == int(
            self.ver_code.value
        ):
            await ctx.edit_response(
                "You have been verified for a NetID role! Have a good time!",
                components=[],
            )
            fb.db.child("users").child(ctx.user.id).child("verification").set("netid")
            netid = (
                fb.db.child("users").child(ctx.user.id).child("maybe_netid").get().val()
            )
            fb.db.child("users").child(ctx.user.id).child("netid").set(netid)
            fb.db.child("users").child(ctx.user.id).child("maybe_netid").remove()
            fb.db.child("verified_netids").push(netid)
            roles_to_del = set(
                fb.db.child("guilds")
                .child(f"{ctx.guild_id}")
                .child("all_roles")
                .get()
                .val()
                .values()
            )
            role_to_add = (
                fb.db.child("guilds")
                .child(f"{ctx.guild_id}")
                .child("all_roles")
                .get()
                .val()
                .values()
                .mapping.get(self.role)
            )
            user_roles = set(await ctx.member.fetch_roles())
            final_roles = [
                role.id for role in user_roles if role.id not in roles_to_del
            ]
            final_roles.append(role_to_add)
            await ctx.member.edit(roles=final_roles)
            self.stop()
            return

        # You can also access the values using ctx.values, Modal.values, or use ctx.get_value_by_id()
        await ctx.edit_response(
            "That is not correct! Please try again, or grab a different role."
        )
        self.stop()

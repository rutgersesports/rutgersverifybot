import hikari
import miru
import src.database.firebase as fb


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


class SelectMenu(miru.Select):
    def __init__(self, netid_roles, all_roles_list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.netid_roles = netid_roles
        self.all_roles_list = all_roles_list

    async def callback(self, ctx: miru.Context) -> None:
        if self.values[0] not in self.netid_roles:
            await ctx.edit_response(
                "You have been verified for a guest role! Have a good time!",
                components=[],
            )
            fb.db.child("users").child(ctx.user.id).child("verification").set("guest")
            roles_to_del = set((all_roles := self.all_roles_list.values()))
            role_to_add = all_roles.mapping.get(self.values[0])
            user_roles = set(await ctx.member.fetch_roles())
            final_roles = [
                role.id for role in user_roles if role.id not in roles_to_del
            ]
            final_roles.append(role_to_add)
            await ctx.member.edit(roles=final_roles)
            self.view.stop()
        elif (
            netid := fb.db.child("users").child(ctx.user.id).child("netid").get().val()
        ) is not None:
            await add_netid_role(ctx, self.values[0], netid, self.all_roles_list)
            self.view.stop()
        else:
            view = ModalView(self.values[0], self.all_roles_list)
            message = await ctx.edit_response(
                "Please verify your Net ID below:",
                flags=hikari.MessageFlag.EPHEMERAL,
                components=view,
            )
            await view.start(message)


class ModalView(miru.View):
    def __init__(self, role, all_roles_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.all_roles_list = all_roles_list

    @miru.button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, _: miru.Button, ctx: miru.ViewContext) -> None:
        modal = FirstModal(
            title="NetID verification:",
            role=self.role,
            all_roles_list=self.all_roles_list,
        )
        await ctx.respond_with_modal(modal)


class FirstModal(miru.Modal):
    def __init__(self, role, all_roles_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.all_roles_list = all_roles_list

    netid = miru.TextInput(label="NetID", placeholder="Type your NetID!", required=True)

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        if not await fb.test_netid(self.netid.value):
            await ctx.edit_response(
                "This NetID has already been verified. Please try again.", components=[]
            )
            self.stop()
            return
        view = VercodeView(
            role=self.role, netid=self.netid.value, all_roles_list=self.all_roles_list
        )
        message = await ctx.edit_response(
            "Please check your email for the verification code!", components=view
        )
        await view.start(message)
        await fb.send_email(self.netid.value, ctx.author.id)


class VercodeView(miru.View):
    def __init__(self, role, all_roles_list, netid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.netid = netid
        self.all_roles_list = all_roles_list

    @miru.button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, _: miru.Button, ctx: miru.ViewContext) -> None:
        modal = SecondModal(
            title="Verification code:",
            role=self.role,
            netid=self.netid,
            all_roles_list=self.all_roles_list,
        )
        await ctx.respond_with_modal(modal)


class SecondModal(miru.Modal):
    def __init__(self, role, netid, all_roles_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.netid = netid
        self.all_roles_list = all_roles_list

    ver_code = miru.TextInput(
        label="Verification code",
        placeholder="Check your email for the verification code!",
        required=True,
    )

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        if not self.ver_code.value.isdigit():
            await ctx.edit_response("Please make sure you're only inputting digits!")
        elif fb.db.child("users").child(ctx.user.id).child(
            "ver_code"
        ).get().val() == int(self.ver_code.value):
            await add_netid_role(ctx, self.role, self.netid, self.all_roles_list)
            self.stop()
        else:
            await ctx.edit_response(
                "That is not correct! Please try again, or grab a different role."
            )


async def add_netid_role(ctx, role: str, netid: str, all_roles_list):
    await ctx.edit_response(
        "You have been verified for a NetID role! Have a good time!",
        components=[],
    )
    fb.db.child("users").child(ctx.user.id).child("verification").set("netid")
    if netid is not None:
        fb.db.child("users").child(ctx.user.id).child("netid").set(netid)
    else:
        fb.db.child("verified_netids").push(netid)
    roles_to_del = set((all_roles := all_roles_list.values()))
    role_to_add = all_roles.mapping.get(role)
    user_roles = set(await ctx.member.fetch_roles())
    final_roles = [role.id for role in user_roles if role.id not in roles_to_del]
    final_roles.append(role_to_add)
    await ctx.member.edit(roles=final_roles)
    return

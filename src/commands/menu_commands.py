import miru


async def remove_netid_role(ctx: miru.Context, role) -> None:
    ctx.bot.guilds[ctx.guild_id]["all_roles"].pop(role)
    ctx.bot.guilds[ctx.guild_id]["netid_roles"].pop(role)
    ctx.bot.db.child("guilds").child(ctx.guild_id).child("all_roles").child(
        role
    ).remove()
    ctx.bot.db.child("guilds").child(ctx.guild_id).child("netid_roles").child(
        role
    ).remove()


async def remove_guest_role(ctx: miru.Context, role) -> None:
    ctx.bot.guilds[ctx.guild_id]["all_roles"].pop(role)
    ctx.bot.guilds[ctx.guild_id]["guest_roles"].pop(role)
    ctx.bot.db.child("guilds").child(ctx.guild_id).child("all_roles").child(
        role
    ).remove()
    ctx.bot.db.child("guilds").child(ctx.guild_id).child("guest_roles").child(
        role
    ).remove()


async def remove_join_role(ctx: miru.Context, role) -> None:
    ctx.bot.guilds[ctx.guild_id]["join_roles"].pop(role)
    ctx.bot.db.child("guilds").child(ctx.guild_id).child("join_roles").child(
        role
    ).remove()

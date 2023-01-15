import miru
from src.database.firebase import db


async def remove_netid_role(ctx: miru.Context, role) -> None:
    db.child("guilds").child(ctx.guild_id).child("all_roles").child(role).remove()
    db.child("guilds").child(ctx.guild_id).child("netid_roles").child(role).remove()


async def remove_guest_role(ctx: miru.Context, role) -> None:
    db.child("guilds").child(ctx.guild_id).child("all_roles").child(role).remove()
    db.child("guilds").child(ctx.guild_id).child("guest_roles").child(role).remove()


async def remove_join_role(ctx: miru.Context, role) -> None:
    db.child("guilds").child(ctx.guild_id).child("join_roles").child(role).remove()

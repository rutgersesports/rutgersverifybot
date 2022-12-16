import hikari
import lightbulb
from src.database.Firebase import db
plugin = lightbulb.Plugin("SlashPlugin")


@plugin.command()
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD), lightbulb.checks.guild_only)
@lightbulb.command(name="setagreementchannel", description="Sets the agreement channel of the server.")
@lightbulb.implements(lightbulb.SlashCommand)
async def setAgreementChannel(ctx: lightbulb.SlashContext) -> None:
    current = db.child("guilds").child(f"{ctx.guild_id}").child("agreementChannel").get(ctx.channel_id).val()
    if current == ctx.channel_id:
        await ctx.respond(f'{ctx.get_channel().mention} is already the agreement channel.')
        return
    db.child("guilds").child(f"{ctx.guild_id}").child("agreementChannel").set(ctx.channel_id)
    await ctx.respond(
        f"{ctx.get_channel().mention} has been set to {ctx.get_guild().name}'s agreement channel"
    )


@plugin.command()
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD), lightbulb.checks.guild_only)
@lightbulb.option(name="role5", description="The role to add to this server's agreement roles.", type=hikari.Role,
                  required=False)
@lightbulb.option(name="role4", description="The role to add to this server's agreement roles.", type=hikari.Role,
                  required=False)
@lightbulb.option(name="role3", description="The role to add to this server's agreement roles.", type=hikari.Role,
                  required=False)
@lightbulb.option(name="role2", description="The role to add to this server's agreement roles.", type=hikari.Role,
                  required=False)
@lightbulb.option(name="role", description="The role to add to this server's agreement roles.", type=hikari.Role,
                  required=True)
@lightbulb.command(name="setnetidroles", description="Sets the agreement roles that require NetID.")
@lightbulb.implements(lightbulb.SlashCommand)
async def setNetIDRoles(ctx: lightbulb.SlashContext) -> None:
    # string = ', '.join([v[1].name for v in ctx.options.items()])
    # ''' if v[1].id not in db.child("guilds").child(f"{ctx.guild_id}").child("NetIDRoles").get().val().values()'''
    # await ctx.respond(string)
    # if string == '':
    #     await ctx.respond("All roles are already agreement roles.")
    # await ctx.respond(f'{string}' + (" has" if ' ' in string else " have been added to the agreement roles."))
    roles: list[hikari.Role] = [v[1] for v in ctx.options.items()]
    await ctx.respond(f'{roles[0].name} {roles[1].name}')
    await ctx.respond(', '.join([v.name for v in roles]))


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.MissingRequiredPermission):
        await event.context.respond(
            f"You do not have permissions to use `{event.context.command.name}`.")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)

import discord


def verified_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Verification Confirmed",
        description="You've been verified.",
        color=0x00FF33,
    )
    return embed


def email_sent(user_email) -> discord.Embed:
    embed = discord.Embed(
        title="Email Sent",
        description=f"A verification code has been sent to `{user_email}`.\nIf you haven't received an email, check your spam.",
        color=0x006EFF,
    )
    return embed


def ask_email() -> discord.Embed:
    embed = discord.Embed(
        title="Awaiting Email",
        description=f"Send your email as a message.",
        color=0x006EFF,
    )
    return embed

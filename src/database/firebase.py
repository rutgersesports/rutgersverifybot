import random
from os import getenv

import lightbulb
from email.message import EmailMessage
import ssl
import smtplib

import requests
from src.bot import NewBot


async def send_email(bot: NewBot, netid: str, author_id: int) -> None:
    # Declare var, FIX NETID/ver_code input parsing
    email_sender = getenv("email")
    email_password = getenv("emailpass")
    email_receiver = netid + "@scarletmail.rutgers.edu"
    ver_code = random.randrange(100000, 999999)
    bot.users[author_id]["ver_code"] = ver_code
    bot.db.child("users").child(author_id).child("ver_code").set(ver_code)

    subject = "Your CoolCat verification code"

    # Email formatting, em is the object
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content("Placeholder, do not remove")

    # Import email template (html) data from GitHub
    link = getenv("email_template")
    form = requests.get(link)

    # Edit Template (variable swap)
    html_message = form.text
    html_message = html_message.replace("{{verification}}", str(ver_code))

    # Replacing content with
    em.add_alternative(html_message, subtype="html")

    # Establish SSL security
    context = ssl.create_default_context()

    # Send email using SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)

        smtp.sendmail(email_sender, email_receiver, em.as_string())


async def is_agreement_channel(ctx: lightbulb.Context) -> bool:
    try:
        agreement_channel = ctx.bot.guilds[ctx.guild_id]["agreement_channel"]
    except KeyError:
        raise lightbulb.errors.CheckFailure(
            "This server has not set up an agreement channel yet."
        )
    if int(ctx.channel_id) == agreement_channel:
        return True
    else:
        raise lightbulb.errors.CheckFailure(
            "Agree can only be used in the set agreement channel."
        )


async def has_agreement_roles(ctx: lightbulb.Context) -> bool:
    try:
        all_roles = ctx.bot.guilds[ctx.guild_id]["all_roles"]
    except KeyError:
        raise lightbulb.errors.CheckFailure(
            "This server has not set up agreement roles yet."
        )
    return bool(all_roles)


async def has_moderation_channel(ctx: lightbulb.Context) -> bool:
    try:
        moderation_channel = ctx.bot.guilds[ctx.guild_id]["moderation_channel"]
    except KeyError:
        return False
    return bool(moderation_channel)


async def test_netid(bot: NewBot, netid: str) -> bool:
    return bot.verified_netids is None or netid not in bot.verified_netids.values()

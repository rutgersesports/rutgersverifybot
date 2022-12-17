import random
from os import getenv

import lightbulb
import pyrebase
from email.message import EmailMessage
import ssl
import smtplib

import requests

config = {
    "apiKey": getenv("apiKey"),
    "authDomain": getenv("authDomain"),
    "databaseURL": getenv("databaseURL"),
    "projectId": getenv("projectId"),
    "storageBucket": getenv("storageBucket"),
    "messagingSenderId": getenv("messagingSenderId"),
    "appId": getenv("appId"),
    "measurementId": getenv("measurementId"),
    "serviceAccount": getenv("serviceAccount"),
}

db = pyrebase.initialize_app(config).database()


async def check_empty_or_mia(author_id: int) -> bool:
    if (
        db.child("users").get().val() is None
        or f"{author_id}" not in db.child("users").get().val()
    ):
        db.child("users").child(f"{author_id}").set(
            {
                "msg_count": 0,
                "verified": False,
                "netID": "unknown",
            }
        )
        return False
    return True


# async def email() -> bool:


def check_vercode(code: int, user_id: int) -> bool:
    if db.child("users").child(f"{user_id}").child("ver_code").get().val() == code:
        db.child("users").child(f"{user_id}").update({"verified": True})
        return True
    return False


async def send_email(netid: str, author_id: int) -> None:

    # Declare var, FIX NETID/ver_code input parsing
    email_sender = getenv("email")
    email_password = getenv("emailpass")
    email_receiver = netid + "@scarletmail.rutgers.edu"
    ver_code = random.randrange(100000, 999999)
    db.child("users").child(f"{author_id}").child("ver_code").set(ver_code)

    subject = "Your CoolCat verification code"

    # Email formatting, em is the object
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content("Placeholder, do not remove")

    # Import email template (html) data from GitHub
    link = "https://raw.githubusercontent.com/rutgersesports/rutgersverifybot/main/src/database/emailtemplate.html"
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


# async def get_prefix(guildID: int) -> str:
#     try:
#         prefix = (
#             db.child("guilds").child(f"{guildID}").child("prefix").get().val().values()
#         )
#     except AttributeError:
#         db.child("guilds").child(f"{guildID}").update({"prefix": "!"})
#         return "!"
#     else:
#         return prefix


async def is_agreement_channel(ctx: lightbulb.Context) -> bool:
    if (
        db.child("guilds")
        .child(f"{ctx.guild_id}")
        .child("agreement_channel")
        .get()
        .val()
        is None
    ):
        raise lightbulb.errors.CheckFailure(
            "This server has not set up an agreement channel yet."
        )
    chan_id = int(ctx.channel_id)
    agree_id = (
        db.child("guilds")
        .child(f"{ctx.guild_id}")
        .child("agreement_channel")
        .get()
        .val()
    )
    if chan_id == agree_id:
        return True
    else:
        raise lightbulb.errors.CheckFailure(
            "Agree can only be used in the set agreement channel."
        )


async def has_agreement_roles(ctx: lightbulb.Context) -> bool:
    if (
        db.child("guilds").child(f"{ctx.guild_id}").child("netid_roles").get().val()
        is None
        and db.child("guilds").child(f"{ctx.guild_id}").child("guest_roles").get().val()
        is None
    ):
        raise lightbulb.errors.CheckFailure(
            "This server has not set up agreement roles yet."
        )
    return True


async def test_netid(netid: str) -> bool:
    return (
        db.child("verified_netids").get().val() is None
        or netid not in db.child("verified_netids").get().val().values()
    )

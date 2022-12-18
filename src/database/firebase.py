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


async def send_email(netid: str, author_id: int) -> None:
    # Declare var, FIX NETID/ver_code input parsing
    email_sender = getenv("email")
    email_password = getenv("emailpass")
    email_receiver = netid + "@scarletmail.rutgers.edu"
    ver_code = random.randrange(100000, 999999)
    db.child("users").child(author_id).child("ver_code").set(ver_code)

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
    if (
        agreement_channel := db.child("guilds")
        .child(ctx.guild_id)
        .child("agreement_channel")
        .get()
        .val()
    ) is None:
        raise lightbulb.errors.CheckFailure(
            "This server has not set up an agreement channel yet."
        )
    chan_id = int(ctx.channel_id)
    if chan_id == agreement_channel:
        return True
    else:
        raise lightbulb.errors.CheckFailure(
            "Agree can only be used in the set agreement channel."
        )


async def has_agreement_roles(ctx: lightbulb.Context) -> bool:
    if (
        db.child("guilds").child(ctx.guild_id).child("netid_roles").get().val() is None
        and db.child("guilds").child(ctx.guild_id).child("guest_roles").get().val()
        is None
    ):
        raise lightbulb.errors.CheckFailure(
            "This server has not set up agreement roles yet."
        )
    return True


async def has_moderation_channel(ctx: lightbulb.Context) -> bool:
    return (
        db.child("guilds").child(ctx.guild_id).child("moderation_channel").get().val()
        is not None
    )


async def test_netid(netid: str) -> bool:
    return (
        verified_netids := db.child("verified_netids").get().val()
    ) is None or netid not in verified_netids.values()

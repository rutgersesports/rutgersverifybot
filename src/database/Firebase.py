from os import getenv

import hikari
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


async def checkEmptyOrMia(author_id: int) -> bool:
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


def checkVercode(code: int, id: int) -> bool:
    if db.child("users").child(f"{id}").child("ver_code").get().val() == code:
        db.child("users").child(f"{id}").update({"verified": True})
        return True
    return False

async def sendEmail(event: hikari.DMMessageCreateEvent):

    # Declare var, FIX NETID/ver_code input parsing
    email_sender = os.getenv('email')
    email_password = os.getenv('emailpass')
    email_receiver = event.content + '@scarletmail.rutgers.edu'
    ver_code = db.child('users').child(f'{event.author_id}').child('ver_code').get().val()
    netID = db.child('users').child(f'{event.author_id}').child('netID').get().val()

    subject = 'Your CoolCat Verification'
    
    # Email formatting, em is the object
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content("Placeholder, do not remove")
    
    # Import email template (html) data from github
    link = 'https://raw.githubusercontent.com/rutgersesports/rutgersverifybot/main/src/database/emailtemplate.html'
    form = requests.get(link)

    # Edit Template (variable swap)
    html_message = form.text
    html_message = html_message.replace('{{verification}}', str(ver_code))

    #Replacing content with 
    em.add_alternative(html_message, subtype = 'html')

    # Establish SSL security
    context = ssl.create_default_context()

    # Send email using SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:

        smtp.login(email_sender, email_password)

        smtp.sendmail(email_sender, email_receiver, em.as_string())

# async def place_msg(event: hikari.GuildMessageCreateEvent):
#     if not event.is_human:
#         return
#     await checkEmptyOrMia(event.author_id)
#     # try:
#     msg_count = (
#         db.child("users").child(f"{event.author_id}").child("msg_count").get().val()
#     )
#     db.child("users").child(f"{event.author_id}").update({"msg_count": msg_count + 1})
#     msg_count += 1

# BUGGED AND CANNOT FIX, PYREBASE ISSUE
# except TypeError:
#     db.update({"msg_count": 1})
#     # db.update({"msg_count": 0})
#     msg_count = (
#         db.child("users").child(f"{event.author_id}").child("msg_count").get().val()
#     )
# db.child("users").child(f"{event.author_id}").child("msgs").child(
#     f'key{msg_count}').set(event.content)

async def getPrefix(guildID: int) -> str:
    try:
        prefix = (
            db.child("guilds").child(f"{guildID}").child("prefix").get().val().values()
        )
    except AttributeError:
        db.child("guilds").child(f"{guildID}").update({"prefix": "!"})
        return "!"
    else:
        return prefix


def getAgreementRoles(guild_id: int):
    return db.child("guilds").child(f"{guild_id}").child("NetIDRoles").get()

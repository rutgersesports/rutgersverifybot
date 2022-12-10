import os
import random

import hikari
import pyrebase
import dotenv
from email.message import EmailMessage
import ssl
import smtplib

dotenv.load_dotenv()
config = {
    "apiKey": os.getenv("apiKey"),
    "authDomain": os.getenv("authDomain"),
    "databaseURL": os.getenv("databaseURL"),
    "projectId": os.getenv("projectId"),
    "storageBucket": os.getenv("storageBucket"),
    "messagingSenderId": os.getenv("messagingSenderId"),
    "appId": os.getenv("appId"),
    "measurementId": os.getenv("measurementId"),
    "serviceAccount": os.getenv("serviceAccount")
}

db = pyrebase.initialize_app(config).database()


async def checkEmptyOrMia(author_id: int, join: bool) -> bool:
    if db.child('users').get().val() is None or f'{author_id}' not in db.child('users').get().val():
        db.child('users').child(f'{author_id}').set({
            'msg_count': 0,
            'verified': False,
            'ver_code': random.randrange(100000, 999999),
            'netID': 'unknown',
        })
        return False
    return True

# async def email() -> bool:


def checkVercode(code: int, id: int) -> bool:
    if db.child('users').child(f'{id}').child('ver_code').get().val() == code:
        db.child('users').child(f'{id}').update({'verified': True})
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
    body = f"""
    Here is your CoolCat verification code:
    {ver_code}
    Please send it back to the bot through its DM!
    """

    # Email formatting, em is the object
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Establish SSL security
    context = ssl.create_default_context()

    # Send email using SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:

        smtp.login(email_sender, email_password)

        smtp.sendmail(email_sender, email_receiver, em.as_string())


async def place_msg(event: hikari.GuildMessageCreateEvent):
    if not event.is_human:
        return
    await checkEmptyOrMia(event.author_id, False)
    msg_count = db.child('users').child(f'{event.author_id}').child('msg_count').get().val()
    db.child('users').child(f'{event.author_id}').update({'msg_count': msg_count + 1})
    db.child('users').child(f'{event.author_id}').child('msgs').child(f'key{msg_count}').set(event.content)

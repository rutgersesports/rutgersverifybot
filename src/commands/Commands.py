import asyncio
import os
import random

import dotenv
import hikari

from src.database import Firebase as db
dotenv.load_dotenv()
bot = hikari.GatewayBot(token=os.getenv("token"), intents=hikari.Intents.ALL)


# Split into separate commands files for ease of access soon
@bot.listen()
async def count(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human:
        return
    await db.place_msg(event)


@bot.listen()
async def join(event: hikari.MemberCreateEvent) -> None:
    if event.user.is_bot:
        return
    print("here")
    await verification(event.user)


async def verification(u: hikari.User):
    await db.checkEmptyOrMia(u.id)
    if not db.db.child("users").child(f"{u.id}").child("verified").get().val():
        await u.send(
            "Are you a Rutgers Student, Alumni, or Guest?"
            "\nPossible responses: Rutgers Student, Alumni, Guest"
        )
        try:
            AccType = await bot.wait_for(
                hikari.DMMessageCreateEvent,
                timeout=300,
                predicate=lambda e: e.author_id == u.id
                and (
                    e.content == "Rutgers Student"
                    or e.content == "Alumni"
                    or e.content == "Guest"
                ),
            )
            if AccType.content == "Guest":
                await u.send("fill")
            else:
                await u.send("Enter your NetID")
            netid = await bot.wait_for(
                hikari.DMMessageCreateEvent,
                # How long to wait for
                timeout=300,
                # The event only matches if this returns True
                predicate=lambda e: (
                    (
                        db.db.child("netIDs").get().val() is None
                        or e.content.lower()
                        not in db.db.child("netIDs").get().val().values()
                    )
                    and e.author_id == u.id
                    and e.content.isalnum()
                    and len(e.content) < 10
                )
                or e.content == os.getenv("skipcode"),
            )

            await u.send(
                "You are not verified, please check your email for the verification code"
            )
            if netid.content != os.getenv("skipcode"):
                await db.sendEmail(netid)
            else:
                await u.send(
                    db.db.child("users").child(f"{u.id}").child("ver_code").get().val()
                )
            await bot.wait_for(
                hikari.DMMessageCreateEvent,
                # How long to wait for
                timeout=300,
                # The event only matches if this returns True
                predicate=lambda e: e.author_id == u.id
                and e.content.isdigit()
                and len(e.content) == 6
                and db.checkVercode(int(e.content), e.author_id),
            )
            await u.send("You are now verified! Have fun :)")
            db.db.child("users").child(f"{u.id}").update(
                {"netID": f"{netid.content.lower()}"}
            )
            db.db.child("netIDs").push(f"{netid.content.lower()}")
        except asyncio.TimeoutError:
            await u.send(
                'Your session has timed out. Please respond "Retry" to retry the verification process.'
            )
    else:
        await u.send("You are already verified! Have fun :)")


@bot.listen()
async def retryVerification(event: hikari.DMMessageCreateEvent):
    if not event.is_human:
        return None
    if event.content.lower() == "retry":
        db.db.child("users").child(f"{event.author_id}").child("ver_code").set(random.randrange(100000, 999999))
        await verification(event.author)

bot.run()

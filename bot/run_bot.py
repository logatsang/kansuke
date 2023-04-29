import os

import asyncio
import sqlite3
from operator import itemgetter

from dataclasses import dataclass

import discord
from discord.commands.context import ApplicationContext as Context
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
DBFILE = "bot/test.db"

bot = discord.Bot()
db_lock = asyncio.Lock()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command(description="Sends the bot's latency.")
async def ping(ctx: Context):
    await ctx.respond(f"Pong! Latency is {bot.latency}")


@bot.command(description="Resets database.")
async def reset(ctx: Context, password: discord.Option(str)):
    if password != os.environ.get("PASSWORD"):  # TODO: better solution than this
        await ctx.respond("Invalid request.")
        return

    await database_reset()
    await ctx.respond("Database reset.")


@bot.command(description="Reads entries for character.")
async def read(ctx: Context, char: discord.Option(str)):
    content = await database_read(char[0])
    await ctx.respond(content)


@bot.command(description="Adds entry for character.")
async def write(ctx: Context, char: discord.Option(str), tag: discord.Option(str)):
    await database_write(ctx.author.id, char[0], tag)
    await ctx.respond("Entry added.")


async def database_read(char: str=None) -> list:
    codepoint = ord(char)

    async with db_lock:
        db = sqlite3.connect(DBFILE)
        cursor = db.execute(f"""SELECT * FROM entries WHERE codepoint = {codepoint};""")
        data = cursor.fetchall()
        db.close()

    data = sorted(data, key=itemgetter(1), reverse=True)
    content = []
    for row in data:
        _codepoint, user, tag = row
        content.append((user, tag))

    return content


async def database_reset():
    async with db_lock:
        db = sqlite3.connect(DBFILE)
        db.execute("DROP TABLE IF EXISTS characters;")
        db.execute("""CREATE TABLE characters
        (
            codepoint   INT NOT NULL UNIQUE PRIMARY KEY,
            count       INT NOT NULL DEFAULT 0
        );
        """)

        db.execute("DROP TABLE IF EXISTS entries;")
        db.execute("""CREATE TABLE entries
        (
            codepoint   INT NOT NULL PRIMARY KEY,
            user        INT NOT NULL,
            tag         STRING NOT NULL
        );
        """)
        db.commit()
        db.close()


async def database_write(user: int, char: str, tag: str):
    char = char[0]
    codepoint = ord(char)

    async with db_lock:
        db = sqlite3.connect(DBFILE)
        db.execute(f"""INSERT INTO characters (codepoint, count) VALUES ({codepoint}, 1)
                       ON CONFLICT DO UPDATE SET count = count + 1;""")
        db.execute(f"""INSERT INTO entries (codepoint, user, tag) VALUES
                       ({codepoint}, {user}, '{tag}');""")
        db.commit()
        db.close()


if __name__ == "__main__":
    bot.run(TOKEN)

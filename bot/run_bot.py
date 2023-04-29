import os
from dotenv import load_dotenv

import discord
from discord.commands.context import ApplicationContext as Context

load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
DBFILE = "/test.db"

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command(description="Sends the bot's latency.")
async def ping(ctx: Context):
    print(type(ctx))
    await ctx.respond(f"Pong! Latency is {bot.latency}")


if __name__ == "__main__":
    bot.run(TOKEN)

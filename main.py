import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional
import discord
from discord.ext import commands,tasks
from itertools import cycle
import os
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()
DISCORD_TOKEN = os.getenv("BOT_TOKEN")
PREFIX = os.getenv("PREFIX")

def get_server_prefix(client,message):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)
    return prefix.get(str(message.guild.id), "!")


PREFIX = get_server_prefix

client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())


@client.event
async def on_ready():
    await client.tree.sync()
    print("Synced slash commands.")
    print("Bot is connected to Discord...")

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
            print(f"{filename[:-3]} loaded...")

async def main():
    async with client:
        await load()
        await client.start(token=DISCORD_TOKEN)


asyncio.run(main())
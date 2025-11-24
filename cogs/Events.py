# cogs/events.py
import discord
from discord.ext import commands
import json
import os

PREFIX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prefixes.json")

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open(PREFIX_PATH, "r") as f:
            prefix = json.load(f)

        prefix[str(guild.id)] = "!"

        with open(PREFIX_PATH, "w") as f:
            json.dump(prefix, f, indent=4)


async def setup(client):
    await client.add_cog(Events(client))

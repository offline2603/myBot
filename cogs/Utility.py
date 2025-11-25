import discord
from discord.ext import commands
from discord import app_commands
import json
import os

PREFIX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prefixes.json")


class Utility(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    # command to set prefix for a server 
    @commands.command()
    async def setprefix(self,ctx,*,newPrefix:str):
        with open(PREFIX_PATH, "r") as f:
            prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = newPrefix
        
        with open(PREFIX_PATH,"w") as f:
            json.dump(prefixes,f,indent=4)
        
        await ctx.reply(f"Prefix for your server have been changed to {newPrefix}")

    # ping command
    @commands.command()
    async def ping(self,ctx):
        bot_latency = round(self.client.latency * 1000)
        await ctx.reply(f"Pong! {bot_latency} ms")
        
    #slash command for ping
    @app_commands.command(name="ping", description="Shows bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.client.latency * 1000)
        await interaction.response.send_message(f"Pong! `{latency}ms`",ephemeral=True)

    # Slash command: greet
    @app_commands.command(name="greet", description="Greet a user")
    async def greet(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"Hello {user.mention}! 👋", ephemeral=False)


async def setup(client):
    await client.add_cog(Utility(client))
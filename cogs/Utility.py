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
    
    # command to create a embed just for testing 
    @commands.command()
    async def embed(self,ctx):
        embed_msg = discord.Embed(color= ctx.author.color,title="Title of Embed",type= 'rich', url= None, description="Description of embed")
        
        embed_msg.set_author(name=f"Requested by {ctx.author.name}",icon_url=ctx.author.avatar.url)
        embed_msg.set_thumbnail(url=ctx.guild.icon)
        embed_msg.set_image(url=ctx.guild.icon)
        embed_msg.set_footer(text="footer", icon_url=ctx.author.avatar.url)
        embed_msg.add_field(name="field name", value="field value", inline=False)

        await ctx.reply(embed=embed_msg)



async def setup(client):
    await client.add_cog(Utility(client))
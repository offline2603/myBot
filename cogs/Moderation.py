import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self,client):
        self.client = client
        
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def clear(self,ctx,count:int):
        await ctx.channel.purge(limit=count)
        await ctx.reply(f"{count} messages have been deleted.")
        
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self,ctx,member:discord.Member,*, reason="No Reason Provided"):
        await member.kick(reason=reason)
        await ctx.reply(f"{member} successfully kicked,{reason}")
        
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self,ctx,member:discord.Member,*,reason="No Reason provided"):
        await member.ban(reason=reason)
        await ctx.reply(f"{member} successfully banned, {reason}")
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unban(self,ctx,userId:int):
        user = await self.client.fetch_user(userId)
        await ctx.guild.unban(user)
        await ctx.reply(f"<@{userId}> successfully unbanned...")

    
async def setup(client):
    await client.add_cog(Moderation(client=client))
        
        
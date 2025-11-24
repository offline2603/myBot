import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from json import JSONDecodeError
from datetime import datetime, timezone
from typing import Optional, Dict


SIMPLE_EVENTS = ["message_delete", "message_edit", "member_join", "member_remove"]


class Logs(commands.Cog):
    """Beginner-friendly logging cog.

    Features (4):
    - Message Delete log
    - Message Edit log
    - Member Join log
    - Member Remove log

    Simple commands:
    - /setlogchannel <channel>
    - /showlogchannel
    - /enablelogs (enable all 4)
    - /disablelogs (disable all)

    JSON format (simple):
    {
      "guild_id": {
         "log_channel": 1234567890,
         "enabled": ["message_delete", ...]
      }
    }
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.file_path = os.path.join(os.getcwd(), "logs.json")
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    # --------- JSON helpers ---------
    def load(self) -> Dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            return {}

    def save(self, data: Dict):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def _ensure(self, gid: str) -> Dict:
        data = self.load()
        conf = data.get(gid)
        if conf is None:
            conf = {"log_channel": None, "enabled": []}
            data[gid] = conf
            self.save(data)
        return conf

    def _ts(self):
        return datetime.now(timezone.utc)

    def _get_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        data = self.load()
        conf = data.get(str(guild.id), {})
        ch = conf.get("log_channel")
        if not ch:
            return None
        return guild.get_channel(ch)

    def _is_enabled(self, guild: discord.Guild, event: str) -> bool:
        data = self.load()
        conf = data.get(str(guild.id), {})
        enabled = conf.get("enabled", [])
        return event in enabled

    async def _send(self, guild: discord.Guild, embed: discord.Embed):
        ch = self._get_channel(guild)
        if not ch:
            return
        try:
            await ch.send(embed=embed)
        except Exception:
            return

    # --------- Commands ---------
    @app_commands.command(name="setlogchannel", description="Set the channel where logs are sent.")
    async def setlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.guild:
            await interaction.response.send_message("Run this command in a server.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need Manage Server permission.", ephemeral=True)
            return

        data = self.load()
        gid = str(interaction.guild.id)
        conf = data.get(gid, {})
        conf["log_channel"] = channel.id
        conf.setdefault("enabled", conf.get("enabled", []))
        data[gid] = conf
        self.save(data)

        embed = discord.Embed(title="Log Channel Set", description=f"Logs will be sent to {channel.mention}", color=discord.Color.green(), timestamp=self._ts())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="showlogchannel", description="Show the current log channel.")
    async def showlogchannel(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Run this command in a server.", ephemeral=True)
            return

        data = self.load()
        conf = data.get(str(interaction.guild.id), {})
        ch = conf.get("log_channel")
        desc = f"{f'<#{ch}>' if ch else 'Not set'}"
        embed = discord.Embed(title="Log Channel", description=desc, color=discord.Color.blurple(), timestamp=self._ts())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="enablelogs", description="Enable all simple logs (no args).")
    async def enablelogs(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Run in server.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Manage Server permission required.", ephemeral=True)
            return

        data = self.load()
        gid = str(interaction.guild.id)
        conf = self._ensure(gid)
        conf["enabled"] = SIMPLE_EVENTS.copy()
        data[gid] = conf
        self.save(data)
        await interaction.response.send_message("Enabled simple logs.", ephemeral=True)

    @app_commands.command(name="disablelogs", description="Disable all simple logs (no args).")
    async def disablelogs(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Run in server.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Manage Server permission required.", ephemeral=True)
            return

        data = self.load()
        gid = str(interaction.guild.id)
        conf = self._ensure(gid)
        conf["enabled"] = []
        data[gid] = conf
        self.save(data)
        await interaction.response.send_message("Disabled simple logs.", ephemeral=True)

    # --------- Event handlers (4 simple) ---------
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        event = "message_delete"
        if not message.guild or not self._is_enabled(message.guild, event):
            return

        author = message.author
        author_name = getattr(author, "display_name", "Unknown") if author else "Unknown"
        author_id = getattr(author, "id", "N/A")
        content = message.content or "(no content)"

        embed = discord.Embed(title="Message Deleted", color=discord.Color.red(), timestamp=self._ts())
        embed.add_field(name="Author", value=f"{author_name} ({author_id})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention if message.channel else "Unknown", inline=False)
        embed.add_field(name="Content", value=content[:1024], inline=False)
        try:
            if author and getattr(author, "display_avatar", None):
                embed.set_thumbnail(url=author.display_avatar.url)
        except Exception:
            pass

        await self._send(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        event = "message_edit"
        if not before.guild or not self._is_enabled(before.guild, event):
            return
        if before.author and before.author.bot:
            return
        if before.content == after.content:
            return

        author = before.author
        name = getattr(author, "display_name", "Unknown") if author else "Unknown"
        uid = getattr(author, "id", "N/A")

        embed = discord.Embed(title="Message Edited", color=discord.Color.orange(), timestamp=self._ts())
        embed.add_field(name="Author", value=f"{name} ({uid})", inline=False)
        embed.add_field(name="Channel", value=before.channel.mention if before.channel else "Unknown", inline=False)
        embed.add_field(name="Before", value=(before.content or "(no content)")[:1024], inline=False)
        embed.add_field(name="After", value=(after.content or "(no content)")[:1024], inline=False)

        try:
            if author and getattr(author, "display_avatar", None):
                embed.set_thumbnail(url=author.display_avatar.url)
        except Exception:
            pass

        await self._send(before.guild, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        event = "member_join"
        if not member.guild or not self._is_enabled(member.guild, event):
            return

        name = member.display_name
        uid = member.id
        created = member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")

        embed = discord.Embed(title="Member Joined", description=f"{name} has joined.", color=discord.Color.green(), timestamp=self._ts())
        embed.add_field(name="User", value=f"{name} ({uid})", inline=False)
        embed.add_field(name="Account Created", value=created, inline=False)
        try:
            if getattr(member, "display_avatar", None):
                embed.set_thumbnail(url=member.display_avatar.url)
        except Exception:
            pass

        await self._send(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        event = "member_remove"
        if not member.guild or not self._is_enabled(member.guild, event):
            return

        embed = discord.Embed(title="Member Left", color=discord.Color.dark_grey(), timestamp=self._ts())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        try:
            if getattr(member, "display_avatar", None):
                embed.set_thumbnail(url=member.display_avatar.url)
        except Exception:
            pass

        await self._send(member.guild, embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from json import JSONDecodeError


class Logs(commands.Cog):
    """Simple logging cog. Stores per-guild settings in `logs.json`.

    Commands:
    - /setlogchannel channel: set channel for logs
    - /enablelog event: enable logging for an event
    - /disablelog event: disable logging for an event
    - /showlogs: show current log channel and enabled events

    Events supported: `member_join`, `member_remove`, `message_delete`, `message_edit`
    """

    SUPPORTED_EVENTS = ["member_join", "member_remove", "message_delete", "message_edit"]

    def __init__(self, client: commands.Bot):
        self.client = client
        self.file_path = os.path.join(os.getcwd(), "logs.json")

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f, indent=4)

    def load_data(self) -> dict:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            return {}

    def save_data(self, data: dict):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    # ------------------ Commands ------------------
    @app_commands.command(name="setlogchannel", description="Set the channel where logs will be sent.")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        gid = str(interaction.guild.id)
        data[gid] = data.get(gid, {})
        data[gid]["channel"] = channel.id
        self.save_data(data)

        await interaction.response.send_message(f"Log channel set to {channel.mention}")

    @app_commands.command(name="enablelog", description="Enable logging for a specific event.")
    async def enable_log(self, interaction: discord.Interaction, event: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        event = event.lower()
        if event not in self.SUPPORTED_EVENTS:
            await interaction.response.send_message(f"Unsupported event. Supported: {', '.join(self.SUPPORTED_EVENTS)}", ephemeral=True)
            return

        data = self.load_data()
        gid = str(interaction.guild.id)
        data[gid] = data.get(gid, {})
        enabled = set(data[gid].get("enabled", []))
        enabled.add(event)
        data[gid]["enabled"] = list(enabled)
        self.save_data(data)

        await interaction.response.send_message(f"Enabled logging for `{event}`")

    @app_commands.command(name="disablelog", description="Disable logging for a specific event.")
    async def disable_log(self, interaction: discord.Interaction, event: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        event = event.lower()
        if event not in self.SUPPORTED_EVENTS:
            await interaction.response.send_message(f"Unsupported event. Supported: {', '.join(self.SUPPORTED_EVENTS)}", ephemeral=True)
            return

        data = self.load_data()
        gid = str(interaction.guild.id)
        data[gid] = data.get(gid, {})
        enabled = set(data[gid].get("enabled", []))
        if event in enabled:
            enabled.remove(event)
        data[gid]["enabled"] = list(enabled)
        self.save_data(data)

        await interaction.response.send_message(f"Disabled logging for `{event}`")

    @app_commands.command(name="showlogs", description="Show current log settings for this server.")
    async def show_logs(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        data = self.load_data()
        gid = str(interaction.guild.id)
        conf = data.get(gid, {})
        channel_id = conf.get("channel")
        enabled = conf.get("enabled", [])

        channel_mention = f"<#{channel_id}>" if channel_id else "Not set"

        text = f"Log Channel: {channel_mention}\nEnabled events: {', '.join(enabled) if enabled else 'None'}"
        await interaction.response.send_message(text, ephemeral=True)

    # ------------------ Event handlers ------------------
    def _get_log_channel(self, guild: discord.Guild):
        data = self.load_data()
        conf = data.get(str(guild.id), {})
        ch_id = conf.get("channel")
        if not ch_id:
            return None
        return guild.get_channel(ch_id)

    def _is_enabled(self, guild: discord.Guild, event: str) -> bool:
        data = self.load_data()
        conf = data.get(str(guild.id), {})
        enabled = conf.get("enabled", [])
        return event in enabled

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not self._is_enabled(member.guild, "member_join"):
            return
        channel = self._get_log_channel(member.guild)
        if not channel:
            return

        embed = discord.Embed(title="Member Joined", color=discord.Color.green())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not self._is_enabled(member.guild, "member_remove"):
            return
        channel = self._get_log_channel(member.guild)
        if not channel:
            return

        embed = discord.Embed(title="Member Left", color=discord.Color.dark_grey())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return
        if not self._is_enabled(message.guild, "message_delete"):
            return
        if message.author and message.author.bot:
            return

        channel = self._get_log_channel(message.guild)
        if not channel:
            return

        content = message.content or "(no content)"
        embed = discord.Embed(title="Message Deleted", color=discord.Color.red())
        embed.add_field(name="Author", value=f"{message.author} ({getattr(message.author, 'id', 'N/A')})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention if message.channel else "Unknown", inline=False)
        embed.add_field(name="Content", value=content[:1024], inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return
        if not self._is_enabled(before.guild, "message_edit"):
            return
        if before.author and before.author.bot:
            return
        if before.content == after.content:
            return

        channel = self._get_log_channel(before.guild)
        if not channel:
            return

        embed = discord.Embed(title="Message Edited", color=discord.Color.orange())
        embed.add_field(name="Author", value=f"{before.author} ({getattr(before.author, 'id', 'N/A')})", inline=False)
        embed.add_field(name="Channel", value=before.channel.mention if before.channel else "Unknown", inline=False)
        embed.add_field(name="Before", value=before.content[:1024] or "(no content)", inline=False)
        embed.add_field(name="After", value=after.content[:1024] or "(no content)", inline=False)
        await channel.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Logs(client))

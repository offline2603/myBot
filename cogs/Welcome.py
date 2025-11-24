import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from json import JSONDecodeError

class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.file_path = os.path.join(os.getcwd(), "welcome.json")

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f, indent=4)

    # utility: load json
    def load_data(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            return {}

    # utility: save json
    def save_data(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    # ------------------------------------------------
    # SLASH COMMAND: Set Welcome Channel
    # ------------------------------------------------
    @app_commands.command(
        name="setwelcomechannel",
        description="Set the channel where welcome messages should be sent."
    )
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        guild_id = str(interaction.guild.id)

        data[guild_id] = data.get(guild_id, {})
        data[guild_id]["channel"] = channel.id

        self.save_data(data)

        embed = discord.Embed(
            title="Welcome Channel Updated",
            description=f"Welcome messages will now be sent in {channel.mention} 🎉",
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed)

    # ------------------------------------------------
    # SLASH COMMAND: Set Welcome Message
    # ------------------------------------------------
    @app_commands.command(
        name="setwelcomemessage",
        description="Set a multi-line welcome message (use {user})."
    )
    async def set_welcome_message(self, interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)

        # Modal for multi-line welcome message
        class WelcomeMessageModal(discord.ui.Modal, title="Set Welcome Message"):
            message = discord.ui.TextInput(
                label="Welcome message",
                style=discord.TextStyle.long,
                placeholder="You can use placeholders like {user} and press Enter for new lines.",
                required=True,
                max_length=2000,
            )

            def __init__(self, parent_cog, guild_id: str):
                super().__init__()
                self.parent_cog = parent_cog
                self.guild_id = guild_id

            async def on_submit(self, modal_interaction: discord.Interaction):
                data = self.parent_cog.load_data()
                data[self.guild_id] = data.get(self.guild_id, {})
                data[self.guild_id]["message"] = self.message.value
                self.parent_cog.save_data(data)

                try:
                    await modal_interaction.response.send_message("Welcome message saved.", ephemeral=True)
                except Exception:
                    # fallback if response already used
                    await modal_interaction.followup.send("Welcome message saved.", ephemeral=True)

        modal = WelcomeMessageModal(self, guild_id)
        await interaction.response.send_modal(modal)

    # ------------------------------------------------
    # SLASH COMMANDS: Set individual embed fields
    # ------------------------------------------------
    @app_commands.command(
        name="setwelcometitle",
        description="Set the title for the welcome embed. Use placeholders."
    )
    async def set_welcome_title(self, interaction: discord.Interaction, title: str):

        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        guild_id = str(interaction.guild.id)

        data[guild_id] = data.get(guild_id, {})
        data[guild_id]["title"] = title
        self.save_data(data)

        await interaction.response.send_message(f"Welcome title set to:\n`{title}`")

    @app_commands.command(
        name="setwelcomefooter",
        description="Set the footer for the welcome embed. Use placeholders."
    )
    async def set_welcome_footer(self, interaction: discord.Interaction, footer: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        guild_id = str(interaction.guild.id)
        data[guild_id] = data.get(guild_id, {})
        data[guild_id]["footer"] = footer
        self.save_data(data)

        await interaction.response.send_message(f"Welcome footer set to:\n`{footer}`")

    @app_commands.command(
        name="setwelcomethumbnail",
        description="Set the thumbnail URL for the welcome embed."
    )
    async def set_welcome_thumbnail(self, interaction: discord.Interaction, url: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        guild_id = str(interaction.guild.id)
        data[guild_id] = data.get(guild_id, {})
        data[guild_id]["thumbnail"] = url
        self.save_data(data)

        await interaction.response.send_message(f"Welcome thumbnail URL set.")

    @app_commands.command(
        name="setwelcomeimage",
        description="Set the large image URL for the welcome embed."
    )
    async def set_welcome_image(self, interaction: discord.Interaction, url: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        guild_id = str(interaction.guild.id)
        data[guild_id] = data.get(guild_id, {})
        data[guild_id]["image"] = url
        self.save_data(data)

        await interaction.response.send_message(f"Welcome image URL set.")

    @app_commands.command(
        name="setwelcomeauthor",
        description="Set the author name for the welcome embed. Use placeholders."
    )
    async def set_welcome_author(self, interaction: discord.Interaction, name: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        guild_id = str(interaction.guild.id)
        data[guild_id] = data.get(guild_id, {})
        data[guild_id]["author_name"] = name
        self.save_data(data)

        await interaction.response.send_message(f"Welcome author name set to:\n`{name}`")

    @app_commands.command(
        name="setwelcomeauthoricon",
        description="Set the author icon URL for the welcome embed."
    )
    async def set_welcome_author_icon(self, interaction: discord.Interaction, url: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need the Manage Server permission to use this command.", ephemeral=True)
            return

        data = self.load_data()
        guild_id = str(interaction.guild.id)
        data[guild_id] = data.get(guild_id, {})
        data[guild_id]["author_icon"] = url
        self.save_data(data)

        await interaction.response.send_message(f"Welcome author icon URL set.")

    # ------------------------------------------------
    # SLASH COMMAND: Show available placeholders
    # ------------------------------------------------
    @app_commands.command(
        name="welcome_variables",
        description="Show placeholders you can use in welcome messages and fields."
    )
    async def welcome_variables(self, interaction: discord.Interaction):
        desc = (
            "Available placeholders you can use in messages, title, footer, and author name:\n"
            "`{user}` - mention the user\n"
            "`{user.name}` - user's username\n"
            "`{user.discriminator}` - user's discriminator (e.g., 1234)\n"
            "`{user.id}` - user's ID\n"
            "`{server}` - server name\n"
            "`{member_count}` - server member count\n"
        )

        await interaction.response.send_message(desc, ephemeral=True)

    # ------------------------------------------------
    # EVENT: Member Joins
    # ------------------------------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        data = self.load_data()
        guild_id = str(member.guild.id)

        if guild_id not in data:
            return

        channel_id = data[guild_id].get("channel")
        welcome_msg = data[guild_id].get("message", "Welcome {user} to the server!")

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        # Prepare welcome embed, allowing customized fields
        guild_conf = data.get(guild_id, {})

        def fmt(text: str) -> str:
            if not text:
                return text
            return (
                text.replace("{user}", member.mention)
                    .replace("{user.name}", member.name)
                    .replace("{user.discriminator}", member.discriminator)
                    .replace("{user.id}", str(member.id))
                    .replace("{server}", member.guild.name)
                    .replace("{member_count}", str(member.guild.member_count))
            )

        title = fmt(guild_conf.get("title", "🎉 Welcome to the Server!"))
        description = fmt(guild_conf.get("message", welcome_msg.replace("{user}", member.mention)))

        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())

        # author
        author_name = fmt(guild_conf.get("author_name", ""))
        author_icon = guild_conf.get("author_icon")
        if author_name:
            try:
                embed.set_author(name=author_name, icon_url=author_icon)
            except Exception:
                embed.set_author(name=author_name)

        # thumbnail (fallback to user's avatar if not set)
        thumbnail_url = guild_conf.get("thumbnail")
        if not thumbnail_url:
            try:
                thumbnail_url = member.display_avatar.url
            except Exception:
                thumbnail_url = None

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        # image
        image_url = guild_conf.get("image")
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception:
                pass

        # footer
        footer_text = fmt(guild_conf.get("footer", f"Member #{member.guild.member_count}"))
        if footer_text:
            embed.set_footer(text=footer_text)

        await channel.send(embed=embed)

    # ------------------------------------------------
    # Helper: format placeholders in text for a given member
    # ------------------------------------------------
    def format_placeholders(self, text: str, member: discord.Member) -> str:
        if text is None:
            return text
        return (
            text.replace("{user}", member.mention)
                .replace("{user.name}", member.name)
                .replace("{user.discriminator}", member.discriminator)
                .replace("{user.id}", str(member.id))
                .replace("{server}", member.guild.name)
                .replace("{member_count}", str(member.guild.member_count))
        )

    # ------------------------------------------------
    # SLASH COMMAND: Preview Welcome Embed
    # ------------------------------------------------
    @app_commands.command(
        name="previewwelcome",
        description="Preview the welcome embed for a user (ephemeral)."
    )
    async def preview_welcome(self, interaction: discord.Interaction, member: discord.Member = None):

        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        member = member or interaction.user

        data = self.load_data()
        guild_id = str(interaction.guild.id)
        guild_conf = data.get(guild_id, {})

        # Build preview using same logic as on_member_join
        title = self.format_placeholders(guild_conf.get("title", "🎉 Welcome to the Server!"), member)
        message_template = guild_conf.get("message", "Welcome {user} to the server!")
        description = self.format_placeholders(guild_conf.get("message", message_template.replace("{user}", member.mention)), member)

        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())

        # author
        author_name = self.format_placeholders(guild_conf.get("author_name", ""), member)
        author_icon = guild_conf.get("author_icon")
        if author_name:
            try:
                embed.set_author(name=author_name, icon_url=author_icon)
            except Exception:
                embed.set_author(name=author_name)

        # thumbnail (fallback to user's avatar if not set)
        thumbnail_url = guild_conf.get("thumbnail")
        if not thumbnail_url:
            try:
                thumbnail_url = member.display_avatar.url
            except Exception:
                thumbnail_url = None

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        # image
        image_url = guild_conf.get("image")
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception:
                pass

        # footer
        footer_text = self.format_placeholders(guild_conf.get("footer", f"Member #{member.guild.member_count}"), member)
        if footer_text:
            embed.set_footer(text=footer_text)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(Welcome(client))

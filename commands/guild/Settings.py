import sys, discord

sys.path.insert(1, sys.path[0].replace("commands/guild", ""))
sys.path.insert(1, sys.path[0].replace("guild", ""))
from utils import Logger, Config, DBManager, CUtils, OAuthHelper
from utils.Config import client
from commands.Guild import guild_group


"""
Other Select Menus
"""

class ChannelSelect(discord.ui.Select):
    def __init__(self, channels, page = 1):
        self.channels = channels[(page-1)*25:(page-1)*25+25]
        self.page = page

        options = []
        for channel in self.channels:
            options.append(discord.SelectOption(label=channel.name, value=str(channel.id), description=f"Channel ID: {channel.id}"))

        super().__init__(placeholder="Select a channel...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Log it
        Logger.info("commands.guild.Settings.ChannelSelect.callback", f"Channel Select called by {interaction.user.name}")

        # Attempt to change it
        try:
            settings = DBManager.get_server_settings(interaction.guild.id)
            settings["authorize_button"]["channel"] = int(self.values[0])
            DBManager.set_server_settings(interaction.guild.id, settings)
        except Exception as e:
            Logger.error("commands.guild.Settings.ChannelSelect.callback", f"Error changing channel: {e}")
            await interaction.response.edit_message(embed=discord.Embed(title=":x: Error Changing Channel", description="There was an error changing the channel. Please try again later.", color=discord.Color.red()), view=None)
            return

        # Send response back
        await interaction.response.edit_message(embed=discord.Embed(title=":white_check_mark: Channel Selected", description=f"Channel selected: <#{self.values[0]}>", color=discord.Color.green()), view=None)

class RoleSelect(discord.ui.Select):
    def __init__(self, roles, page = 1):
        self.roles = roles[(page-1)*25:(page-1)*25+25]
        self.page = page

        options = []
        for role in self.roles:
            options.append(discord.SelectOption(label=role.name, value=str(role.id), description=f"Role ID: {role.id}"))

        super().__init__(placeholder="Select a role...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Log it
        Logger.info("commands.guild.Settings.RoleSelect.callback", f"Role Select called by {interaction.user.name}")

        # Attempt to change it
        try:
            settings = DBManager.get_server_settings(interaction.guild.id)
            settings["authorize_button"]["role"] = int(self.values[0])
            DBManager.set_server_settings(interaction.guild.id, settings)
        except Exception as e:
            Logger.error("commands.guild.Settings.RoleSelect.callback", f"Error changing role: {e}")
            await interaction.response.edit_message(embed=discord.Embed(title=":x: Error Changing Role", description="There was an error changing the role. Please try again later.", color=discord.Color.red()), view=None)
            return

        # Send response back
        await interaction.response.edit_message(embed=discord.Embed(title=":white_check_mark: Role Selected", description=f"Role selected: <@&{self.values[0]}>", color=discord.Color.green()), view=None)


"""
Settings Select Menu
"""
class SettingsSelect(discord.ui.Select):
    def __init__(self, auth_button):
        self.auth_button = auth_button
        options = []

        # Auth button options
        if auth_button:
            options.append(discord.SelectOption(label="Authorize Button", value="auth_button", description="Disable authorize button for this server", emoji="🟢"))
            options.append(discord.SelectOption(label="Authorize Channel", value="auth_channel", description="Change the channel for the authorize button"))
            options.append(discord.SelectOption(label="Authorize Role", value="auth_role", description="Change the role for the authorize button"))
            options.append(discord.SelectOption(label="Authorize Message", value="auth_msg", description="Change the message for the authorize button"))
        else:
            options.append(discord.SelectOption(label="Authorize Button", value="auth_button", description="Enable authorize button for this server", emoji="🔴"))

        super().__init__(placeholder="Select a setting to change...", min_values=1, max_values=1, options=options)


    async def handle_auth_button(self, interaction: discord.Interaction):
        """
        Handle the clicking of the authorize option of the dropdown menu
        Turn off authorize button if it is on, and turn it on if it is off
        """

        settings = DBManager.get_server_settings(interaction.guild.id)

        if self.auth_button:
            settings["authorize_button"]["enabled"] = False
            await interaction.response.edit_message(embed=discord.Embed(title=":x: Authorize Button Disabled", description="The authorize button has been disabled for this server.", color=discord.Color.red()), view=None)
        else:
            settings["authorize_button"]["enabled"] = True
            await interaction.response.edit_message(embed=discord.Embed(title=":white_check_mark: Authorize Button Enabled", description="The authorize button has been enabled for this server.", color=discord.Color.green()), view=None)

        DBManager.set_server_settings(interaction.guild.id, settings)

    async def handle_option(self, option: str, interaction: discord.Interaction):
        """
        Creates a channel select menu for the user to select a channel
        """

        view = discord.ui.View(timeout=60)

        title = ":pencil: Edit a Setting"
        description = "Select a option for the setting to change"

        match option:
            case "auth_channel":
                view.add_item(ChannelSelect(interaction.guild.text_channels))
                title = ":pencil: Select a channel"
                description = "Select a channel for the authorize button to be sent in."

            case "auth_role":
                view.add_item(RoleSelect(interaction.guild.roles))
                title = ":pencil: Select a role"
                description = "Select a role that will be added to the user when they authorize."

            case _:
                await interaction.response.edit_message(embed=discord.Embed(title=":x: Invalid Option", description="This option is not available yet.", color=discord.Color.red()), view=None)


        await interaction.response.edit_message(embed=discord.Embed(title=title, description=description, color=discord.Color.blurple()), view=view)




    # When the user selects an option
    async def callback(self, interaction: discord.Interaction):
        Logger.info("commands.guild.Settings.SettingsSelect.callback", f"Settings Select called by {interaction.user.name}")
        self.disabled = True
        answer = self.values[0]

        match answer:
            case "auth_button":
                await self.handle_auth_button(interaction)
            case _:
                await self.handle_option(answer, interaction)
                


class SettingsSelectView(discord.ui.View):
    def __init__(self, auth_button_enabled):
        self.auth_button = auth_button_enabled
        super().__init__(timeout=60)

        self.add_item(SettingsSelect(self.auth_button))



"""
Actual Commands
"""

@guild_group.command(name="settings", description="View or change your guild settings")
async def settings(interaction: discord.Interaction):
    Logger.info("commands.guild.Settings.settings", f"Settings command called by {interaction.user.name}")
    await interaction.response.defer()

    if(interaction.user.guild_permissions.administrator == False):
        await interaction.response.send_message(embed=discord.Embed(title=":x: Missing Permission: Admin", description="You need the ```Administrator``` permission to use this command.", color=discord.Color.red()))
        return

    if CUtils.check_disabled("guild_settings"):
        await interaction.followup.send(embed=Config.DISCORD_EMBED_COMMAND_DISABLED)
        return
    
    settings = DBManager.get_server_settings(interaction.guild.id)
    
    settings_embed = discord.Embed(title=f"{interaction.guild.name} Settings", color=discord.Color.blurple())

    # Authorize Button Stuff
    if(settings["authorize_button"]["enabled"]):
        settings_embed.description = f"\n\n**Authorize Button**: Enabled :white_check_mark:"
        settings_embed.description += f"\n> **Authorize Channel**: {(await client.fetch_channel(settings['authorize_button']['channel'])).mention}"
        settings_embed.description += f"\n> **Authorize Role**: {settings['authorize_button']['role']}"
        settings_embed.description += f"\n> **Authorize Message**: {settings['authorize_button']['message']}"
        settings_embed.description += f"\n> **Errors**: {settings['authorize_button']['errors']}"
    else:
        settings_embed.description = f"\n\n**Authorize Button**: Disabled :x:"

    

    await interaction.followup.send(embed=settings_embed, view=SettingsSelectView(settings["authorize_button"]["enabled"]))
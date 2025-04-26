# Import packages
import sys, os, discord, asyncio, logging
from discord import app_commands
from discord.ext import commands

# Import custom modules
from utils import Logger, Config, DBManager, CUtils, OAuthHelper
from utils.Config import client, oauthSession
from webserver import app

# Import Commands
from commands import authorize, deauthorize
from commands.guild import settings

# Random one time use functions
def get_path():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        return application_path
    return os.path.dirname(os.path.abspath(__file__))

# Set path for this file
Config.set_path(get_path())

# Button
class AuthorizeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Authorize", style=discord.ButtonStyle.success, emoji="🔒")
    async def authorize(self, interaction: discord.Interaction, button: discord.ui.Button):
        Logger.info("main.AuthorizeButton.authorize", f"Authorize Button Clicked by {interaction.user.name}")
        await authorize(interaction)
        

# On ready event
@client.event
async def on_ready():
    Logger.info("main.on_ready", "Bot is ready")

    # Sync commands
    Logger.info("main.on_ready", f"Synced {len(await client.tree.sync())} commands")

    # Show how many servers it's in
    Logger.info("main.on_ready", f"Currently in {len(client.guilds)} servers")

    # Remove Previous buttons from guilds
    # Add new buttons from guilds
    for guild in client.guilds:
        # Check server settings
        settings = DBManager.get_server_settings(guild.id)

        if not settings["authorize_button"]["enabled"]:
            continue

        # Get all the necessary settings
        authorize_channel = settings["authorize_button"]["channel"]
        prev_button_id = settings["authorize_button"]["prev_button_id"]
        authorize_message = settings["authorize_button"]["message"]

        # Do some formatting
        channel = client.get_channel(authorize_channel)

        if channel is None:
            Logger.warn("main.on_ready", f"Guild: {guild.id} has invalid channel")
            settings["authorize_button"]["enabled"] = False
            settings["authorize_button"]["errors"] = "Invalid Channel"
            DBManager.set_server_settings(guild.id, settings)
            continue

        try:
            prev_button = await channel.fetch_message(prev_button_id)
        except discord.errors.NotFound:
            settings["authorize_button"]["prev_button_id"] = None
            prev_button = None

        if authorize_message == "default_embed":
            authorize_message = Config.DISCORD_EMBED_PERM_AUTHORIZE_BUTTON

        # Attempt to delete the previous button
        try:
            if prev_button is not None:
                await prev_button.delete()
                prev_button_id = None
        except discord.errors.Forbidden:
            Logger.warn("main.on_ready", f"Bot doesn't have perms to delete button in {guild.id}. Please notify guild owner")
        except Exception as err:
            Logger.error("main.on_ready", f"Error deleting button: {err}")

        # Send new button
        try:
            prev_button_id = await channel.send(embed=authorize_message, view=AuthorizeButton())
        except discord.errors.Forbidden:
            Logger.warn("main.on_ready", f"Bot doesn't have perms to send button in {guild.id}. Disabling button setting")
            settings["authorize_button"]["enabled"] = False
            settings["authorize_button"]["errors"] = "Cannot Send Button, Check permissions"
        except Exception as err:
            Logger.error("main.on_ready", f"Error sending button: {err}")

        settings["authorize_button"]["prev_button_id"] = prev_button_id.id

        DBManager.set_server_settings(guild.id, settings)





# disable the stupid auto logger from flask, with the exception of error logging
logging.getLogger("werkzeug").setLevel(logging.ERROR)

os.system("clear")


# Run bot if this is the main file
if __name__ == "__main__":
    DBManager.connect()
    app.run_via_thread()
    client.run(Config.DISCORD_TOKEN)
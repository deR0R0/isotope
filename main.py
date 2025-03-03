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

    # Remove previous buttons

    # Create Button
    channel: discord.TextChannel = await client.fetch_channel(Config.AUTHORIZE_BUTTON_CHANNEL)
    await channel.send(embed=discord.Embed(title=":atom: Authorize to Access the Server", color=discord.Color.green()), view=AuthorizeButton())
    # Create Tasks Loop

# disable the stupid auto logger from flask
logging.getLogger("werkzeug").setLevel(logging.ERROR)

#os.system("clear")


# Run bot if this is the main file
if __name__ == "__main__":
    DBManager.connect()
    app.run_via_thread()
    client.run(Config.DISCORD_TOKEN)
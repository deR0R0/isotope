import sys, discord

sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils import Logger, Config, DBManager, CUtils, OAuthHelper
from utils.Config import client, oauthSession
from utils.Exceptions import *

class AuthorizeButton(discord.ui.View):
    def __init__(self, url, message: discord.InteractionMessage):
        super().__init__(timeout=Config.AUTHORIZE_BUTTON_TIMEOUT)
        self.button = discord.ui.Button(label="Authorize", style=discord.ButtonStyle.url, url=url)
        self.add_item(self.button)
        self.msg = message

    async def on_timeout(self):
        self.button.disabled = True
        await self.msg.edit(embed=discord.Embed(title=":x: Authorize Button Expired", color=discord.Color.red()), view=self)

@client.tree.command(name=Config.COMMAND_AUTHORIZE[0], description=Config.COMMAND_AUTHORIZE[1])
async def authorize_front(interaction: discord.Interaction):
    await authorize(interaction)

async def authorize(interaction: discord.Interaction):
    Logger.info("commands.Authorize.authorize", f"Authorize Command Called by {interaction.user.name}")
    await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Recieved Authorize Request", description="Please wait a moment!", color=discord.Color.green()), ephemeral=True)
    res = await interaction.original_response()

    # Check if command is disabled
    if CUtils.check_disabled("authorize"):
        await res.edit(embed=Config.DISCORD_EMBED_COMMAND_DISABLED)
        return
    
    await res.edit(embed=discord.Embed(title=":atom: Recieved Authorize Request", description="<a:loading:1278333115516850253> Checking whether or not you're already verified... (may take a moment)", color=discord.Color.dark_grey()))
    
    # Check Session
    if OAuthHelper.check_session(interaction.user.id):
        await res.edit(embed=discord.Embed(title=":x: You are already authorized", color=discord.Color.red()))
        return
    
    # Create session
    url, state = oauthSession.authorization_url(Config.ION_AUTHORIZATION_URL)

    # Set user's token to state, that way we can check if the user is authorized
    DBManager.edit_token_user_id(interaction.user.id, state)

    await res.edit(embed=discord.Embed(title=f":atom: Authorize via Ion", description=f"Button Expires in {Config.AUTHORIZE_BUTTON_TIMEOUT} Seconds", color=discord.Color.dark_grey()), view=AuthorizeButton(url, res))
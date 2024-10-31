import sys
import os
import discord
from discord import app_commands
from requests_oauthlib import OAuth2Session

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.OauthManager import OManager

# Create the command class
class authorize:

    # Actual command
    @staticmethod
    async def authorize(interaction: discord.Interaction, originalResponse=None):

        # Log Command that was Ran
        Logger.log(f"{interaction.user} used /authorize")

        # Loading...
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=True)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["authorize"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        # Check if they already connected or not
        if OManager.checkOauthSession(interaction.user.id):
            await originalResponse.edit(embed=discord.Embed(title=":x: Already Connected", color=discord.Color.red()))
            return
        
        # Wrap in try catch statmeent
        try:
            # Create a new oauth session
            oauthUsers[str(interaction.user.id)] = OAuth2Session(client_id=CLIENTID, redirect_uri=oauthLink, scope="read")
            authURL, state = oauthUsers[str(interaction.user.id)].authorization_url("https://ion.tjhsst.edu/oauth/authorize")

            # Set their state so when they authorize, it will link to correct user
            oauthUsers[str(interaction.user.id)] = state
        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
            
        # Send authorize URL back
        await originalResponse.edit(embed=discord.Embed(description=f"[Authorize On Ion]({authURL})"))



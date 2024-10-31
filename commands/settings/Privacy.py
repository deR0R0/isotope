# Imports
import sys
import os
import discord
import json
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
from oauthlib.oauth2 import TokenExpiredError, InvalidGrantError
from requests_oauthlib import OAuth2Session, oauth2_auth

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands/settings", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.SettingsManager import SManager



class privacy:
    # Command
    @staticmethod
    async def privacy(interaction: discord.Interaction, privacy: str, originalResponse=None):

        # Send loading
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=True)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["settings_privacy"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        # Now change their setting
        try:
            # Check if their thing doesn't exist
            res = SManager.changeSetting(interaction.user.id, "privacy", privacy)
            if res == "success":
                discordEmbedSuccessfullyChangedSetting.title = f":white_check_mark: Successfully Changed Privacy to ```{privacy}```"
                await originalResponse.edit(embed=discordEmbedSuccessfullyChangedSetting)
            elif res == "unknownOption":
                discordEmbedUnknownSettingOption.description = f"Please choose options ```{settingOptions["privacy"]}```"
                await originalResponse.edit(embed=discordEmbedUnknownSettingOption)
            else:
                await originalResponse.edit(embed=discordEmbedInternalError)

        except Exception as err:
            Logger.warn(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
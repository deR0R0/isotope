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
sys.path.insert(1, sys.path[0].replace("commands/currency", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.SettingsManager import SManager
from utils.CurrencyManager import CManager

class daily:
    @staticmethod
    async def daily(interaction: discord.Interaction, originalResponse = None):
        # Send loading
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=False)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["currency_daily"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        try:
            response = CManager.claimDailyReward(interaction.user.id)

            if response.isnumeric():
                await originalResponse.edit(embed=discord.Embed(title=f":x: Already Claimed Daily!", description=f"Please wait <t:{response}:R> to claim again!", color=discord.Color.red()))
                return
            
            await originalResponse.edit(embed=discordEmbedClaimedIQ)
        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
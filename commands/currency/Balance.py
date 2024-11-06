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

class balance:
    @staticmethod
    async def balance(interaction: discord.Interaction, originalResponse = None):
        # Send loading
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=False)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["currency_balance"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        try:
            balance = CManager.getMoney(interaction.user.id)
            balanceEmbed = discord.Embed(title=f"{interaction.user.display_name}'s Balance", color=interaction.user.color)
            balanceEmbed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url, url="https://discord.com/vanityurl/dotcom/steakpants/flour/flower/index11.html")
            balanceEmbed.description = f"\n:brain: {balance[0]} IQ\n:bank: {balance[1]} IQ"
            
            await originalResponse.edit(embed=balanceEmbed)
        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
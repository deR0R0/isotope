import sys
import os
import discord
import json
from discord import app_commands

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands/settings", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.SettingsManager import SManager
from utils.OauthManager import OManager

class view:
    @staticmethod
    async def view(interaction: discord.Interaction, originalResponse = None):
        Logger.cmd(f"{interaction.user} used /settings")

        # Loading...
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=False)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["whois"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        try:
            settings = SManager.getSettings(interaction.user.id)

            userSettingEmbed = discord.Embed(title=f"__{interaction.user.display_name}__'s Settings", color=interaction.user.color)
            for setting in settings.keys():
                settingValue = settings[setting]
                userSettingEmbed.add_field(name=f"{setting} (```{settingValue}```)", value=f"{settingsDescriptions[setting]}")

            await originalResponse.edit(embed=userSettingEmbed)
        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)

        
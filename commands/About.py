import sys
import os
import discord
import psutil
from discord import app_commands
from requests_oauthlib import OAuth2Session

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.OauthManager import OManager


process = psutil.Process()

class about:
    @staticmethod
    async def about(interaction: discord.Interaction, originalResponse=None):
        # Loading...
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=False)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["about"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return

        try:
            # Build Embed
            me = await client.fetch_user(668626305188757536)
            embed = discord.Embed(title="About This Bot!", color=me.color)
            embed.set_author(name=me.name, url="https://github.com/deR0R0", icon_url=me.avatar.url)
            embed.add_field(name="CPU Usage", value=f"{process.cpu_percent()}%", inline=False)
            embed.add_field(name="Memory Footprint", value=f"{process.memory_info().rss // (1024*1024)}Mb", inline=False)
            embed.add_field(name="Python Version", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", inline=False)
            embed.add_field(name="Discord.py Version", value=discord.__version__, inline=False)
            await originalResponse.edit(embed=embed)
        except Exception as err:
            Logger.warn(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
        
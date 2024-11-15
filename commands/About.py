import sys
import os
import discord
import psutil
import speedtest
import asyncio
from discord import app_commands
from requests_oauthlib import OAuth2Session
from threading import Thread

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.OauthManager import OManager


process = psutil.Process()

downloadSpeed = 0
uploadSpeed = 0
location = ""

class about:
    @staticmethod
    async def about(interaction: discord.Interaction, originalResponse=None):
        global downloadSpeed
        global uploadSpeed
        global location
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
            # Create Embed
            me = await client.fetch_user(668626305188757536)
            embed = discord.Embed(title="About This Bot!", color=me.color)
            embed.set_author(name=me.name, url="https://github.com/deR0R0", icon_url=me.avatar.url)
            embed.description = f"\n> CPU Usage ```{process.cpu_percent()}%```"
            embed.description = embed.description + f"\n> Memory Used ```{round((process.memory_percent() / 100) * (psutil.virtual_memory().total / (1024*1024)), 2)} MB```"
            embed.description = embed.description + f"\n> Python Version ```{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}```"
            embed.description = embed.description + f"\n> Discord.py Version ```{discord.__version__}```"
            embed.description = embed.description + f"\n> Heartbeat Latency ```{round(client.latency * 1000, 2)}ms```"
            await originalResponse.edit(embed=embed)
        except Exception as err:
            Logger.warn(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
        
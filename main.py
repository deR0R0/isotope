# Discord
import discord
from discord import app_commands
from discord.ext import commands, tasks
# System
import os
import sys
import pathlib
import json
import threading
import random
# Networking and Oauth
import requests
from requests_oauthlib import OAuth2Session
from flask import render_template, Flask, request
import oauthlib
from oauthlib import oauth2
# Time
import time
import datetime
import asyncio
# Colors :O
from colorama import Fore as fore
# Improve speed ..?
from functools import lru_cache

# Import Utilities
from utils.LogManager import Logger
from utils.FileManager import FManager
from utils.RateLimiter import RateLimit
from utils.Configuration import *
from app import WebServer

# Import commands
from commands.Authorize import authorize
from commands.Deauthorize import deauthorize
from commands.WhoIs import whois

# Import Tasks
from tasks.detectVerified import DetectVerified

# Variables
progPath = os.path.dirname(os.path.abspath(__file__))

# Authorize Button
class AuthorizeIon(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Authenticate", style=discord.ButtonStyle.success)
    async def authenticate(self, interaction: discord.Interaction, button: discord.ui.Button):
        Logger.cmd(f"{interaction.user} pressed Authenticate button!")
        await authorize.authorize(interaction)


# Client Events

# On Ready
@lru_cache
@client.event
async def on_ready():
    # Online, Log username
    Logger.log("Bot Online, logged in as: " + str(client.user))
    Logger.log(f"Synced {len(await client.tree.sync())} commands")

    # Delete Previous Buttons
    for server in list(config["serverConfigs"].keys()):
        if config["serverConfigs"][server]["authorizeButton"] != None:
            # Fetch channel and message, then delete
            channel: discord.TextChannel = await client.fetch_channel(config["serverConfigs"][server]["authorizeButton"][0])
            message = await channel.fetch_message(config["serverConfigs"][server]["authorizeButton"][1])
            await message.delete()

            # Send new buttons :)
            channel: discord.TextChannel = await client.fetch_channel(config["serverConfigs"][server]["authorizeChannel"])
            message = await channel.send(embed=discordEmbedConnectAccount, view=AuthorizeIon())
            config["serverConfigs"][server]["authorizeButton"] = [channel.id, message.id]

            # Save Data
            if not FManager.write("config.json", config):
                Logger.warn("There was an exception while saving config.json")
            



    # Start Tasks
    await taskLoop.start()

# Commands
@client.tree.command(name=authorizeName, description=authorizeDescription)
async def mainAuthorize(interaction: discord.Interaction):
    await authorize.authorize(interaction)

@client.tree.command(name=deauthorizeName, description=deauthorizeDescription)
async def mainDeauthorize(interaction: discord.Interaction):
    await deauthorize.deauthorize(interaction)

@client.tree.command(name=whoisName, description=whoisDescription)
async def mainWhoIs(interaction: discord.Interaction):
    await whois.whois(interaction)

# Tasks
@tasks.loop(seconds=3)
async def taskLoop():
    await DetectVerified.detectVerified()


# Set directory for utilities
Logger.setPath(progPath)
FManager.setPath(progPath)
whois.setPath(progPath)

# Load config
config.update(FManager.read("config.json"))

# Run the webserver
WebServer.startWebSever()

# Run the rate limit thread
RateLimit.startRateLimitThread()


client.run(TOKEN)
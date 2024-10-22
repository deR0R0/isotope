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


    # Refresh tokens
    if oauthUsersTokens != None:
        for user in oauthUsersTokens:
            if not isinstance(oauthUsersTokens[user], str):
                oauthUsers[user] = OAuth2Session(client_id=CLIENTID, token=oauthUsersTokens[user])
    else:
        Logger.warn("Missing Tokens")


    try:
        await taskLoop.start()
    except RuntimeError:
        Logger.warn("Task already started")
            

# CLI
@lru_cache
@client.event
async def on_message(message: discord.Message):
    global program_path
    global config

    if message.content.startswith(">isotope"):
        if str(message.author.id) in config["approvedCLIUsers"]:
            args = message.content.split()
            args.pop(0)

            if len(args) == 0:
                await message.reply("Command Must Have Arguments")
                return
            
            # Help
            if args[0].lower() == "help":
                await message.reply("No Help :(")

            # Config
            elif args[0].lower() == "config":
                Logger.log(f"Giving config to {message.author}")
                await message.reply(file=discord.File(f"{progPath}/data/config.json"))
            
            # Logs
            elif args[0].lower() == "logs":
                # Check if args is long enough
                if len(args) == 1:
                    await message.reply("Missing Args: ```[view / append]```")
                    return

                if args[1].lower() == "view":
                    Logger.log(f"Giving logs to {message.author}")
                    await message.reply(file=discord.File(f"{progPath}/data/logs.txt"))
                elif args[1].lower() == "append":
                    # Check if arg long enough
                    
                    # Pull string together
                    msg = ""
                    for arg in args:
                        if arg not in ["logs", "append"]:
                            msg = msg + arg + " "
                    
                    # Log it
                    Logger.log(msg)
                    await message.reply(f'Added "{msg}" to logs')
                elif args[1].lower() == "clear":
                    # Clear the logs
                    FManager.write("logs.txt", "")
                    await message.add_reaction("✅")

                else:
                    # Unknown :(
                    await message.add_reaction("❌")
            
            # Rate Limit
            elif args[0].lower() == "ratelimit":
                Logger.log("ratelimit")
                
            elif args[0].lower() == "cli":
                Logger.log("cli")
            
            elif args[0].lower() == "stop":
                if str(message.author.id) == "668626305188757536":
                    await client.close()

            else:
                await message.reply("Unknown Command")
        
            FManager.write("config.json", config)

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
data = FManager.read("config.json")
if data == None:
    Logger.err("No config.json file found. Please create one. Program will now exit")
    sys.exit()

config.update(data)

# Load tokens
data = FManager.read("tokens.json")
if data != None:
    oauthUsersTokens.update(FManager.read("tokens.json"))

# Run the webserver
WebServer.startWebSever()

# Run the rate limit thread
RateLimit.startRateLimitThread()


client.run(TOKEN)
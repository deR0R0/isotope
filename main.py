# Discord
import discord
from discord import app_commands
from discord.ext import commands, tasks
import typing
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
from commands.About import about
from commands.settings.Privacy import privacy

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
os.system("clear")

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
            try:
                # Fetch channel and message, then delete
                channel: discord.TextChannel = await client.fetch_channel(config["serverConfigs"][server]["authorizeButton"][0])
                message = await channel.fetch_message(config["serverConfigs"][server]["authorizeButton"][1])
                await message.delete()
            except Exception:
                pass

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

    # Load user settings
    userSettings.update(FManager.read("userPreferences.json"))


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

    # Fun responses :D
    if message.content.lower() == "<@1277278355036700843>":
        responses = ["beep boop", "beep boop?", "boop beep", "beep boop ^_^"]
        await message.reply(random.choice(responses))

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
                    await message.reply(f'Added ```{msg}``` to logs')
                elif args[1].lower() == "clear":
                    # Clear the logs
                    FManager.write("logs.txt", "")
                    await message.add_reaction("✅")

                else:
                    # Unknown :(
                    await message.add_reaction("❌")
            
            # Rate Limit
            elif args[0].lower() == "ratelimit":
                # Check enough args
                if len(args) == 1:
                    await message.reply("Require more args! ```[trigger / delay] [seconds]```")
                    return
                # Trigger rate limit
                if args[1] == "trigger":
                    try:
                        config["messagesTriggerLimit"] = args[2]
                        await message.add_reaction("✅")
                    except:
                        await message.add_reaction("❌")
                elif args[1] == "delay":
                    try:
                        config["removeRateLimitTime"] = args[2]
                        await message.add_reaction("✅")
                    except:
                        await message.add_reaction("❌")
                else:
                    await message.reply(f"Invalid Syntax: {args[1]}")

            # Disable Commands
            elif args[0].lower() == "command":
                try:
                    config["enabledCommands"][args[1]] = args[2] == "true"
                except:
                    await message.add_reaction("❌")
                
            elif args[0].lower() == "nuke":
                messagesToDelete = []
                for i in range(10):
                    messagesToDelete.append(await message.channel.send(f"{10-i}"))
                    await asyncio.sleep(1)

                for i in range(10):
                    messagesToDelete.append(await message.channel.send(f"# NUKED BY ISOTOPE, L GET BETTER"))

                for i in messagesToDelete:
                    await i.delete()
                    await asyncio.sleep(0.5)

                
                
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
async def mainWhoIs(interaction: discord.Interaction, user: discord.Member = None):
    await whois.whois(interaction, user)

@client.tree.command(name=aboutName, description=aboutDescription)
async def mainAbout(interaction: discord.Interaction):
    await about.about(interaction)

@settingsGroup.command(name=settings_PrivacyName, description=settings_PrivacyDescription)
@app_commands.describe(value="Set your privacy to public or private")
async def mainSettingsPrivacy(interaction: discord.Interaction, value: str):
    await privacy.privacy(interaction, value)

@lru_cache
@mainSettingsPrivacy.autocomplete("value")
async def mainSettingsPrivacyAutocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = []
    for choice in ["public", "private"]:
        if current.lower() in choice:
            choices.append(app_commands.Choice(name=choice, value=choice))

    return choices

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
    oauthUsersTokens.update(data)

# Load Money
money = FManager.read("userMoney.json")
if money != None:
    userMoney.update(money)

# Run the webserver
WebServer.startWebSever()

# Run the rate limit thread
RateLimit.startRateLimitThread()


client.run(TOKEN)
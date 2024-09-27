# Discord
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
# System
import os
import sys
import pathlib
import json
import threading
import random
# Networking
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


# Declare the client and create intents + token + description
TOKEN = os.environ.get("token")
OAUTHKEY = os.environ.get("oauth")
CLIENTID = os.environ.get("clientid")
intents = discord.Intents().all()
description = "Hello world :P"
client = commands.Bot(command_prefix="/", description=description, intents=intents)

"""
Mini-"Configuration"
"""
discordEmbedInternalError = discord.Embed(title=":x: Internal Error!", color=discord.Color.red())
discordEmbedServerError = discord.Embed(title=":x: Server Error!", color=discord.Color.red())
discordEmbedRateLimited = discord.Embed(title=":x: Rate Limited!", description="You were rate limtied to prevent API overuse 🙃", color=discord.Color.red())
discordEmbedLoading = discord.Embed(title="<a:loadinggif:1278333115516850253> Loading...", color=discord.Color.blurple())
discordEmbedAccountNotConnected = discord.Embed(title=":x: Ion Account Not Connected", description="Tip: Use the /connect_ion command to connect your Ion account!", color=discord.Color.red())
discordEmbedConnectAccount = discord.Embed(title="Authorize Before Accessing this Server!", color=discord.Color.green())
discordEmbedCommandDisabled = discord.Embed(title=":x: Command Disabled!", color=discord.Color.red())
discordEmbedAreYouSure = discord.Embed(title=":thinking: Are You Sure?", color=discord.Color.yellow())


# Default Config Values, please change config.json for config
config = {
    "MESSAGESTRIGGERLIMIT": 2,
    "REMOVERATELIMITTIME": 5,
    "SAVELOGS": True,
    "HIDEINTRUSIVEMESSAGES": False,
    "DISABLEAUTHENTICATION": False,
    "APPROVEDCLIUSERS": [668626305188757536]
}

commandEnabled = {
    "authorize": True,
    "deauthorize": True,
    "profile": True,
    "bot_stats": True
}

"""
Flask Stuff
"""
app = Flask(__name__)
"""
Variables
"""
program_path = None
stats = {
    "commandIssueCount": {
        "schedule": 0
    }
}
FileManager = None
LogManager = None
rateLimitUsers = {}
PRODUCTION = True
oauthLink = "http://localhost:80/authorize" # Put your authorization link here or go into client events and replace that
oauthUsers = {}
oauth = None

"""
███████╗██╗░░░██╗███╗░░██╗░█████╗░████████╗██╗░█████╗░███╗░░██╗░██████╗
██╔════╝██║░░░██║████╗░██║██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██╔════╝
█████╗░░██║░░░██║██╔██╗██║██║░░╚═╝░░░██║░░░██║██║░░██║██╔██╗██║╚█████╗░
██╔══╝░░██║░░░██║██║╚████║██║░░██╗░░░██║░░░██║██║░░██║██║╚████║░╚═══██╗
██║░░░░░╚██████╔╝██║░╚███║╚█████╔╝░░░██║░░░██║╚█████╔╝██║░╚███║██████╔╝
╚═╝░░░░░░╚═════╝░╚═╝░░╚══╝░╚════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═════╝░
"""

# Clearing Terminal
def clearConsole():
    # Clear console, but we have to check for stoop windows / mac / linux inconsists
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

def get_path():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        return application_path
    return os.path.dirname(os.path.abspath(__file__))

# Adding users to the rate limit dictionary
def add_rate_limit(userId: int) -> bool:
    global rateLimitUsers
    global config
    global LogManager

    if userId in rateLimitUsers:
        rateLimitUsers[userId] += 1
    else:
        # If not in the dictionary, add them into it
        rateLimitUsers[userId] = 1

    # Check if the rate limit exceeds
    if rateLimitUsers[userId] > config["MESSAGESTRIGGERLIMIT"]:
        LogManager.log(msg=f"{userId} got rate limited!")
        return True
    # Doesn't exceed rate limit
    return False

    

# Removing user's rate limit!
def rate_limit_remover():
    global rateLimitUsers
    global config

    while True:
        for i in range(len(rateLimitUsers)):
            rateLimitList = list(rateLimitUsers)
            userToRemoveLimit = rateLimitList[i]
            rateLimitUsers[userToRemoveLimit] -= 1
        time.sleep(config["REMOVERATELIMITTIME"])

# Checking if they verified or not
oldOauthusers = {}
@tasks.loop(seconds=3)
async def detectVerified():
    global oauthUsers
    global oldOauthusers

    # What we're doing here is checking if they exist, then check if they are a string (not authenticated) and then if they don't align, then they authenticated
    if oldOauthusers != oauthUsers:
        oldOauthusersList = list(oldOauthusers.keys())
        for i in range(len(oldOauthusersList)):
            if isinstance(oldOauthusers[oldOauthusersList[i]], str):
                if oldOauthusers[oldOauthusersList[i]] != oauthUsers[oldOauthusersList[i]] and not isinstance(oauthUsers[oldOauthusersList[i]], str):
                    x = await client.fetch_user(oldOauthusersList[i])
                    await x.send(embed=discord.Embed(title=":white_check_mark: Verified/Authenticated!"))
                    for guild in client.guilds:
                        if guild in x.mutual_guilds:
                            try:
                                role = discord.utils.get(guild.roles, name="Verified Student")
                            except:
                                LogManager.warn(f"{guild.id} does not have a Verfied Student role! Ignoring Exception")
                                return
                            try:
                                #await guild.get_member(x.id).remove_roles(role)
                                await guild.get_member(x.id).add_roles(role)
                            except:
                                LogManager.warn("Handled a unknown error o_o")

        oldOauthusers = oauthUsers.copy()

# Send the schedule at 6 o clock
@tasks.loop(minutes=1)
async def sendSchedule():
    global lastTimeSentSchedule
    global client
    try:
        currentTime = datetime.datetime.now().strftime("%H:%M")
        if currentTime == "06:30":
            if datetime.datetime.today().weekday() < 5:
                for guild in client.guilds:
                    if str(guild.id) in config["SERVERCONFIGS"]:
                        if "SCHEDULECHANNEL" not in config["SERVERCONFIGS"][str(guild.id)]:
                            LogManager.log(f"{guild.id} does not have a schedule channel set!")
                            return
                        
                        channel = await client.fetch_channel(config["SERVERCONFIGS"][str(guild.id)]["SCHEDULECHANNEL"])
                        # Send an api request
                        statusCode, response = Request(f"https://ion.tjhsst.edu/api/schedule/{datetime.datetime.now().date()}").getData("json")
                        if statusCode == 200:  
                            # Create the title
                            embedTitle: str = response["day_type"]["name"]
                            embedTitle.replace("<br>", "")
                            # Get the color
                            if "blue" in embedTitle.lower():
                                embedColor = discord.Color.blue()
                            elif "red" in embedTitle.lower():
                                embedColor = discord.Color.red()
                            else:
                                embedColor = discord.Color.blurple()
                            # Build the embed
                            embedDate = response["date"]
                            scheduleEmbed = discord.Embed(title=f"{embedTitle} - {embedDate}", description="Blocks you should be going to for this day", color=embedColor)
                            for i in range(len(response["day_type"]["blocks"])):
                                scheduleEmbed.add_field(name=response["day_type"]["blocks"][i]["name"], value=response["day_type"]["blocks"][i]["start"] + " -> " + response["day_type"]["blocks"][i]["end"], inline=False)

                            await channel.send(embed=scheduleEmbed, view=ViewEighth())
                            LogManager.log("Sent the schedule for this morning")

    except Exception as err:
        LogManager.err("Error in send Schedule")
        LogManager.err(err)


"""
░█████╗░██╗░░░░░░█████╗░░██████╗░██████╗███████╗░██████╗
██╔══██╗██║░░░░░██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝
██║░░╚═╝██║░░░░░███████║╚█████╗░╚█████╗░█████╗░░╚█████╗░
██║░░██╗██║░░░░░██╔══██║░╚═══██╗░╚═══██╗██╔══╝░░░╚═══██╗
╚█████╔╝███████╗██║░░██║██████╔╝██████╔╝███████╗██████╔╝
░╚════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═════╝░╚══════╝╚═════╝░
"""

# Requests
class Request:
    def __init__(self, link: str):
        self.link = link

    def getResponse(self):
        LogManager.log(f"Made request to {self.link}")
        response = requests.get(self.link)
        return response

    def getData(self, type: str):
        response = self.getResponse()
        response_code = response.status_code
        if response_code == 200:
            if type == "json":
                response = response.json()
            elif type == "text":
                response = response.text

        response = [response_code, response]
        LogManager.log("Successfully Returned Data")
        return response
# File Manager
class FManager:
    def readFile(self, file: str):
        global program_path
        try:
            with open(rf"{program_path}/{file}", 'r') as fmFile:
                if ".json" in file:
                    return json.load(fmFile)
                elif ".txt" in file:
                    return fmFile.read()
                else:
                    LogManager.warn("Unknown File Type!")
                    return
        except FileNotFoundError:
            LogManager.warn(f"File Not Found: {file}")
            return
        
    def readRawFile(self, file: str):
        global program_path
        try:
            with open(rf"{program_path}/{file}", 'r') as fmFile:
                if ".json" in file:
                    return fmFile
                else:
                    LogManager.warn("Unknown File Type!")
                    return
        except FileNotFoundError:
            LogManager.warn(f"File Not Found: {file}")
            return

    def writeFile(self, file: str, thingToWrite) -> int:
        global program_path
        try:
            with open(rf"{program_path}/{file}", 'w') as fmFile:
                if ".json" in file:
                    json.dump(thingToWrite, fmFile, indent=4)
                    return 200
                elif ".txt" in file:
                    fmFile.write(f"{thingToWrite}")
                    return 200
                else:
                    LogManager.warn("Unknown Error Type")
                    return 500
        except Exception as err:
            LogManager.err("Error while writing to file")
            LogManager.err(err)
            return 500
        
    def appendFile(self, file: str, thingToWrite) -> int:
        global program_path

        try:
            with open(rf"{program_path}/{file}", 'a') as fmFile:
                if ".txt" in file:
                    fmFile.write(f"{thingToWrite}\n")
                    return 200
                else:
                    LogManager.warn("Unknown File Type!")
                    return 500
        except Exception as err:
            LogManager.err(err)
            return 500

# Custom LogManager!
class LogManager:
    def save_logs(self, content: str):
        global FileManager
        global config

        if not config["SAVELOGS"]:
            return

        if FileManager.appendFile(file="logs.txt", thingToWrite=f"{datetime.datetime.now()} | {content}") == 200:
            pass
        else:
            print("Error while saving file")

    def log(self, msg: str):
        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {fore.LIGHTBLUE_EX}INFO | {fore.WHITE}{msg}")
        self.save_logs(content=msg)

    def err(self, msg: str):
        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {fore.RED}ERR  | {msg}")
        self.save_logs(content=msg)

    def warn(self, msg: str):
        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {fore.YELLOW}WARN | {msg}")
        self.save_logs(content=msg)

    def bot(self, msg: str):
        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {fore.LIGHTBLUE_EX}BOT  | {fore.WHITE}{msg}")
        self.save_logs(content=msg)

    def cmd(self, msg: str):
        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {fore.GREEN}CMD  | {fore.WHITE}{msg}")
        self.save_logs(content=msg)
    
# Now discord stuff

# Authorize Button
class AuthorizeIon(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Authenticate", style=discord.ButtonStyle.success)
    async def authenticate(self, interaction: discord.Interaction, button: discord.ui.Button):
        LogManager.cmd(f"{interaction.user} pressed Authenticate button!")
        await actual_authorize(interaction)

# View Profile Button
class ViewProfile(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="View Profile", style=discord.ButtonStyle.blurple)
    async def viewProfile(self, interaction: discord.Interaction, button: discord.ui.Button):
        LogManager.cmd(f"{interaction.user} pressed View Profile button!")
        await actual_profile(interaction)

# View Eighth Period Button
class ViewEighth(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="View Eighth", style=discord.ButtonStyle.blurple)
    async def viewEighth(self, interaction: discord.Interaction, button: discord.ui.Button):
        LogManager.cmd(f"{interaction.user} pressed View Eighth button!")
        # Call the view eighth per async func

# Confirm
class ConfirmationButtons(discord.ui.View):
    def __init__(self, cmd: str, userid: int, msg: discord.Message):
        self.cmd: str = cmd
        self.userid: int = userid
        self.msg: discord.Message = msg
        super().__init__()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def Confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the user who pressed the button is the one that used the command!
        if interaction.user.id != self.userid:
            await interaction.response.send_message(embed=discord.Embed(title=":x: This is not your button!"))
            return
        await self.msg.delete()
        LogManager.cmd(f"{interaction.user} pressed Confirm button for {self.cmd}")
        if self.cmd == "deauth":
            await delete_deauthorize(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def Cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the user who pressed the button is the one that used the command!
        if interaction.user.id != self.userid:
            await interaction.response.send_message(embed=discord.Embed(title=":x: This is not your button!"))
            return
        await self.msg.delete()
        await interaction.response.send_message(embed=discord.Embed(title=":x: Canceled!", color=discord.Color.red()))
# Cancel
        
    



"""
░█████╗░██╗░░░░░██╗███████╗███╗░░██╗████████╗  ███████╗██╗░░░██╗███████╗███╗░░██╗████████╗░██████╗
██╔══██╗██║░░░░░██║██╔════╝████╗░██║╚══██╔══╝  ██╔════╝██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔════╝
██║░░╚═╝██║░░░░░██║█████╗░░██╔██╗██║░░░██║░░░  █████╗░░╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░╚█████╗░
██║░░██╗██║░░░░░██║██╔══╝░░██║╚████║░░░██║░░░  ██╔══╝░░░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░░╚═══██╗
╚█████╔╝███████╗██║███████╗██║░╚███║░░░██║░░░  ███████╗░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██████╔╝
░╚════╝░╚══════╝╚═╝╚══════╝╚═╝░░╚══╝░░░╚═╝░░░  ╚══════╝░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═════╝░
"""
@client.event
async def on_ready():
    global program_path
    global stats
    global PRODUCTION
    global oauthLink
    global oauth
    
    # Print out bot stats
    LogManager.log("Bot Online")
    LogManager.bot(f"Logged In As: {client.user}")

    # Sync the bot commands
    commandsSynced = await client.tree.sync()
    LogManager.bot(f"Synced {len(commandsSynced)} commands!")

    # Check what 
    if PRODUCTION:
        oauthLink = "https://isotope.sites.tjhsst.edu/authorize"

    

    try:
        # Delete the last buttons and then send the new ones
        if "PREVIOUSBUTTONS" in config:
            for channelNMessage in config["PREVIOUSBUTTONS"]:
                channel: discord.TextChannel = await client.fetch_channel(channelNMessage[0])
                message: discord.Message = await channel.fetch_message(channelNMessage[1])
                await message.delete()
            config["PREVIOUSBUTTONS"] = []
        
        FileManager.writeFile("config.json", config)

        for guild in client.guilds:
            if str(guild.id) in config["SERVERCONFIGS"]:
                if "AUTHORIZECHANNEL" in config["SERVERCONFIGS"][str(guild.id)] and config["SERVERCONFIGS"][str(guild.id)]["AUTHORIZECHANNEL"] != None:
                    authChannel = await client.fetch_channel(config["SERVERCONFIGS"][str(guild.id)]["AUTHORIZECHANNEL"])
                    msg: discord.Message = await authChannel.send(embed=discordEmbedConnectAccount, view=AuthorizeIon())
                    config["PREVIOUSBUTTONS"].append([str(authChannel.id), str(msg.id)])
                
        FileManager.writeFile("config.json", config)
    except Exception as err:
        if "Unknown Message" in str(err):
            config["PREVIOUSBUTTONS"] = []
            FileManager.writeFile("config.json", config)
        else:
            LogManager.warn(err)

    await detectVerified.start()



# CLI
@client.event
async def on_message(message: discord.Message):
    global program_path
    global config

    if message.content.startswith(">isotope"):
        if str(message.author.id) in config["APPROVEDCLIUSERS"]:
            args = message.content.split()
            args.pop(0)

            if len(args) == 0:
                await message.reply("Command Must Have Arguments")
                return

            if args[0].lower() == "help":
                helpEmbed = discord.Embed(title="CLI Commands", color=discord.Color.green())
                helpEmbed.add_field(name="**config**", value="```No More Args``` Returns config", inline=False)
                helpEmbed.add_field(name="**intrusive**", value="```[true / false]``` Changes intrusive messages", inline=False)
                helpEmbed.add_field(name="**ratelimit**", value="```[trigger / delay] [secs]``` Changes rate limit settings", inline=False)
                helpEmbed.add_field(name="**cli**", value="```[add / remove] [user id]``` Adds a cli-approved member", inline=False)
                helpEmbed.add_field(name="**reset**", value="```No More Args``` Resets config", inline=False)
                
                await message.reply(embed=helpEmbed, delete_after=10)
            
            elif args[0].lower() == "config":
                LogManager.bot("Viewing Config")
                with open(rf"{program_path}/config.json", 'r') as configFile:
                    LogManager.bot("Gave config values to Roro :)")
                    await message.reply(file=discord.File(configFile))
                    configFile.close()
                return
            
            elif args[0].lower() == "logs":
                LogManager.bot(f"Returning Logs to {message.author.id}")
                with open(rf"{program_path}/logs.txt", 'r') as logFile:
                    await message.reply(file=discord.File(logFile))
                    logFile.close()
                return
            
            elif args[0] == "channel":
                if args[1] == "schedule":
                    if args[2] == "set":
                        config["SERVERCONFIGS"][str(message.guild.id)]["SCHEDULECHANNEL"] = str(message.channel.id)
                        await message.add_reaction("✅")
                    elif args[2] == "reset":
                        config["SERVERCONFIGS"][str(message.guild.id)]["SCHEDULECHANNEL"] = None
                        await message.add_reaction("✅")
                    else:
                        await message.reply("Missing Argument: ```set/reset```")
                elif args[1] == "authorize":
                    if args[2] == "set":
                        config["SERVERCONFIGS"][str(message.guild.id)]["AUTHORIZECHANNEL"] = str(message.channel.id)
                        await message.add_reaction("✅")
                    elif args[2] == "reset":
                        config["SERVERCONFIGS"][str(message.guild.id)]["AUTHORIZECHANNEL"] = None
                        await message.add_reaction("✅")
                    else:
                        await message.reply("Missing Argument: ```set/reset```")

                elif args[1] == "reset":
                    config["SERVERCONFIGS"][str(message.guild.id)]["AUTHORIZECHANNEL"] = None
                    config["SERVERCONFIGS"][str(message.guild.id)]["SCHEDULECHANNEL"] = None
                    await message.add_reaction("✅")

                else:
                    await message.reply("Missing Arguments! ```schedule/authorize/reset```")

            elif args[0].lower() == "intrusive":
                config["HIDEINTRUSIVEMESSAGES"] = "true" in args[1]
                await message.add_reaction("✅")

            elif args[0].lower() == "ratelimit":
                if args[1].lower() == "trigger":
                    config["MESSAGESTRIGGERLIMIT"] = int(args[2])
                    await message.add_reaction("✅")
                elif args[1].lower() == "delay":
                    config["REMOVERATELIMITTIME"] = int(args[2])
                    await message.add_reaction("✅")
                else:
                    await message.reply("Missing Arguments: ```<trigger / delay> <integer (seconds)>")
                    return
            elif args[0].lower() == "cli":
                if args[1].lower() == "add":
                    config["APPROVEDCLIUSERS"].append(str(args[2]))
                    await message.add_reaction("✅")
                elif args[1].lower() == "remove":
                    config["APPROVEDCLIUSERS"].remove(str(args[2]))
                    await message.add_reaction("✅")
                else:
                    await message.reply("Missing Arguments: ```<add / remove> <integer (userid)>```")
                    return
            elif args[0].lower() == "command":
                if str(args[1]) in commandEnabled:
                    commandEnabled[str(args[1])] = args[2].lower() == "true"
                    await message.add_reaction("✅")
                else:
                    await message.reply("Command Doesn't Exist or Isn't Implmeneted!")
            
            elif args[0].lower() == "stop":
                if str(message.author.id) == "668626305188757536":
                    await client.close()
                    
            elif args[0].lower() == "reset":
                config = {
                    "MESSAGESTRIGGERLIMIT": 2,
                    "REMOVERATELIMITTIME": 5,
                    "SAVELOGS": False,
                    "HIDEINTRUSIVEMESSAGES": False,
                    "APPROVEDCLIUSERS": [668626305188757536]
                }
                await message.add_reaction("✅")
            elif args[0].lower() == "say":
                args.pop(0)
                messageToSay = "```"
                for arg in args:
                    messageToSay = messageToSay + arg + " "
                messageToSay = messageToSay + "```" + f"- {message.author.mention}"
                await message.channel.send(messageToSay)
            else:
                await message.reply("Unknown Command")
        
            status = FileManager.writeFile('config.json', config)
            if status == 200:
                LogManager.log("Successfully saved config")
            elif status == 500:
                LogManager.err("Unsuccessfully saved config")
            else:
                await message.reply("Unknown Status Code")


    if message.author != client.user:
        await sendSchedule()





"""
░█████╗░██╗░░░░░██╗███████╗███╗░░██╗████████╗  ░█████╗░░█████╗░███╗░░░███╗███╗░░░███╗░█████╗░███╗░░██╗██████╗░░██████╗
██╔══██╗██║░░░░░██║██╔════╝████╗░██║╚══██╔══╝  ██╔══██╗██╔══██╗████╗░████║████╗░████║██╔══██╗████╗░██║██╔══██╗██╔════╝
██║░░╚═╝██║░░░░░██║█████╗░░██╔██╗██║░░░██║░░░  ██║░░╚═╝██║░░██║██╔████╔██║██╔████╔██║███████║██╔██╗██║██║░░██║╚█████╗░
██║░░██╗██║░░░░░██║██╔══╝░░██║╚████║░░░██║░░░  ██║░░██╗██║░░██║██║╚██╔╝██║██║╚██╔╝██║██╔══██║██║╚████║██║░░██║░╚═══██╗
╚█████╔╝███████╗██║███████╗██║░╚███║░░░██║░░░  ╚█████╔╝╚█████╔╝██║░╚═╝░██║██║░╚═╝░██║██║░░██║██║░╚███║██████╔╝██████╔╝
░╚════╝░╚══════╝╚═╝╚══════╝╚═╝░░╚══╝░░░╚═╝░░░  ░╚════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░╚═════╝░
"""


# Schedule
@client.tree.command(name="schedule", description="Sends the classes you should be going to with timestamps")
@app_commands.describe(date="Specific date to see the schedule. Format: MM-DD-YYYY")
async def schedule(interaction: discord.Interaction, date: str=None):
    global program_path
    global config

    LogManager.cmd(f"{interaction.user} used /schedule!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # Check if date is in the correct format
        if date == None:
            date = datetime.datetime.now().date()
        elif date.lower() == "tmr" or "tomorrow":
            date = datetime.datetime.now().date() + datetime.timedelta(1)
        else:
            if len(date) != 10:
                await originalResponse.edit(embed=discord.Embed(title=":x: Invalid Date!", description="Format: MM-DD-YYYY", color=discord.Color.red()))
                return
            dateMonth = int(date[:2])
            dateDay = int(date[3:5])
            dateYear = date[6:10]
            if dateMonth > 12 or dateMonth < 1:
                await originalResponse.edit(embed=discord.Embed(title=":x: Invalid Date!", description="Format: MM-DD-YYYY", color=discord.Color.red()))
                return
            if dateDay > 31 or dateDay < 1:
                await originalResponse.edit(embed=discord.Embed(title=":x: Invalid Date!", description="Format: MM-DD-YYYY", color=discord.Color.red()))
                return
            if len(dateYear) != 4:
                await originalResponse.edit(embed=discord.Embed(title=":x: Invalid Date!", description="Format: MM-DD-YYYY", color=discord.Color.red()))
                return
            date = f"{dateYear}-{dateMonth}-{dateDay}"
        # Get the data
        scheduleResponse = Request(f"https://ion.tjhsst.edu/api/schedule/{date}").getData("json")
        # If the server had issue or whatever, return as server error!
        if scheduleResponse[0] != 200:
            LogManager.warn("Server may be down, please check or fix bot code")
            discordEmbedServerError.description = f"Status Code: {scheduleResponse[0]}"
            originalResponse = await originalResponse.edit(embed=discordEmbedServerError)
            return
        
        # Format the data by building embed
        if "day_type" in scheduleResponse[1]:
            scheduleData = scheduleResponse[1]["day_type"]
            schedulePeriod = scheduleData["blocks"]
            scheduleName: str = scheduleData["name"] + " " + str(date)
            if "<br>" in scheduleName:
                scheduleName = scheduleName.replace("<br>", " ")
            if "red" in scheduleName.lower():
                embedColor = discord.Color.red()
            elif "blue" in scheduleName.lower():
                embedColor = discord.Color.blue()
            else:
                embedColor = discord.Color.blurple()
            schedule = discord.Embed(title=scheduleName, color=embedColor)
            for i in range(len(scheduleData["blocks"])):
                startTime = schedulePeriod[i]["start"]
                endTime = schedulePeriod[i]["end"]
                schedule.add_field(name=schedulePeriod[i]["name"], value=f"{startTime} - {endTime}", inline=False)
        else:
            await originalResponse.edit(embed=discord.Embed(title=":x: Not Supported Schedule", color=discord.Color.red()))
            return

        # Return the data
        await originalResponse.edit(embed=schedule)

        # Free up memory
        originalResponse = None
        scheduleResponse = None
        scheduleData = None
        schedulePeriod = None
        scheduleName = None
        embedColor = None
        schedule = None
        startTime = None
        endTime = None
        dateMonth = None
        dateDay = None
        dateYear = None
    except Exception as err:
        LogManager.err("Exception at /schedule command!")
        LogManager.err(err)
        await originalResponse.edit(content="", embed=discordEmbedInternalError)


# ION CONNECTOR/AUTHENTICATOR
@client.tree.command(name="authorize", description="Connect your discord account to Ion! (for this bot)")
async def authorize(interaction: discord.Interaction):
    await actual_authorize(interaction)

async def actual_authorize(interaction: discord.Interaction):
    global program_path
    global config
    global OAUTHKEY
    global CLIENTID
    global oauthLink

    LogManager.cmd(f"{interaction.user} used /authorize!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=True)
        originalResponse = await interaction.original_response()

        # Check for verification disable
        if config["DISABLEAUTHENTICATION"]:
            await originalResponse.edit(embed=discord.Embed(title=":x: Authentication is currently disabled!"))
            return

        # Check if they already have and check if they in it in the first place
        if str(interaction.user.id) in oauthUsers:
            if not isinstance(oauthUsers[str(interaction.user.id)], str):
                await originalResponse.edit(embed=discord.Embed(title=":x: You already have an account linked!", color=discord.Color.red()))
                return

        # -- Command Logic --
        LogManager.log(f"Generated a verification link for {interaction.user}")
        oauthUsers[str(interaction.user.id)] = OAuth2Session(client_id=CLIENTID, redirect_uri=oauthLink, scope="read")
        authURL, state = oauthUsers[str(interaction.user.id)].authorization_url("https://ion.tjhsst.edu/oauth/authorize")
        oauthUsers[str(interaction.user.id)] = state
        await originalResponse.edit(embed=discord.Embed(title=f"Do NOT Share this Link!", description=f"[Proceed To Ion]({authURL})"))
                                    
        # Free up memory
        originalResponse = None
        authURL = None
        state = None
        
    except Exception as err:
        LogManager.err("Exception at /authorize command!")
        LogManager.err(err)
        if originalResponse != None:
            await originalResponse.edit(content="", embed=discordEmbedInternalError)


# Profile
@client.tree.command(name="profile", description="Sends data thats associated with your Ion account")
@app_commands.describe(user="Specify a member to see their Ion profile")
async def profile(interaction: discord.Interaction, user: discord.Member=None):
    await actual_profile(interaction, user)

async def actual_profile(interaction: discord.Interaction, user: discord.Member=None):
    global program_path
    global config
    global CLIENTID
    global commandEnabled

    LogManager.cmd(f"{interaction.user} used /profile!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.bot(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    # Command Enabled?
    if not commandEnabled["profile"]:
        LogManager.cmd("/profile command disabled!")
        await interaction.response.send_message(embed=discordEmbedCommandDisabled)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # Have to turn the member into thing
        member = interaction.user
        if user != None:
            member = user

        # -- Command Logic --

        # Check if they have an account connected
        if str(member.id) not in oauthUsers:
            print(oauthUsers)
            await originalResponse.edit(embed=discordEmbedAccountNotConnected)
            return
        
        # If they are in it, now check if they actually authicated
        if isinstance(oauthUsers[str(member.id)], str):
            await originalResponse.edit(embed=discordEmbedAccountNotConnected)
            return
        
        # Now fetch the data. If the token is expired, it should be handled
        profile = oauthUsers[str(member.id)].get("https://ion.tjhsst.edu/api/profile")
        profile = json.loads(profile.content.decode())

        profileEmbed = discord.Embed(title=profile["ion_username"], description="Details about this user's ion profile", color=interaction.user.color)
        if member.avatar != None:
            profileEmbed.set_author(name=member, url=member.avatar.url)
        profileEmbed.add_field(name="First Name", value=profile["full_name"].split(' ', 1)[0], inline=False)
        profileEmbed.add_field(name="Counselor", value=profile["counselor"]["full_name"], inline=False)
        profileEmbed.add_field(name="Grade", value=profile["grade"]["number"], inline=False)
        profileEmbed.add_field(name="Grad Year", value=str(profile["graduation_year"]), inline=False)
        profileEmbed.add_field(name="Sysadmin", value=profile["is_eighth_admin"], inline=False)
        # Some disgusting azz if statements but whatever, it works :P
        if member.avatar != None:
            profileEmbed.set_thumbnail(url=member.avatar.url)
        else:
            profileEmbed.set_thumbnail(url=f"https://cdn.discordapp.com/embed/avatars/{random.randint(0, 4)}.png")

        if user != None:
            if interaction.user.avatar == None:
                link = f"https://cdn.discordapp.com/embed/avatars/{random.randint(0, 4)}.png"
            else:
                link = interaction.user.avatar.url
            profileEmbed.set_footer(text=f"Requested By {interaction.user}", icon_url=link)

        await originalResponse.edit(embed=profileEmbed, view=ViewProfile())


        # Free up memory
        originalResponse = None
        profile = None
        member = None
        link = None

    except oauth2.TokenExpiredError:
        LogManager.warn("User has an expired token, refreshing token")
        args = { "client_id": CLIENTID, "client_secret": OAUTHKEY}
        oauthUsers[str(interaction.user.id)].refresh_token("https://ion.tjhsst.edu/oauth/token", **args)
        actual_profile(interaction)

    except Exception as err:
        LogManager.err("Exception at /profile command!")
        LogManager.err(err)
        if originalResponse != None:
            await originalResponse.edit(content="", embed=discordEmbedInternalError)


@client.tree.command(name="deauthorize", description="Unlink your Ion account")
async def deauthorize_confirmation(interaction: discord.Interaction):
    global program_path
    global config
    global commandEnabled

    LogManager.cmd(f"{interaction.user} used /deauthorize!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # Check if command is disabled
        if not commandEnabled["deauthorize"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Check if they are authorized in the first place
        if str(interaction.user.id) in oauthUsers:
            if isinstance(oauthUsers[str(interaction.user.id)], str):
                await originalResponse.edit(embed=discordEmbedAccountNotConnected)
                return
        else:
            await originalResponse.edit(embed=discordEmbedAccountNotConnected)
            return
        # Send them a confirmation button
        await originalResponse.edit(embed=discordEmbedAreYouSure, view=ConfirmationButtons("deauth", interaction.user.id, originalResponse))
        # Free up memory
        originalResponse = None
        
    except Exception as err:
        LogManager.err("Exception at /template command!")
        LogManager.err(err)
        await originalResponse.edit(content="", embed=discordEmbedInternalError)
# The actual delete process!
async def delete_deauthorize(interaction: discord.Interaction):
    global program_path
    global config

    LogManager.cmd(f"{interaction.user}'s account is getting deleted!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # Remove them from the oauth session, this is not the proper way to revoke session but its whatever, gotta implement this quick!
        del oauthUsers[str(interaction.user.id)]
        # Send Response
        await originalResponse.edit(embed=discord.Embed(title=":white_check_mark: Successfully Deleted All Data", description=":( Sad to see you go!", color=discord.Color.blue()))
        # Free up memory
        originalResponse = None
    
    except KeyError:
        LogManager.err("Tried to delete a user that doesn't exist!")
        if originalResponse != None:
            await originalResponse.edit(content="", embed=discordEmbedAccountNotConnected)
        
    except Exception as err:
        LogManager.err("Exception at /template command!")
        LogManager.err(err)
        if originalResponse != None:
            await originalResponse.edit(content="", embed=discordEmbedInternalError)

@client.tree.command(name="bot_stats", description="Bot Stats")
async def test(interaction: discord.Interaction):
    global program_path
    global config

    LogManager.cmd(f"{interaction.user} used /bot_stats!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # Get versions
        pythonVersion = sys.version
        firstStepTime = time.time_ns()
        pythonSpeed = str(round((time.time_ns() - firstStepTime)))
        discordpyVersion = discord.__version__
        userMadeBy: discord.User = await client.fetch_user(668626305188757536)
        # Now test internet speed
        timeBeforeRequest = time.time_ns()
        requests.get("https://httpbin.org/anything/sigma")
        roundTripInternetSpeed = str(round((time.time_ns() - timeBeforeRequest) // 1000000))
        # Build embed
        botstatsEmbed = discord.Embed(title="Bot Stats", description="Pretty cool stats about this discord bot!")
        botstatsEmbed.add_field(name="**Python Version**", value=f"{pythonVersion}", inline=False)
        botstatsEmbed.add_field(name="**Python Speed**", value=f"{pythonSpeed}ns", inline=False)
        botstatsEmbed.add_field(name="**Discord.py Version**", value=f"{discordpyVersion}", inline=False)
        botstatsEmbed.add_field(name="**Internet Speed (kinda)**", value=f"{roundTripInternetSpeed}ms roundtrip for 5 bytes of data", inline=False)
        botstatsEmbed.add_field(name="**Made By**", value=userMadeBy.global_name, inline=False)
        # Send Results
        await originalResponse.edit(embed=botstatsEmbed)
        # Free up memory
        pythonVersion = None
        firstStepTime = None
        pythonSpeed = None
        discordpyVersion = None
        userMadeBy = None
        originalResponse = None
        botstatsEmbed = None
        timeBeforeRequest = None
        roundTripInternetSpeed = None
        
    except Exception as err:
        LogManager.err("Exception at /bot_stats command!")
        LogManager.err(err)
        await originalResponse.edit(content="", embed=discordEmbedInternalError)

# TOS
@client.tree.command(name="tos", description="Terms of Service")
async def test(interaction: discord.Interaction):
    global program_path
    global config

    LogManager.cmd(f"{interaction.user} used /tos!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # Build Embed
        tosEmbed = discord.Embed(title="Terms of Service", description="By using this bot, you agree to these terms.")
        tosEmbed.add_field(name=":one: Exploits", value="\n>>> If you find any bugs that are data-exposing, you MUST report it to a bot developer", inline=False)
        tosEmbed.add_field(name=":two: Your Data", value="\n>>> Use the /privacy to get details on it", inline=False)
        tosEmbed.add_field(name=":three: Rate Limits", value="\n>>> To prevent the overuse of API and the bot, there is a rate limit system in place. CLI approved users will be able to change this", inline=False)
        tosEmbed.add_field(name=":four: Complaints?", value="\n>>> Just send a ping to @deroro_ and I might just fix it.", inline=False)
        tosEmbed.add_field(name=":five: Ion TOS", value="\n>>> You need to comply with Ion TOS as well", inline=False)
        tosEmbed.add_field(name=":six: Open-Source Software", value=">>> This discord bot is open sourced! It's on github and contributions are welcome! :relaxed:")
        # Send Results
        await originalResponse.edit(embed=tosEmbed)
        # Free up memory
        tosEmbed = None
        originalResponse = None
        
    except Exception as err:
        LogManager.err("Exception at /tos command!")
        LogManager.err(err)
        if originalResponse != None:
            await originalResponse.edit(content="", embed=discordEmbedInternalError)

# TOS
@client.tree.command(name="privacy", description="Privacy Policy")
async def test(interaction: discord.Interaction):
    global program_path
    global config

    LogManager.cmd(f"{interaction.user} used /privacy!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # Build Embed
        priEmbed = discord.Embed(title="Privacy Policy", description="By using this bot, you agree to these terms")
        priEmbed.add_field(name=":one: Data Being Stored", value="\n>>> Data that is stored includes, your discord user ID and your Ion oauth2 session", inline=False)
        priEmbed.add_field(name=":two: Data Collection", value="\n>>> Dawg, its a discord bot. The only data I'm collecting is your username/id for debugging purposes...", inline=False)
        priEmbed.add_field(name=":three: Data Security", value="\n>>> It's stored in an unencrypted json file. JK only sensitive thing is your oauth session; which is stored in memory (RAM)", inline=False)
        priEmbed.add_field(name=":four: Delete Your Data", value="\n>>> If you want, you can use the /deauthorize command anytime to delete your data!", inline=False)
        # Send Results
        await originalResponse.edit(embed=priEmbed)
        # Free up memory
        priEmbed = None
        originalResponse = None
        
    except Exception as err:
        LogManager.err("Exception at /privacy command!")
        LogManager.err(err)
        if originalResponse != None:
            await originalResponse.edit(content="", embed=discordEmbedInternalError)



"""!
@client.tree.command(name="template_command", description="template command")
@app_commands.describe(date="test?")
async def test(interaction: discord.Interaction, test: str=None):
    global program_path
    global config

    LogManager.cmd(f"{interaction.user} used /test!")

    # Rate Limiter
    if add_rate_limit(interaction.user.id):
        LogManager.log(f"{interaction.user} was rate limited")
        await interaction.response.send_message(embed=discordEmbedRateLimited)
        return
    
    try:
        # Now we send a response that alerts the user that their request has been processed 
        await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=config["HIDEINTRUSIVEMESSAGES"])
        originalResponse = await interaction.original_response()

        # -- Command Logic --

        # Send Results

        # Free up memory
        originalResponse = None
        
    except Exception as err:
        LogManager.err("Exception at /template command!")
        LogManager.err(err)
        await originalResponse.edit(content="", embed=discordEmbedInternalError)
"""


"""
░██╗░░░░░░░██╗███████╗██████╗░░██████╗██╗████████╗███████╗
░██║░░██╗░░██║██╔════╝██╔══██╗██╔════╝██║╚══██╔══╝██╔════╝
░╚██╗████╗██╔╝█████╗░░██████╦╝╚█████╗░██║░░░██║░░░█████╗░░
░░████╔═████║░██╔══╝░░██╔══██╗░╚═══██╗██║░░░██║░░░██╔══╝░░
░░╚██╔╝░╚██╔╝░███████╗██████╦╝██████╔╝██║░░░██║░░░███████╗
░░░╚═╝░░░╚═╝░░╚══════╝╚═════╝░╚═════╝░╚═╝░░░╚═╝░░░╚══════╝
"""

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/authorize')
def authorize():
    global oauthUsers
    # If the code doesn't exist
    if len(request.args) == 0:
        return "Go to discord and click on the link"
    # Get auth code and token
    try:
        auth_code = request.args.get("code")
        state = request.args.get("state")
        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {fore.LIGHTBLUE_EX}SERV | {fore.WHITE}Recieved Get Request for {auth_code}")
        oauth = OAuth2Session(client_id=CLIENTID, redirect_uri=oauthLink, scope="read")
        token = oauth.fetch_token("https://ion.tjhsst.edu/oauth/token", code=auth_code, client_secret=OAUTHKEY)
    except oauthlib.oauth2.InvalidGrantError:
        return {"Error": "Invalid Token, go back to discord!"}
    except Exception as err:
        print(err)
        return "An Unexpected Error has occured! Ping @deroro_ with the follow: " + str(err)
    
    # Now match and set
    oauthusersList = list(oauthUsers)
    for i in range(len(oauthusersList)):
        if oauthUsers[oauthusersList[i]] == state:
            oauthUsers[oauthusersList[i]] = oauth
            print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {fore.LIGHTBLUE_EX}SERV | {fore.WHITE}Successfully added user!")

    oauthusersList = None
    oauth = None
    token = None
    auth_code = None
    state = None
    return render_template("success.html")



def run():
    app.run(host="0.0.0.0", port=80)

def run_thread():
    global t
    t = threading.Thread(target=run)
    t.start()





# Initianlize a bunch of classes and the rate limiter
program_path = get_path()
FileManager = FManager()
LogManager = LogManager()
# Clear terminal
clearConsole()
# Then load the config
configValues = FileManager.readFile("config.json")
if config == None:
    LogManager.warn("Missing File.. Using default values! Please create a config file next time!!!")
    pass
else:
    config = configValues
    configValues = None


# First check for an internet connection/internet speed
testInternetConnectionStart = time.time_ns()
try:
    if Request("https://httpbin.org/status/200").getData("text")[0] == 200:
        # This is if there is an internet connection
        LogManager.log("Test for internet connection successful!")
        testInternetConnectionEnd = time.time_ns()
        testInternetConnectionSpeed = (testInternetConnectionEnd - testInternetConnectionStart) // 1000000
        LogManager.log(f"Took {testInternetConnectionSpeed}ms for roundtrip")
        if testInternetConnectionSpeed > 1000:
            LogManager.warn("Roundtrip speed took >1000ms. Response times will be slow. Please find better internet or stop using hotspot...")
        pass
except requests.exceptions.ConnectionError:
    LogManager.err("Connection to httpbin.org/status/200 was not successful. Check internet connnection or firewall")
    print(f"{fore.WHITE}Make sure internet is connected (or check your firewall)")
    input("[ACKNOWLEDGE]")
    sys.exit()
except Exception as err:
    LogManager.err(msg=f"Unknown Error: {err}")



# Threads
rateLimitThread = threading.Thread(target=rate_limit_remover)
rateLimitThread.start()


run_thread()
client.run(TOKEN)

sys.exit()
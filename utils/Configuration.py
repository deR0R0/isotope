# Imports
import discord
import os
import sys
from discord import app_commands
from discord.ext import commands
from utils.LogManager import Logger

# Secret Tokens
TOKEN = os.environ.get("token")
OAUTHKEY = os.environ.get("oauth")
CLIENTID = os.environ.get("clientid")

# Declare the client and create intents + token + description
intents = discord.Intents().all()
client = commands.Bot(command_prefix="/", description="description", intents=intents)

# Oauth Stuff
oauthUsers = {}
oauthUsersTokens = {}
oauthLink = "http://localhost:80/authorize"

# Rate Limit Stuff
rateLimitUsers = {}

# Config
config = {}

# User Preferences
userSettings = {}
defaultUserSettings = {
    "privacy": "private"
}

settingOptions = {
    "privacy": ["private", "public"]
}

# User Currency Stuff
userMoney = {}

# Discord Embeds
discordEmbedInternalError = discord.Embed(title=":x: Internal Error!", color=discord.Color.red())
discordEmbedServerError = discord.Embed(title=":x: Server Error!", color=discord.Color.red())
discordEmbedRateLimited = discord.Embed(title=":x: Rate Limited!", description="You've Been Rate Limited! 🙃", color=discord.Color.red())
discordEmbedLoading = discord.Embed(title="<a:loadinggif:1278333115516850253> Loading...", color=discord.Color.blurple())
discordEmbedAccountNotConnected = discord.Embed(title=":x: Ion Account Not Connected", description="Tip: Use the /authorize command to connect your Ion account!", color=discord.Color.red())
discordEmbedConnectAccount = discord.Embed(title="Developing Mode... Check back later!", color=discord.Color.green())
discordEmbedCommandDisabled = discord.Embed(title=":x: Command Disabled!", color=discord.Color.red())
discordEmbedAreYouSure = discord.Embed(title=":thinking: Are You Sure?", color=discord.Color.yellow())
discordEmbedHaventEightSignups = discord.Embed(title=":x: You Haven't Signed Up For Eighth Yet!", color=discord.Color.red())
discordEmbedThisIsNotYourButton = discord.Embed(title=":x: This Is Not Your Button!", color=discord.Color.red())
discordEmbedReauthorizePlease = discord.Embed(title=":x: Invalid Token, please reauthorize!", color=discord.Color.red())
discordEmbedSuccessfullyChangedSetting = discord.Embed(title=":white_check_mark: Successfully Changed Setting To ", color=discord.Color.green())
discordEmbedUnknownSettingOption = discord.Embed(title=":x: Unknown Setting Option", color=discord.Color.red())
discordEmbedAccountPrivate = discord.Embed(title=":x: User's Account is Private", color=discord.Color.red())


# Command Names and Descriptions
authorizeName = "authorize"
authorizeDescription = "Link your TJHSST ion account to your discord account"

deauthorizeName = "deauthorize"
deauthorizeDescription = "Unlink your TJHSST ion account from your discord account"

whoisName = "whois"
whoisDescription = "Find out who is the person you ping. (by the user's consent!)"

aboutName = "about"
aboutDescription = "About this bot, has some interesting information"

settings_PrivacyName = "privacy"
settings_PrivacyDescription = "Set your privacy settings to public or private"



# Command Groups
settingsGroup = app_commands.Group(name="settings", description="Settings Group")
client.tree.add_command(settingsGroup)
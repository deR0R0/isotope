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
    "allowDMs": True,
    "privacy": "private",
    "signUpForEighth": True,
    "eighthReminders": False,
}

settingOptions = {
    "allowDMs": ["True", "False"],
    "privacy": ["private", "public"],
    "signUpForEighth": ["True", "False"],
    "eighthReminders": ["True", "False"],
}

settingsDescriptions = {
    "allowDMs": "If this bot can DM you.",
    "privacy": "People cannot see your personal information when private.",
    "signUpForEighth": "Ping/DM when you haven't signed up for eighth.",
    "eighthReminders": "DMs you about your eighth period details."
}

# User Currency Stuff
userMoney = {}
defaultUserMoney = {
    "money": 0,
    "bank": 0
}

# Discord Embeds
discordEmbedInternalError = discord.Embed(title=":x: Internal Error!", color=discord.Color.red())
discordEmbedServerError = discord.Embed(title=":x: Server Error!", color=discord.Color.red())
discordEmbedRateLimited = discord.Embed(title=":x: Rate Limited!", description="You've Been Rate Limited! 🙃", color=discord.Color.red())
discordEmbedLoading = discord.Embed(title="<a:loadinggif:1278333115516850253> Loading...", color=discord.Color.blurple())
discordEmbedPerformingSpeedTest = discord.Embed(title="<a:loadinggif:1278333115516850253> Performing Speed Test!", color=discord.Color.blurple())
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
discordEmbedForbidden = discord.Embed(title=":x: I Don't Have Permissions", color=discord.Color.red())
discordEmbedTransferedIQ = discord.Embed(title=":x: Successfully Tranferred __ IQ!", color=discord.Color.green())
discordEmbedInsufficientFunds = discord.Embed(title=":x: Insufficient IQ", color=discord.Color.red())
discordEmbedDepositNotValidInput = discord.Embed(title=":x: Not Valid Input", description="Valid Options: ```<number / all / half>```", color=discord.Color.red())
discordEmbedDepositZeroIQ = discord.Embed(title=":x: Cannot Deposit ```0 IQ```!", color=discord.Color.red())


discordEmbedClaimedIQ = discord.Embed(title=":white_check_mark: Claimed 100 IQ!", color=discord.Color.green())


# Command Names and Descriptions
authorizeName = "authorize"
authorizeDescription = "Link your TJHSST ion account to your discord account"

deauthorizeName = "deauthorize"
deauthorizeDescription = "Unlink your TJHSST ion account from your discord account"

whoisName = "whois"
whoisDescription = "Find out who is the person you ping. (by the user's consent!)"

aboutName = "about"
aboutDescription = "About this bot, has some interesting information"

settings_ViewName = "view"
settings_ViewDescription = "View your user settings"

settings_PrivacyName = "privacy"
settings_PrivacyDescription = "Set your privacy settings to public or private"

settings_AllowDMsName = "allowdms"
settings_AllowDMsDescription = "Allow this bot to send you dms"

commandOptions = {
    "currency_deposit": ["all", "half", "100", "200", "300", "400", "500"],
    "currency_withdraw": ["all", "half", "100", "200", "300", "400", "500"]
}



# Command Groups
settingsGroup = app_commands.Group(name="settings", description="Settings Group")
client.tree.add_command(settingsGroup)

currencyGroup = app_commands.Group(name="currency", description="Currency Group")
client.tree.add_command(currencyGroup)
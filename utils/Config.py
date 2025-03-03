import discord, os
from requests_oauthlib import OAuth2Session
from discord.ext import commands
from colorama import Fore as fore
from . import Logger

# General
PROGRAM_PATH = ""
AUTHORIZE_BUTTON_CHANNEL = "1285636266821419029"
DEVELOPMENT = os.environ.get("DEVELOPMENT")

# Discord Stuff
DISCORD_INTENTS = discord.Intents.all()
client = commands.Bot(command_prefix="/", intents=DISCORD_INTENTS)
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# Static Discord Embeds
DISCORD_EMBED_COMMAND_DISABLED = discord.Embed(title=":x: Command Disabled", description="This command is currently disabled", color=discord.Color.red())
DISCORD_EMBED_ALREADY_AUTHORIZED = discord.Embed(title=":x: Already Authorized", description="You are already authorized!", color=discord.Color.red())
DISCORD_EMBED_NOT_AUTHORIZED = discord.Embed(title=":x: Not Authorized", description="You aren't authorized (yet)! Use /authorize to authorize", color=discord.Color.red())
DISCORD_EMBED_PERM_AUTHORIZE_BUTTON = discord.Embed(title=":atom: Authorize via Ion", description="Please wait while we generate your URL", color=discord.Color.dark_grey())


# Logger
LOGGER_DATE_COLOR = fore.LIGHTBLACK_EX
LOGGER_NORM_COLOR = fore.WHITE
LOGGER_LOCATION_COLOR = fore.CYAN
LOGGER_INFO_COLOR = fore.LIGHTBLUE_EX
LOGGER_WARN_COLOR = fore.LIGHTYELLOW_EX
LOGGER_ERROR_COLOR = fore.LIGHTRED_EX


# Database Stuff
DBMANAGER_DBNAME = "data.db"
DEFAULT_GUILD_SETTINGS = {
    "authorize_channel": None,
    "authorize_role": None,
    "authorize_message": "default_embed",
    "prev_button_id": None,
    "commands_disabled": { # We aren't allowing guild owners to disable certain commands due to security concerns
        "authorize": False,
    }
}


# Command Stuff
COMMAND_STATUSES = {
    "web_page": False,
    "authorize": True,
    "deauthorize": True
}

# Command Names and Descriptions
COMMAND_AUTHORIZE = ["authorize", "Connect your Ion account to your Discord account"]
COMMAND_DEAUTHORIZE = ["deauthorize", "Disconnect your Ion account from your Discord account"]

# Oauth application
ION_CLIENT_ID = os.environ.get("ION_CLIENT_ID")
ION_CLIENT_SECRET = os.environ.get("ION_CLIENT_SECRET")

# Oauth urls
ION_AUTHORIZATION_URL = "https://ion.tjhsst.edu/oauth/authorize"
ION_TOKEN_URL = "https://ion.tjhsst.edu/oauth/token"

# Change redirect uri based on whether or not the application is in development or not
ION_REDIRECT_URI = "https://isotope.der0r0.hackclub.app/authorize"
if DEVELOPMENT == "True":
    ION_REDIRECT_URI = "http://localhost:1211/authorize"

oauthSession = OAuth2Session(client_id=ION_CLIENT_ID, redirect_uri=ION_REDIRECT_URI, scope=["read"])
SQL_INJECTION_WORDS = ["--", ";", "select", "drop", "where", "from", "and", "true", "false", "oauthkey", "id", "="] # this is not how you prevent sql injects but whatever

# Authorize Command Stuff
AUTHORIZE_BUTTON_TIMEOUT = 20


# Functions allowing the modification of config
def set_path(path: str):
    global PROGRAM_PATH
    PROGRAM_PATH = path


# Check whether or not the user setup the virutal environment properly
if ION_CLIENT_ID is None or ION_CLIENT_SECRET is None or DISCORD_TOKEN is None or DEVELOPMENT is None:
    print("Missing environmental variable(s)")
    raise Exception("Missing environmental variable(s)")
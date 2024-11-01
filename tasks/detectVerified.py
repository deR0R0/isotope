# Import libraries
import sys
import os
import discord
from discord import app_commands
from requests_oauthlib import OAuth2Session
from functools import lru_cache

# Variables
oldOauthUsers = {}


# Import Utilities
sys.path.insert(1, sys.path[0].replace("tasks", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit




# Please do not look here, it will hurt your eyes o_o
# Nested if statements... idk how to avoid this
# If you have a solution, feel free to create a pull request!
class DetectVerified:
    # Command
    @staticmethod
    async def detectVerified():
        global oldOauthUsers
        
        #Pongo was here
        try:
            if oldOauthUsers != oauthUsers:
                # When old doesn't equal new, we want to do something idk
                oldOauthUsersList = list(oldOauthUsers.keys())
                for user in oldOauthUsersList:
                    # We can speed up the process by skipping those who didn't change
                    if oldOauthUsers[user] != oauthUsers[user]:
                        # Check if it's a string (aka, state is stored)
                        if not isinstance(oauthUsers[user], str):
                            # Fetch user
                            discordUser: discord.User = await client.fetch_user(user)
                            for guild in discordUser.mutual_guilds:
                                # Check if guild HAS config in the first place
                                if str(guild.id) in config["serverConfigs"]:
                                    # Check if authorization is enabled on the guild
                                    if "authorizationEnabled" in config["serverConfigs"][str(guild.id)]:
                                        if config["serverConfigs"][str(guild.id)]["authorizationEnabled"] == True:
                                            # Get the role (check if exists)
                                            try:
                                                role = discord.utils.get(guild.roles, name="Verified Student")
                                            except Exception as err:
                                                Logger.warn(err)
                                                return
                                            
                                            # Add the role
                                            try:
                                                await guild.get_member(discordUser.id).add_roles(role, reason="Verified Through Oauth")
                                            except Exception as err:
                                                # This is when the bot most likely doesn't have permission to add the role
                                                Logger.warn(err)
                                                return
                    
                            # Once added role, we want to tell them they're verified
                            await discordUser.send(embed=discord.Embed(title=":white_check_mark: Authenticated!", color=discord.Color.green()))
                            Logger.log(f"Successfully verified {discordUser.name}")



                oldOauthUsers = oauthUsers.copy()
        except Exception as err:
            Logger.warn(err)
            oldOauthUsers = oauthUsers.copy()

import sys
import os
import discord
from discord import app_commands
from requests_oauthlib import OAuth2Session
from functools import lru_cache

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.OauthManager import OManager
from utils.CurrencyManager import CManager
from utils.SettingsManager import SManager

# ConfirmDeletion
class ConfirmDeletion(discord.ui.View):
    def __init__(self, msg: discord.Message, userId: int):
        self.userId: int = userId
        self.msg: discord.Message = msg
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def authenticate(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if this is their button
        if self.userId != interaction.user.id:
            await interaction.response.send_message(embed=discordEmbedThisIsNotYourButton, ephemeral=True)
            return
        
        # Call the actual deletion
        Logger.cmd(f"{interaction.user} pressed Confirm Deletion button!")
        await deauthorize.deleteAccount(interaction, self.msg, False)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def deauthenticate(self, interaction: discord.Interaction, button: discord.ui.Button):
        # CHeck if this is their button
        if self.userId != interaction.user.id:
            await interaction.response.send_message(embed=discordEmbedThisIsNotYourButton, ephemeral=True)
            return
        
        # Remove this message
        await interaction.response.send_message(embed=discord.Embed(title=":x: Canceled!", color=discord.Color.red()), ephemeral=True)
        await self.msg.delete()

    @discord.ui.button(label="Only My Ion", style=discord.ButtonStyle.gray)
    async def onlymyion(self, interaction: discord.Interaction, button: discord.ui.button):
        # Check if this is their button
        if self.userId != interaction.user.id:
            await interaction.response.send_message(embed=discordEmbedThisIsNotYourButton, ephemeral=True)
            return
        
        # Call Only Ion deletion
        Logger.cmd(f"{interaction.user} pressed Only My Ion button!")
        await deauthorize.deleteAccount(interaction, self.msg, True)

# Create the command class
class deauthorize:

    # Actual command
    @staticmethod
    async def deauthorize(interaction: discord.Interaction, originalResponse=None):

        # Log Command that was Ran
        Logger.log(f"{interaction.user} used /deauthorize")

        # Loading...
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=True)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["deauthorize"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        # Check if they have connected or not
        if str(interaction.user.id) not in oauthUsers:
            await originalResponse.edit(embed=discordEmbedAccountNotConnected)
            return
        
        # Wrap in try catch statmeent
        try:
            # Send buttons
            await originalResponse.edit(embed=discordEmbedAreYouSure, view=ConfirmDeletion(originalResponse, interaction.user.id))

        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
            
       
    # Deletion Background Task
    @staticmethod
    async def deleteAccount(interaction: discord.Interaction, message: discord.Message, ionOnly: bool, originalResponse = None):
        
        # Log Command that was Ran
        Logger.log(f"{interaction.user} is deauthorizing their account!")

        # Delete the other message
        await message.delete()

        # Loading...
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=True)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["deauthorize"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        # Wrap in try catch statmeent
        try:
            if ionOnly:
                OManager.deleteUser(interaction.user.id)
            else:
                OManager.deleteUser(interaction.user.id)
                CManager.removeUser(interaction.user.id)
                SManager.removeUser(interaction.user.id)

            # Its all gone now


            # Save the tokens
            FManager.write("tokens.json", oauthUsersTokens)

        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
            return

        await originalResponse.edit(embed=discord.Embed(title=":white_check_mark: Successfully Removed!", description="You can always reauthorize with /authorize 🥺", color=discord.Color.green()))



if __name__ == "__main__":
    Logger.log("This file is not meant to be run. Please run via the main process (main.py)")
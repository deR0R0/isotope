
import sys
import os
import discord
import json
from discord import app_commands
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit

progPath = ""

# Create the command class
class whois:

    # Set path
    @staticmethod
    def setPath(path: str):
        global progPath
        progPath = path

    # Actual command
    @lru_cache
    @staticmethod
    async def whois(interaction: discord.Interaction, originalResponse=None):
        global progPath
        # Log Command that was Ran
        Logger.log(f"{interaction.user} used /whois")

        # Loading...
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=False)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["whois"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        # Check if they have connected or not
        if str(interaction.user.id) not in oauthUsers or isinstance(oauthUsers[str(interaction.user.id)], str):
            await originalResponse.edit(embed=discordEmbedAccountNotConnected)
            return
        
        # Wrap in try catch statmeent
        try:
            # Request
            profile = oauthUsers[str(interaction.user.id)].get("https://ion.tjhsst.edu/api/profile")
            profile = json.loads(profile.content.decode())

            # Get the year they graduate
            name = profile["full_name"]
            grad_year = profile["graduation_year"]

            # Import the image, draw it, then save it
            img = Image.open(f"{progPath}/assets/whoIsWide.png")
            imgDraw = ImageDraw.Draw(img)
            # Year of text
            imgDraw.text((154, 76), str(grad_year), font=ImageFont.truetype(f"{progPath}/assets/Roboto-Medium.ttf", 15), fill=(0, 0, 0))
            # Name Text
            imgDraw.text((20, 25), str(name), font=ImageFont.truetype(f"{progPath}/assets/Roboto-Medium.ttf", 35), fill=(0, 0, 0))
            # Save it
            img.save(f"{progPath}/assets/{str(interaction.user.id)}.png")

            # Now, we want to import the image as a discord.file
            await originalResponse.edit(embed=None, content=f"Who Is <@{interaction.user.id}> ?")
            await interaction.channel.send(file=discord.File(f"{progPath}/assets/{interaction.user.id}.png"))

            # Delete the file
            os.remove(f"{progPath}/assets/{interaction.user.id}.png")

        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)



if __name__ == "__main__":
    Logger.log("This file is not meant to be run. Please run via the main process (main.py)")
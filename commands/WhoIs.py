from discord import app_commands
from discord.ext import commands
import discord
import sys

sys.path.insert(1, sys.path[0].replace("command", ""))
from utils import Config, OAuthHelper, Logger, Exceptions
from utils.Config import client

@client.tree.command(name="whois", description="Get info about a user LIMITED TO ADMINS")
@commands.has_guild_permissions(administrator=True)
async def whois(interaction: discord.Interaction, user: discord.User):
    Logger.info("WhoIsCommand", f"IMPORTANT: WhoIs command called by {interaction.user.name} for {user.name}")

    # admin only command. don't check for disabled

    # get user info
    try:
        user_info = OAuthHelper.return_user_data(user.id)
    except Exceptions.NoTokenError:
        await interaction.response.send_message(f"{user.name} has not authorized yet")
        return
    except Exception as e:
        Logger.error("WhoIsCommand", f"Error fetching user data: {e}")
        await interaction.response.send_message(f"An error occurred while fetching user data for {user.name}")
        return
    
    # create embed
    embed = discord.Embed(title=f"WhoIs: {user.name}", color=discord.Color.blue())
    embed.add_field(name="Ion Username", value=user_info.get("ion_username", "N/A"), inline=False)
    embed.add_field(name="Full Name", value=user_info.get("full_name", "N/A"), inline=False)
    embed.add_field(name="Grade", value=user_info.get("grade").get("name", "N/A"), inline=False)

    # send embed
    await interaction.response.send_message(embed=embed)
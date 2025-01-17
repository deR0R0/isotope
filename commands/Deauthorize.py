import sys, discord

sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils import Logger, Config, DBManager, CUtils, OAuthHelper
from utils.Config import client, oauthSession

@client.tree.command(name=Config.COMMAND_DEAUTHORIZE[0], description=Config.COMMAND_DEAUTHORIZE[1])
async def deauthorize(interaction: discord.Interaction):
    Logger.info("commands.Deauthorize.deauthorize", f"Authorize Command Called by {interaction.user.name}")
    await interaction.response.defer(ephemeral=True)

    # Check if command is disabled
    if CUtils.check_disabled("deauthorize"):
        await interaction.followup.send(embed=Config.DISCORD_EMBED_COMMAND_DISABLED)
        return
    
    # Check Session
    if not OAuthHelper.check_session(interaction.user.id):
        await interaction.followup.send(embed=Config.DISCORD_EMBED_NOT_AUTHORIZED)
        return
    
    # Delete session
    DBManager.del_user(interaction.user.id)

    await interaction.followup.send(embed=discord.Embed(title=f":white_check_mark: Successfully Deleted!", description=f"Anything associated with you has been removed. You may revoke the oauth session (to be secure) at <https://ion.tjhsst.edu/oauth/application>.", color=discord.Color.green()), ephemeral=True)
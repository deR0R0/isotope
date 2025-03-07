import sys, discord

sys.path.insert(1, sys.path[0].replace("commands/guild", ""))
sys.path.insert(1, sys.path[0].replace("guild", ""))
from utils import Logger, Config, DBManager, CUtils, OAuthHelper, UserTools
from commands.Guild import guild_group

@guild_group.command(name="setup", description="Set up your guild for this bot. You do not need to run this command!")
async def setup(interaction: discord.Interaction):
    await interaction.response.defer()

    if CUtils.check_disabled("setup"):
        await interaction.followup.send(embed=Config.DISCORD_EMBED_COMMAND_DISABLED)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You must be an administrator to run this command!")
        return
    
    DBManager.setup_server(interaction.guild.id)
    await interaction.followup.send("Server setup successfully")

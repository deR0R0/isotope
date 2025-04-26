import sys, discord

sys.path.insert(1, sys.path[0].replace("commands/guild", ""))
sys.path.insert(1, sys.path[0].replace("guild", ""))
from utils import Logger, Config, DBManager, CUtils, OAuthHelper, UserTools
from commands.Guild import guild_group

@guild_group.command(name="settings", description="View or change your guild settings")
async def settings(interaction: discord.Interaction):
    Logger.info("commands.guild.Settings.settings", f"Settings command called by {interaction.user.name}")
    await interaction.response.defer()

    if CUtils.check_disabled("guild_settings"):
        await interaction.followup.send(embed=Config.DISCORD_EMBED_COMMAND_DISABLED)
        return
    
    settings = DBManager.get_server_settings(interaction.guild.id)
    
    settings_embed = discord.Embed(title=f"{interaction.guild.name} Settings", color=discord.Color.blurple())

    # Authorize Button Stuff
    if(settings["authorize_button"]["enabled"]):
        settings_embed.description = f"\n\n**Authorize Button**: Enabled :white_check_mark:"
        settings_embed.description += f"\n> **Authorize Channel**: {settings['authorize_button']['channel']}"
        settings_embed.description += f"\n> **Authorize Role**: {settings['authorize_button']['role']}"
        settings_embed.description += f"\n> **Authorize Message**: {settings['authorize_button']['message']}"
        settings_embed.description += f"\n> **Errors**: {settings['authorize_button']['errors']}"
    else:
        settings_embed.description = f"\n\n**Authorize Button**: Disabled :x:"

    

    await interaction.followup.send(embed=settings_embed)
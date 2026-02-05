import discord
from utils import Config, Logger, DBManager

class GuildHelper:

    @staticmethod
    async def send_verify_button(guild_id: int) -> bool:
        # get guild settings first
        settings = DBManager.get_server_settings(guild_id)

        # get guild object
        guild = Config.client.get_guild(guild_id)

        if guild is None:
            Logger.warn("GuildHelper.send_verify_button", f"Guild: {guild_id} is invalid")
            return False

        # check if the button is enabled
        if not settings["authorize_button"]["enabled"]:
            return False
        
        # get all the necessary settings and vars
        authorize_channel = settings["authorize_button"]["channel"]
        prev_button_id = settings["authorize_button"]["prev_button_id"]
        authorize_message = settings["authorize_button"]["message"]

        # get channel object
        channel = Config.client.get_channel(authorize_channel)

        if channel is None:
            Logger.warn("main.on_ready", f"Guild: {guild.id} has invalid channel")
            settings["authorize_button"]["enabled"] = False
            settings["authorize_button"]["errors"] = "Invalid Channel"
            DBManager.set_server_settings(guild.id, settings)
            return False
        
        # attempt to fetch message
        try:
            prev_button = await channel.fetch_message(prev_button_id)
        except discord.errors.NotFound:
            Logger.warn("GuildHelper.send_verify_button", f"Previous button message not found in {guild.id}")
            settings["authorize_button"]["prev_button_id"] = None
            prev_button = None
        except discord.errors.Forbidden:
            Logger.warn("GuildHelper.send_verify_button", f"Bot doesn't have perms to fetch message in {guild.id}. Please notify guild owner")
            return False
        
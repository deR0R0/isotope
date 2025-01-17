from discord import Embed
from . import Config, Logger

class CUtils:
    @staticmethod
    def check_disabled(command: str) -> bool:
        # Check if the command is disabled, if yes, return True
        if Config.COMMAND_STATUSES[command] is not True:
            Config.DISCORD_EMBED_COMMAND_DISABLED.description = Config.COMMAND_STATUSES[command] # Super long 
            return True
        
        return False
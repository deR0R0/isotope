import discord
from . import Logger

class UserTools:
    @staticmethod
    async def add_role(user: discord.Member, role: discord.Role):
        # add role
        try:
            if role not in user.roles:
                await user.add_roles(role)
        except Exception as err:
            Logger.error("UserTools.add_role", err)
            return False
        
        return True
    
    @staticmethod
    async def dm_user(user: discord.Member, message: str):
        # dm user
        try:
            await user.send(message)
        except Exception as err:
            Logger.error("UserTools.dm_user", err)
            return False
        
        return True
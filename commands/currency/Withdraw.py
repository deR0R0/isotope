import discord
import sys

sys.path.insert(1, sys.path[0].replace("commands/currency", ""))
from utils.Configuration import *
from utils.RateLimiter import RateLimit
from utils.CurrencyManager import CManager

class withdraw:
    @staticmethod
    async def withdraw(interaction: discord.Interaction, amount: int, originalResponse=None):
        Logger.cmd(f"{interaction.user} used /currency withdraw")

        # Send loading
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=False)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["currency_withdraw"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        try:
            r = CManager.transferFromBank(interaction.user.id, amount)
            if r == "success":
                discordEmbedTransferedIQ.title = f":white_check_mark: Withdrew ```{amount}IQ``` from the Bank!"
                await originalResponse.edit(embed=discordEmbedTransferedIQ)
            elif r == "insufficientFunds":
                await originalResponse.edit(embed=discordEmbedInsufficientFunds)
            else:
                await originalResponse.edit(embed=discordEmbedInternalError)
                Logger.warn("There seems to be an error in CurrencyManager. Please check it")
        except Exception as err:
            await originalResponse.edit(embed=discordEmbedInternalError)
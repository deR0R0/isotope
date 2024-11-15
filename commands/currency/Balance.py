# Imports
import sys
import os
import discord
import json
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
from oauthlib.oauth2 import TokenExpiredError, InvalidGrantError
from requests_oauthlib import OAuth2Session, oauth2_auth

# Import Utilities
sys.path.insert(1, sys.path[0].replace("commands/currency", ""))
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger
from utils.RateLimiter import RateLimit
from utils.SettingsManager import SManager
from utils.CurrencyManager import CManager
from commands.currency.Deposit import deposit
from commands.currency.Withdraw import withdraw

class DepositWithdrawButtons(discord.ui.View):
    def __init__(self, msgId: int, userid: int):
        self.msgid = msgId
        self.userid = userid
        super().__init__(timeout=15)

    @discord.ui.button(label="📥 Deposit", style=discord.ButtonStyle.blurple)
    async def depositButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        Logger.cmd(f"{interaction.user} pressed Deposit button!")

        if self.userid is not interaction.user.id:
            await interaction.response.send_message(embed=discordEmbedThisIsNotYourButton)
            return
        
        # Disable button
        button.disabled = True
        discord.utils.get(self.children, label="📤 Withdraw").disabled = True
        # Update the message
        embed = interaction.message.embeds[0]
        await interaction.response.send_modal(DepositModal())
        await interaction.followup.edit_message(message_id=self.msgid, embed=embed, view=self)

    @discord.ui.button(label="📤 Withdraw", style=discord.ButtonStyle.blurple)
    async def withdrawButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        Logger.cmd(f"{interaction.user} pressed Withdraw button!")

        if self.userid is not interaction.user.id:
            await interaction.response.send_message(embed=discordEmbedThisIsNotYourButton)
            return
        
        # Disable buttons
        button.disabled = True
        discord.utils.get(self.children, label="📥 Deposit").disabled = True
        # Update the message
        embed = interaction.message.embeds[0]
        await interaction.response.send_modal(WithdrawModal())
        await interaction.followup.edit_message(message_id=self.msgid, embed=embed, view=self)


class DepositModal(discord.ui.Modal, title="Deposit"):
    amount = discord.ui.TextInput(label="Deposit Amount", placeholder="Enter Deposit Amount...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        Logger.cmd(f"{interaction.user} submitted Deposit modal!")
        amount = str(self.amount.value)
        # Check if valid
        if amount.isnumeric():
            if int(amount) != 0:
                await deposit.deposit(interaction, int(amount))
            else:
                await interaction.response.send_message(embed=discordEmbedDepositZeroIQ)
        else:
            if amount == "all":
                await deposit.deposit(interaction, int(CManager.getMoney(interaction.user.id)[0]))
            elif amount == "half":
                await deposit.deposit(interaction, round(int(CManager.getMoney(interaction.user.id)[0]) / 2))
            else:
                await interaction.response.send_message(embed=discordEmbedDepositNotValidInput)

class WithdrawModal(discord.ui.Modal, title="Withdraw"):
    amount = discord.ui.TextInput(label="Withdraw Amount", placeholder="Enter Deposit Amount...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        Logger.cmd(f"{interaction.user} submitted Withdraw modal!")
        amount = str(self.amount.value)
        # Check if valid
        if amount.isnumeric():
            if int(amount) != 0:
                await withdraw.withdraw(interaction, int(amount))
            else:
                await interaction.response.send_message(embed=discordEmbedDepositZeroIQ)
        else:
            if amount == "all":
                await withdraw.withdraw(interaction, int(CManager.getMoney(interaction.user.id)[1]))
            elif amount == "half":
                await withdraw.withdraw(interaction, round(int(CManager.getMoney(interaction.user.id)[1]) / 2))
            else:
                await interaction.response.send_message(embed=discordEmbedDepositNotValidInput)


class balance:
    @staticmethod
    async def balance(interaction: discord.Interaction, originalResponse = None):
        Logger.cmd(f"{interaction.user} used /currency balance")
        
        # Send loading
        if originalResponse == None:
            await interaction.response.send_message(embed=discordEmbedLoading, ephemeral=False)
            originalResponse = await interaction.original_response()
        
        # Check if command is enabled or not
        if not config["enabledCommands"]["currency_balance"]:
            await originalResponse.edit(embed=discordEmbedCommandDisabled)
            return

        # Rate Limiter
        if RateLimit.addUser(interaction.user.id):
            Logger.log(f"{interaction.user} has been rate limited!")
            await originalResponse.edit(embed=discordEmbedRateLimited)
            return
        
        try:
            balance = CManager.getMoney(interaction.user.id)
            balanceEmbed = discord.Embed(title=f"{interaction.user.display_name}'s Balance", color=interaction.user.color)
            balanceEmbed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url, url="https://discord.com/vanityurl/dotcom/steakpants/flour/flower/index11.html")
            balanceEmbed.description = f"\n> :brain: {balance[0]} IQ\n> :bank: {balance[1]} IQ"
            
            await originalResponse.edit(embed=balanceEmbed, view=DepositWithdrawButtons(originalResponse.id, interaction.user.id))
        except Exception as err:
            Logger.err(err)
            await originalResponse.edit(embed=discordEmbedInternalError)
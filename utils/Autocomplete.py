import typing
import discord
from discord import app_commands
from functools import lru_cache
from utils.Configuration import *
from utils.LogManager import Logger
from utils.RegisterCmds import *




@lru_cache
@mainSettingsPrivacy.autocomplete("value")
async def mainSettingsPrivacyAutocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    Logger.log("test")
    choices = []
    for choice in settingOptions["privacy"]:
        if current.lower() in choice.lower():
            choices.append(app_commands.Choice(name=choice, value=choice))

    return choices

@lru_cache
@mainSettingsAllowDms.autocomplete("value")
async def mainSettingsAllowDMsAutocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = []
    for choice in settingOptions["allowDMs"]:
        if current.lower() in choice.lower():
            choices.append(app_commands.Choice(name=choice, value=choice))

    return choices

@lru_cache
@mainCurrencyDeposit.autocomplete("amount")
async def mainSettingsAllowDMsAutocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = []
    for choice in commandOptions["currency_deposit"]:
        if current.lower() in choice.lower():
            choices.append(app_commands.Choice(name=choice, value=choice))

    return choices

@lru_cache
@mainCurrencyWithdraw.autocomplete("amount")
async def mainSettingsAllowDMsAutocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    choices = []
    for choice in commandOptions["currency_withdraw"]:
        if current.lower() in choice.lower():
            choices.append(app_commands.Choice(name=choice, value=choice))

    return choices
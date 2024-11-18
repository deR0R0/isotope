from utils.Configuration import *
from utils.CurrencyManager import CManager

# Import commands
sys.path.insert(1, sys.path[0].replace("utils", ""))
from commands.Authorize import authorize
from commands.Deauthorize import deauthorize
from commands.WhoIs import whois
from commands.About import about
from commands.settings.View import view
from commands.settings.Privacy import privacy
from commands.settings.AllowDMs import allowdms
from commands.currency.Daily import daily
from commands.currency.Balance import balance
from commands.currency.Deposit import deposit
from commands.currency.Withdraw import withdraw

# Commands
@client.tree.command(name=authorizeName, description=authorizeDescription)
async def mainAuthorize(interaction: discord.Interaction):
    await authorize.authorize(interaction)

@client.tree.command(name=deauthorizeName, description=deauthorizeDescription)
async def mainDeauthorize(interaction: discord.Interaction):
    await deauthorize.deauthorize(interaction)

@client.tree.command(name=whoisName, description=whoisDescription)
async def mainWhoIs(interaction: discord.Interaction, user: discord.Member = None):
    await whois.whois(interaction, user)

@client.tree.command(name=aboutName, description=aboutDescription)
async def mainAbout(interaction: discord.Interaction):
    await about.about(interaction)

# Settings Commands
@settingsGroup.command(name=settings_ViewName, description=settings_ViewDescription)
async def mainSettingsView(interaction: discord.Interaction):
    await view.view(interaction)

@settingsGroup.command(name=settings_PrivacyName, description=settings_PrivacyDescription)
@app_commands.describe(value="Set your privacy to public or private")
async def mainSettingsPrivacy(interaction: discord.Interaction, value: str):
    await privacy.privacy(interaction, value)

@settingsGroup.command(name=settings_AllowDMsName, description=settings_AllowDMsDescription)
@app_commands.describe(value="Allow or not the bot to send you dms. True/False")
async def mainSettingsAllowDms(interaction: discord.Interaction, value: str):
    await allowdms.allowdms(interaction, value)


# Currency Commands
@currencyGroup.command(name="daily", description="Every 24 hours you can claim 100 IQ")
async def mainCurrencyDaily(interaction: discord.Interaction):
    await daily.daily(interaction)

@currencyGroup.command(name="balance", description="See your balance")
async def mainCurrencyBalance(interaction: discord.Interaction):
    await balance.balance(interaction)

@currencyGroup.command(name="deposit", description="Transfer the IQ in your brain to a bank")
async def mainCurrencyDeposit(interaction: discord.Interaction, amount: str):
    if amount.isnumeric():
        await deposit.deposit(interaction, int(amount))
    else:
        if amount == "all":
            x = CManager.getMoney(interaction.user.id)[0]
            await deposit.deposit(interaction, x)
        elif amount == "half":
            x = round(CManager.getMoney(interaction.user.id)[0] / 2)
            await deposit.deposit(interaction, x)
        else:
            await interaction.response.send_message(embed=discordEmbedDepositNotValidInput)

@currencyGroup.command(name="withdraw", description="Withdraw IQ from the bank to your brain")
async def mainCurrencyWithdraw(interaction: discord.Interaction, amount: str):
    if amount.isnumeric():
        await withdraw.withdraw(interaction, int(amount))
    else:
        if amount == "all":
            x = CManager.getMoney(interaction.user.id)[1]
            await withdraw.withdraw(interaction, x)
        elif amount == "half":
            x = round(CManager.getMoney(interaction.user.id)[1] / 2)
            await withdraw.withdraw(interaction, x)
        else:
            await interaction.response.send_message(embed=discordEmbedDepositNotValidInput)
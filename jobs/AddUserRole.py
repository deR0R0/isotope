import discord
import sys
import json
from discord.ext import tasks

sys.path.insert(1, sys.path[0].replace("jobs", ""))
from utils import Config, Logger, DBManager

allOldUsers = None

@tasks.loop(seconds=3)
async def add_user_role():
    global allOldUsers

    if allOldUsers == None: 
        allOldUsers = DBManager.get_all_users()
        return

    # basically just checks the difference between
    # old and new db

    allUsers = DBManager.get_all_users()

    # change into a dictionary for easier comparison
    allUsersDict = {user: oauth for user, oauth in allUsers}
    allOldUsersDict = {user: oauth for user, oauth in allOldUsers}

    # loop thru the users
    for user, oauth in allUsersDict.items():
        # check if they're already in the old users
        # if they are, and if its the same oauth, skip
        if user in allOldUsersDict:
            if oauth == allOldUsersDict[user]:
                continue

        # check for json format
        try:
            json.loads(oauth)
        except json.JSONDecodeError:
            continue # probably a string (state), so skip

        currentUser = Config.client.get_user(user)

        if currentUser is None:
            continue

        verified = False
        serversVerifiedIn = []

        for guild in currentUser.mutual_guilds:
            serverSettings = DBManager.get_server_settings(guild.id)
            authorizeButtonEnabled = serverSettings["authorize_button"]["enabled"] # we will use this later
            roleId = serverSettings["authorize_button"]["role"]

            try:
                role = guild.get_role(roleId)
            except Exception as e:
                Logger.error("jobs.AddUserRole.add_user_role", f"Failed to get role for guild \"{guild.id}\": {e}")
                continue

            if role == None:
                break

            # add role
            try:
                await guild.get_member(user).add_roles(role)
                Logger.info("jobs.AddUserRole.add_user_role", f"Added role \"{role.name}\" to user \"{currentUser.name}\" in guild \"{guild.name}\"")
                serversVerifiedIn.append(guild.name)
                verified = True
            except Exception as e:
                Logger.error("jobs.AddUserRole.add_user_role", f"Failed to add role \"{role.name}\" to user \"{currentUser.name}\" in guild \"{guild.name}\": {e}")
                continue

        if verified:
            # do other stuff
            introductionEmbed = discord.Embed(title=":wave: Hello There!", description="")
            introductionEmbed.description += "It seems like it's your first time verifying!\n"
            introductionEmbed.description += "You have been verified in the following servers:\n"
            for guild in serversVerifiedIn:
                introductionEmbed.description += ">" + guild + "\n"
            introductionEmbed.description += "\nThis is probably one of the last times I will DM you, BUT I want to advertise some cool things I can do!\n"
            introductionEmbed.description += "• I can remind you to sign up for eighth periods\n"
            introductionEmbed.description += "• Plenty of features coming soon!\n"
            introductionEmbed.description += "\nIf you have any questions, feel free to DM me @deroro_ on Discord!\n"
            introductionEmbed.description += "PS: I work with multiple servers! Just invite me and configure the verification!!"

            try:
                await currentUser.send(embed=introductionEmbed)
            except discord.Forbidden:
                Logger.warn("jobs.AddUserRole.add_user_role", f"Failed to send introduction DM to user \"{currentUser.name}\". Most likely has DMs off.")
            except Exception as e:
                Logger.error("jobs.AddUserRole.add_user_role", f"Failed to send introduction DM to user \"{currentUser.name}\": {e}")


    allOldUsers = allUsersDict.items()
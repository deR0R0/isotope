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

    # basically just checks the difference between
    # old and new db

    allUsers = DBManager.get_all_users()

    for uIndex in range(len(allUsers)):
        # if user is not in old users, just run it thru idc
        user, oauth = allUsers[uIndex]

        if uIndex < len(allOldUsers):
            oldUser, oldOauth = allOldUsers[uIndex]
            if oauth == oldOauth:
                continue


        # this is when we know that the user
        # has verified OR change states.
        # So, check if it's a state.
        try:
            json.loads(oauth) # it loads???
            pass # go
        except json.JSONDecodeError:
            continue # its probs a string or an error, idgaf

        # has verified.
        currentUser = Config.client.get_user(user)

        for guild in currentUser.mutual_guilds:
            serverSettings = DBManager.get_server_settings(guild.id)
            roleId = serverSettings["authorize_button"]["role"]

            if roleId is None:
                continue

            # get role
            try:
                role = guild.get_role(roleId)
            except Exception as e:
                Logger.error("OAuthHelper.link_via_state", f"Failed to get role for guild \"{guild.id}\": {e}")
                continue

            if role is not None:
                await guild.get_member(user).add_roles(role)
                Logger.info("jobs.AddUserRole.add_user_role", f"Added role \"{role.name}\" to user \"{currentUser.name}\" in guild \"{guild.name}\"")

    allOldUsers = allUsers
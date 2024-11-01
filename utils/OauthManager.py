import os
import sys
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import InvalidGrantError

from utils.LogManager import Logger
from utils.FileManager import FManager
from utils.Configuration import *


class OManager:
    
    @staticmethod
    def linkOauth(authCode: str, state: str) -> bool:
        try:
            for user in oauthUsers.keys():
                if oauthUsers[user] == state:
                    # Breaking this down,
                    # We will first fetch the token from the oauthUsers 
                    oauthUsers[user] = OAuth2Session(client_id=CLIENTID, redirect_uri=oauthLink, scope="read")
                    oauthUsersTokens[user] = oauthUsers[user].fetch_token("https://ion.tjhsst.edu/oauth/token", code=authCode, client_secret=OAUTHKEY)
                    Logger.serv("Added User to Oauth Users")
                    FManager.write("tokens.json", oauthUsersTokens)
        except InvalidGrantError:
            Logger.warn("User attempted to create false session")
            return False

        except Exception as err:
            Logger.warn(err)
            return False
        
        return True
    
    @staticmethod
    def refreshUserToken(userId: int) -> str:
        try:
            args = {"client_id": CLIENTID, "client_secret": OAUTHKEY}
            oauthUsersTokens[str(userId)] = oauthUsers[str(userId)].refresh_token("https://ion.tjhsst.edu/oauth/token", **args)
        except InvalidGrantError:
            # Happens when user usually has an invalid token that will throw an error (not expired error)
            # To handle this, we will just delete their session and token
            OManager.deleteUser(userId)

            return "invalidToken"
        except Exception as err:
            Logger.warn(err)
            return "unknownException"
        
        FManager.write("tokens.json", oauthUsersTokens)
        return "success"
    
    @staticmethod
    def deleteUser(userId: int) -> bool:
        try:
            del oauthUsers[str(userId)]
            del oauthUsersTokens[str(userId)]
        except Exception as err:
            Logger.warn(err)
            return False
        FManager.write("tokens.json", oauthUsersTokens)
        return True


    
    @staticmethod
    def checkOauthSession(userId: int) -> bool:
        if str(userId) not in oauthUsers:
            return False
        
        if isinstance(oauthUsers[str(userId)], str):
            return False
        
        return True
import json
from . import Config, DBManager, Logger
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError, MissingTokenError

class OAuthHelper:
    @staticmethod
    def check_session(user_id: int):
        Logger.info("OAuthHelper.checkSession", f"Checking session for user \"{user_id}\"")

        # Grab token
        token = DBManager.get_token_from_user_id(user_id)

        # Check if token is none
        if token is None:
            return False
        
        # Check if token is correct
        if type(token) is not dict:
            return False
        
        oauthSession = OAuth2Session(Config.ION_CLIENT_ID, token=token)

        # Send request, if request invalid, then session is invalid
        try:
            oauthSession.get("https://ion.tjhsst.edu/api/profile")
        except ValueError:
            # Warn and set token to null
            Logger.warn("OAuthHelper.checkSession", f"Session for user \"{user_id}\" is invalid")
            DBManager.edit_token_user_id(user_id, 'null')

            return False
        except TokenExpiredError: # when token is expired, we want to still return true but also refresh the token
            Logger.warn("OAuthHelper.checkSession", f"Session for user \"{user_id}\" is expired, not invalid")
            
            # Refresh token
            args = {"client_id": Config.ION_CLIENT_ID, "client_secret": Config.ION_CLIENT_SECRET}
            token = oauthSession.refresh_token(Config.ION_TOKEN_URL, **args)
            DBManager.edit_token_user_id(user_id, dict(token))

        except Exception as e:
            Logger.error("OAuthHelper.checkSession", f"Error checking session: {e}")
            return False
        
        return True
    
    @staticmethod
    def link_token_via_state(state: str, token: dict) -> any:
        Logger.info("OAuthHelper.link_via_state", f"Linking via state \"{state}\"")

        # Check if state has any common sql injection words, ignoring case
        for word in Config.SQL_INJECTION_WORDS:
            if word.lower() in state.lower():
                Logger.warn("OAuthHelper.link_via_state", f"State \"{state}\" contains sql injection word \"{word}\"")
                return "sql_injection"

        # Get person based on oauth
        userId = DBManager.get_user_id_from_token(state)

        # Check if user doesn't exist, 99% will succeed
        if userId is None:
            Logger.warn("OAuthHelper.link_via_state", f"User id for state \"{state}\" is None")
            return False
        
        # set userid's token from state to token
        DBManager.edit_token_user_id(userId, token)

        return True
import json
from time import time_ns
from . import Config, DBManager, Logger
from .Exceptions import NoTokenError, InvalidTokenFormatError, InvalidTokenError, FakeStateError
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError, MissingTokenError

class OAuthHelper:
    @staticmethod
    def refresh_token(user_id: int, session: OAuth2Session):
        try:
            args = {"client_id": Config.ION_CLIENT_ID, "client_secret": Config.ION_CLIENT_SECRET}
            token = session.refresh_token(Config.ION_TOKEN_URL, **args)
            DBManager.edit_token_user_id(user_id, dict(token))
        except Exception as e:
            Logger.error("OAuthHelper.refresh_token", f"Error refreshing token: {e}")

    @staticmethod
    def check_token_format(token: dict):
        # Check if token is none
        if token is None:
            raise NoTokenError(f"Missing token")
        
        # Check if token is correct
        if type(token) is not dict:
            raise InvalidTokenFormatError(f"Incorrect data type for token. Expect: dict, got: {type(token)}")
        
    @staticmethod
    def verify_token(user_id: int, session: OAuth2Session):
        try:
            # Benchmark the request, see how long it takes
            # My server is in germany, so it'll take pretty long
            timeBefore = time_ns()
            session.get("https://ion.tjhsst.edu/api/profile")
            timeAfter = time_ns()
            Logger.info("OAuthHelper.verify_token", "Token Verification Benchmark: " + str((timeAfter - timeBefore) // 1_000_000) + "ms")

        except ValueError: # Access token is invalid in some way
            # Remove the "broken" token from the database and make the user reverify
            DBManager.edit_token_user_id(user_id, 'null')
            raise InvalidTokenError(f"Session for user \"{user_id}\" is invalid")
        
        except TokenExpiredError: # Access token is expired
            # Refresh the token
            OAuthHelper.refresh_token(user_id, session)

        except Exception as e: # Unknown error? :O
            raise e


    @staticmethod
    def check_session(user_id: int) -> bool:
        """
        TL;DR:
        Gets the token from the userid.
        Checks whether or not the token is valid. (No token / State "token")
        Creates an oauth2 session based on the token.
        Sends a request to the ion api.
            ValueError: When token is invalid
                Reset the token to null in the database.
                Raise InvalidTokenError
            If the request is valid, then the session is valid.
            If the request is expired, then the session is expired.
                Refreshes the token and sets it to the database.
        """
        Logger.info("OAuthHelper.checkSession", f"Checking session for user \"{user_id}\"")

        # Grab token
        token = DBManager.get_token_from_user_id(user_id)

        # Confirm token format
        try:
            OAuthHelper.check_token_format(token)
        except Exception as err:
            Logger.warn("OAuthHelper.checkSession", f"Token format check failed: {err}")
            DBManager.edit_token_user_id(user_id, 'null')
            return False
        
        # Create an oauth2 session based on the token
        oauthSession = OAuth2Session(Config.ION_CLIENT_ID, token=token)

        # Check if the token is valid
        try:
            OAuthHelper.verify_token(user_id, oauthSession)
        except InvalidTokenError as err:
            Logger.warn("OAuthHelper.checkSession", f"Token is invalid: {err}")
            return False

        except InvalidTokenFormatError as err:
            Logger.warn("OAuthHelper.checkSession", f"Token format is invalid: {err}")
            return False

        except Exception as err:
            Logger.error("OAuthHelper.checkSession", f"Unknown error: {err}")
            return False
        
        
        return True
    
    @staticmethod
    def link_token_via_state(state: str, token: dict) -> any:
        Logger.info("OAuthHelper.link_via_state", f"Linking via state \"{state}\"")

        # Get person based on oauth
        userId = DBManager.get_user_id_from_token(state)

        # Check if user doesn't exist, 99% will succeed
        if userId is None:
            Logger.warn("OAuthHelper.link_via_state", f"User id for state \"{state}\" is None")
            raise FakeStateError(f"User id for state \"{state}\" is None")
        
        # set userid's token from state to token
        DBManager.edit_token_user_id(userId, token)

        return True
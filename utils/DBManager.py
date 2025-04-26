import sqlite3
import json
from . import Config, Logger

# Load in the config, faster than referencing it every time
DBNAME = Config.DBMANAGER_DBNAME

# Variables
db = None
cursor = None

"""
This file is for managing the database.
Instead of accessing server settings through the commands,
all the sql queries are done here.
Please do not modify this at all.
"""

class DBManager:
    @staticmethod
    def connect():
        global db, cursor

        # connect db and store in global variable
        try:
            db = sqlite3.connect(f"{Config.PROGRAM_PATH}/data/{DBNAME}", check_same_thread=False)
            cursor = db.cursor()
        except sqlite3.Error as e:
            Logger.error("DBManager.connect", f"Error connecting to database: {e}")
            exit(1)

        # prepare the db, make sure the table needed exists
        DBManager.prepare()


    @staticmethod
    def prepare():
        global db, cursor

        # Double check the table is created
        cursor.execute("CREATE TABLE IF NOT EXISTS oauth_tokens (id INTEGER PRIMARY KEY, oauthKey TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS guilds_settings (id INTEGER PRIMARY KEY, settings TEXT)")

    # This method will most likely not be used, but just in case :)
    @staticmethod
    def purge():
        global db, cursor

        # Drop the tables
        cursor.execute("DROP TABLE oauth_tokens")
        cursor.execute("DROP TABLE guilds_settings")
        db.commit()

        # Recreate the tables
        DBManager.prepare()

    """
    ░██████╗░██╗░░░░░░█████╗░██████╗░░█████╗░██╗░░░░░
    ██╔════╝░██║░░░░░██╔══██╗██╔══██╗██╔══██╗██║░░░░░
    ██║░░██╗░██║░░░░░██║░░██║██████╦╝███████║██║░░░░░
    ██║░░╚██╗██║░░░░░██║░░██║██╔══██╗██╔══██║██║░░░░░
    ╚██████╔╝███████╗╚█████╔╝██████╦╝██║░░██║███████╗
    ░╚═════╝░╚══════╝░╚════╝░╚═════╝░╚═╝░░╚═╝╚══════╝
    """

    @staticmethod
    def select_guild(guild_id: int):
        global db, cursor

        # Select the guild
        try:
            cursor.execute(f"SELECT * FROM guilds_settings WHERE id= ? ", (guild_id, ))
            guild = cursor.fetchone()
        except sqlite3.Error as e:
            Logger.error("DBManager.select_guild", f"Error selecting guild: {e}")

        return guild
    
    @staticmethod
    def update_guild(guild_id: int, settings: dict):
        global db, cursor

        # Update the guild
        try:
            cursor.execute(f"UPDATE guilds_settings SET settings= ?  WHERE id= ? ", (str(json.dumps(settings)), guild_id))
            db.commit()
        except sqlite3.Error as e:
            Logger.error("DBManager.update_guild", f"Error updating guild: {e}")


    """
    ░██████╗░██╗░░░██╗██╗██╗░░░░░██████╗░░██████╗
    ██╔════╝░██║░░░██║██║██║░░░░░██╔══██╗██╔════╝
    ██║░░██╗░██║░░░██║██║██║░░░░░██║░░██║╚█████╗░
    ██║░░╚██╗██║░░░██║██║██║░░░░░██║░░██║░╚═══██╗
    ╚██████╔╝╚██████╔╝██║███████╗██████╔╝██████╔╝
    ░╚═════╝░░╚═════╝░╚═╝╚══════╝╚═════╝░╚═════╝░
    """

    @staticmethod
    def setup_server(guild_id: int):
        global db, cursor


        # To protect guild settings from unintentionally being overwritten, we check if the guild exists
        guild = DBManager.select_guild(guild_id)

        if guild is not None:
            return

        # Insert the server into the database
        try:
            cursor.execute(f"INSERT INTO guilds_settings (id, settings) VALUES (?, ?)", (guild_id, str(json.dumps(Config.DEFAULT_GUILD_SETTINGS))))
            db.commit()
        except sqlite3.Error as e:
            Logger.error("DBManager.setup_server", f"Error setting up server: {e}")

        Logger.info("DBManager.setup_server", f"Server \"{guild_id}\" successfully setup")

    @staticmethod
    def purge_server(guild_id: int):
        global db, cursor

        # Purge the server from the database
        try:
            cursor.execute(f"DELETE FROM guilds_settings WHERE id= ? ", (guild_id, ))
            db.commit()
        except sqlite3.Error as e:
            Logger.error("DBManager.purge_server", f"Error purging server: {e}")

        Logger.info("DBManager.purge_server", f"Server \"{guild_id}\" successfully purged")

    @staticmethod
    def get_server_settings(guild_id: int):
        global db, cursor

        # Check if the server exists
        guild = DBManager.select_guild(guild_id)

        if guild is None:
            Logger.warn("DBManager.get_server_settings", f"Server \"{guild_id}\" does not exist")
            DBManager.setup_server(guild_id)
            return Config.DEFAULT_GUILD_SETTINGS
        
        # Attempt to return the guild settings.
        # In event of invalid json, purge server and return default settings
        try:
            return json.loads(guild[1])
        except json.JSONDecodeError:
            Logger.info("DBManager.get_server_settings", f"Server \"{guild_id}\" has invalid settings")
            DBManager.purge_server(guild_id)
            DBManager.setup_server(guild_id)
            return Config.DEFAULT_GUILD_SETTINGS
        
    @staticmethod
    def set_server_settings(guild_id: int, settings: dict):
        global db, cursor

        # Check server exists
        DBManager.setup_server(guild_id)

        # TODO: Check if settings are valid, not necessary right now but will be in the future

        # Update the server settings
        DBManager.update_guild(guild_id, settings)

    

    """
    ██╗░░░██╗░██████╗███████╗██████╗░
    ██║░░░██║██╔════╝██╔════╝██╔══██╗
    ██║░░░██║╚█████╗░█████╗░░██████╔╝
    ██║░░░██║░╚═══██╗██╔══╝░░██╔══██╗
    ╚██████╔╝██████╔╝███████╗██║░░██║
    ░╚═════╝░╚═════╝░╚══════╝╚═╝░░╚═╝
    """

    # TODO
    # TODO: Add global methods for user methods. This will make cleaner code and better readability
    # TODO

    @staticmethod
    def add_user(user_id: int, oauth_token: str):
        global db, cursor

        # Insert the user into the database
        # Santization of input is done BEFORE modification of the database
        try:
            cursor.execute("INSERT INTO oauth_tokens (id, oauthKey) VALUES ( ? , ? )", (user_id, oauth_token))
            db.commit()

        except sqlite3.IntegrityError: # Happens when the user already exists
            Logger.warn("DBManager.add_user", f"User \"{user_id}\" already exists")

        except sqlite3.Error as e: # Any other unhandled errors
            Logger.error("DBManager.add_user", f"Error adding user: {e}")

    @staticmethod
    def del_user(user_id: int) -> bool:
        global db, cursor

        Logger.info("DBManager.del_user", f"Deleting user \"{user_id}\"")

        # Delete the user from the database
        # We don't need to santize input since userid is something the user cannot change
        try:
            cursor.execute(f"DELETE FROM oauth_tokens WHERE id= ? ", (user_id))
            db.commit()
        except sqlite3.Error as e:
            Logger.error("DBManager.del_user", f"Error deleting user: {e}")
            return False
        
        return True
    
    @staticmethod
    def check_user_exists(user_id: int):
        global db, cursor

        # Check if the user exists in the database
        try:
            cursor.execute(f"SELECT id FROM oauth_tokens WHERE id= ? ", (user_id, ))
            user = cursor.fetchone()
        except sqlite3.Error as e:
            Logger.error("DBManager.check_user_exists", f"Error checking if user exists: {e}")

        if user is None:
            Logger.warn("DBManager.check_user_exists", f"User \"{user_id}\" does not exist")
            DBManager.add_user(user_id, "null")
            return False

        return True
    
    @staticmethod
    def edit_token_user_id(user_id: int, oauth_token: any):
        global db, cursor

        DBManager.check_user_exists(user_id)

        # Update the user's token in the database
        try:
            if type(oauth_token) is dict:
                cursor.execute(f"UPDATE oauth_tokens SET oauthKey = ? WHERE id = ? ", (json.dumps(oauth_token), user_id))
            else:
                cursor.execute(f"UPDATE oauth_tokens SET oauthKey = ?  WHERE id=  ? ", (oauth_token, user_id))

            db.commit()
        except sqlite3.Error as e:
            Logger.error("DBManager.edit_token_user_id", f"Error editing token: {e}")

    @staticmethod
    def get_user_id_from_token(oauth_token: str):
        global db, cursor

        # Get the user id from the database
        try:
            cursor.execute(f"SELECT id FROM oauth_tokens WHERE oauthKey = ? ", (oauth_token, ))
            user_id = cursor.fetchone()
        except sqlite3.Error as e:
            Logger.error("DBManager.get_user_id_from_token", f"Error getting user id from token: {e}")

        if user_id is None:
            return None

        return user_id[0]

    @staticmethod
    def get_token_from_user_id(user_id: int):
        global db, cursor

        # Check if the user exists
        DBManager.check_user_exists(user_id)

        # Get the token from the database
        try:
            cursor.execute(f"SELECT oauthKey FROM oauth_tokens WHERE id=?", (user_id, ))
            token = cursor.fetchone()
        except sqlite3.Error as e:
            Logger.error("DBManager.get_token_from_user_id", f"Error getting token from user id: {e}")

        # If token is "null" return None
        if token == "null" or token is None:
            Logger.warn("DBManager.get_token_from_user_id", f"Token for user \"{user_id}\" is null")
            return None
        
        """
        Checks whether or not the token is a valid json object
        If it is, format into a dictionary and return it
        If it isn't, return the token as a string (most likely because it's a state token)
        """
        try:
            json.loads(token[0])
        except json.JSONDecodeError:
            return token[0]

        return json.loads(token[0])




    
    # These static methods are for debugging purposes
    @staticmethod
    def drop_table(table: str):
        global db, cursor

        cursor.execute(f"DROP TABLE {table}")
        db.commit()
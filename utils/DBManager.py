import sqlite3
import json
from . import Config, Logger

# Load in the config, faster than referencing it every time
DBNAME = Config.DBMANAGER_DBNAME

# Variables
db = None
cursor = None

class DBManager:
    @staticmethod
    def connect():
        global db, cursor

        # connect db and store in global variable
        try:
            db = sqlite3.connect(f"data/{DBNAME}", check_same_thread=False)
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

    @staticmethod
    def add_user(user_id: int, oauth_token: str):
        global db, cursor

        # Insert the user into the database
        # We are going to santize input before calling the function, doesn't matter
        try:
            cursor.execute(f"INSERT INTO oauth_tokens (id, oauthKey) VALUES ({user_id}, '{oauth_token}')")
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
            cursor.execute(f"DELETE FROM oauth_tokens WHERE id={user_id}")
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
            cursor.execute(f"SELECT id FROM oauth_tokens WHERE id={user_id}")
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
                cursor.execute(f"UPDATE oauth_tokens SET oauthKey='{json.dumps(oauth_token)}' WHERE id={user_id}")
            else:
                cursor.execute(f"UPDATE oauth_tokens SET oauthKey='{oauth_token}' WHERE id={user_id}")

            db.commit()
        except sqlite3.Error as e:
            Logger.error("DBManager.edit_token_user_id", f"Error editing token: {e}")

    @staticmethod
    def get_user_id_from_token(oauth_token: str):
        global db, cursor

        # Get the user id from the database
        try:
            cursor.execute(f"SELECT id FROM oauth_tokens WHERE oauthKey='{oauth_token}'")
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
            cursor.execute(f"SELECT oauthKey FROM oauth_tokens WHERE id={user_id}")
            token = cursor.fetchone()
        except sqlite3.Error as e:
            Logger.error("DBManager.get_token_from_user_id", f"Error getting token from user id: {e}")

        # If token is "null" return None
        if token == "null" or token is None:
            Logger.warn("DBManager.get_token_from_user_id", f"Token for user \"{user_id}\" is null")
            return None
        
        try:
            json.loads(token[0])
        except json.JSONDecodeError:
            return token[0]

        return json.loads(token[0])




    
    # These static methods are for debugging purposes
    @staticmethod
    def drop_table(table: str):
        global db, cursor

        # Drop the table
        cursor.execute(f"DROP TABLE {table}")
        db.commit()
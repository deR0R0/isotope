from time import sleep as wait
from threading import Thread
from utils.LogManager import Logger
from utils.Configuration import *

class RateLimit:

    # Adding users and returning if they bypass the config limit!
    @staticmethod
    def addUser(userId: int) -> bool:
        # Check if they exist
        if userId in rateLimitUsers:
            rateLimitUsers[userId] += 1
        else:
            # If not in the dictionary, add them into it
            rateLimitUsers[userId] = 1

        # Check if the rate limit exceeds
        if rateLimitUsers[userId] > config["messagesTriggerLimit"]:
            Logger.log(f"{userId} got rate limited!")
            return True
        
        # Doesn't exceed rate limit
        return False
    
    # Removing Users
    @staticmethod
    def removeUsers() -> None:
        # Forever
        while True:
            # Remove a command execute
            for i in range(len(rateLimitUsers)):
                listOfUsers = list(rateLimitUsers.keys())
                if rateLimitUsers[listOfUsers[i]] > 0:
                    rateLimitUsers[listOfUsers[i]] -= 1

            try:
                # Delay for config time
                wait(config["removeRateLimitTime"])
            except KeyError:
                Logger.err("Config file seems to be missing key: removeRateLimitTime")


    # Usually execute like this
    @staticmethod
    def startRateLimitThread() -> None:
        t = Thread(target=RateLimit.removeUsers)
        t.start()
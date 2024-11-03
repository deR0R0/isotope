import time
from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger

# Context:
# "IQ" is the currency name, it's the currency name I thought would be the most funny.. idk
class CManager:

    @staticmethod
    def save():
        FManager.write("userMoney.json", userMoney)

    @staticmethod
    def createUser(userId: int) -> bool:
        try:
            userMoney[str(userId)] = defaultUserMoney
        except Exception as err:
            Logger.warn(err)
            return False

        return True
    
    @staticmethod
    def checkUserHasAccount(userId: int) -> None:
        if str(userId) not in userMoney:
            CManager.createUser(userId)

    
    @staticmethod
    def addMoney(userId: int, iq: int) -> bool:
        try:
            CManager.checkUserHasAccount(userId)
            userMoney[str(userId)]["money"] += iq
        except Exception as err:
            Logger.warn(err)
            return False

        return True
            
    @staticmethod
    def setMoney(userId: int, iq: int) -> bool:
        try:
            CManager.checkUserHasAccount(userId)
            userMoney[str(userId)]["money"] = iq
        except Exception as err:
            Logger.warn(err)
            return False

        return True
    

    @staticmethod
    def getMoney(userId: int) -> int:
        CManager.checkUserHasAccount(userId)
        return userMoney[str(userId)]["money"]
    

    # Now we can make the methods that do stuff
    @staticmethod
    def claimDailyReward(userId: int) -> str:
        CManager.checkUserHasAccount(userId)
        if "lastClaimedDaily" in userMoney[str(userId)]:
            if int(userMoney[str(userId)]["lastClaimedDaily"]) < int(time.time()):
                # (lastClaimedDaily + milliseconds in 24 hours) - (current time milliseconds)
                return str((int(userMoney[str(userId)]["lastClaimedDaily"]) + 86400))
            
        # When either they haven't cliamed daily before or they waited 24 hours
        # Add money
        CManager.addMoney(userId, 100)
        # Update last time they claimed daily
        userMoney[str(userId)]["lastClaimedDaily"] = str(int(time.time()))
        CManager.save()
        return "claimed"
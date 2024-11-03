from utils.Configuration import *
from utils.FileManager import FManager
from utils.LogManager import Logger

# Context:
# "IQ" is the currency name, it's the currency name I thought would be the most funny.. idk
class CManager:

    @staticmethod
    def createUser(userId: int) -> bool:
        try:
            userMoney[str(userId)] = defaultUserSettings
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
    
    
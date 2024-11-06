from utils.LogManager import Logger
from utils.Configuration import *
from utils.FileManager import FManager

class Reminder:
    @staticmethod
    def save():
        FManager.write("userPreferences.json", userSettings)


    @staticmethod
    def addReminder(userId: int) -> bool:
        try:
            userSettings[str(userId)]["reminders"]
        except Exception as err:
            Logger.warn(err)
            return False
        
        return True
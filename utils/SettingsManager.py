import os
import sys


from utils.LogManager import Logger
from utils.FileManager import FManager
from utils.Configuration import *
from functools import lru_cache



class SManager:

    @staticmethod
    def createUser(userId: int) -> bool:
        try:
            userSettings[str(userId)] = defaultUserSettings
        except Exception as err:
            Logger.warn(err)
            return False
        
        FManager.write("userPreferences.json", userSettings)
        
        return True


    @staticmethod
    def changeSetting(userId: int, setting: str, value: str) -> str:
        # Check if they are in the settings
        if userId not in userSettings:
            # Create them
            SManager.createUser(userId)

        if setting not in userSettings[str(userId)]:
            if not SManager.handleMissingSetting(userId, setting):
                Logger.warn(f"Unknown Setting: {setting}")
                return "unknownSetting"
            else:
                Logger.log("Successfully Created missing Setting for User!")
        
        # Check if valid option
        if value not in settingOptions[setting]:
            Logger.warn(f"Unknown Option: {value}")
            return "unknownOption"
        
        userSettings[str(userId)][setting] = value
        FManager.write("userPreferences.json", userSettings)
        return "success"
    

    @staticmethod
    def handleMissingSetting(userId: int, setting: str) -> bool:
        try:
            # Make sure the setting actually exists
            if setting not in settingOptions.keys():
                return False
            
            userSettings[str(userId)][setting] = defaultUserSettings[setting]
            return True
        except Exception as err:
            Logger.warn(err)
            return False


    @staticmethod
    def resetDefault(userId: int) -> bool:
        try:
            userSettings[str(userId)] = defaultUserSettings
        except Exception as err:
            Logger.warn(err)
            return False
        
        return True
    

    @staticmethod
    def checkPrivacy(userId: int) -> bool:
        if str(userId) not in userSettings:
            SManager.createUser(userId)

        if userSettings[str(userId)]["privacy"].lower() == "private":
            return False
        else:
            return True
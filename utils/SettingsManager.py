import os
import sys


from utils.LogManager import Logger
from utils.FileManager import FManager
from utils.Configuration import *
from functools import lru_cache



class SManager:

    @staticmethod
    def save():
        FManager.write("userPreferences.json", userSettings)

    @staticmethod
    def createUser(userId: int) -> bool:
        try:
            userSettings[str(userId)] = defaultUserSettings
        except Exception as err:
            Logger.warn(err)
            return False
        
        SManager.save()
        
        return True
    
    @staticmethod
    def checkUserExist(userId: int) -> bool:
        if str(userId) not in userSettings:
            return False
        
        return True


    @staticmethod
    def changeSetting(userId: int, setting: str, value: any) -> str:
        # Check if they are in the settings
        if not SManager.checkUserExist(userId):
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
        SManager.save()
        return "success"
    

    @staticmethod
    def handleMissingSetting(userId: int, setting: str) -> bool:
        try:
            # Make sure the setting actually exists
            if setting not in settingOptions.keys():
                return False
            
            userSettings[str(userId)][setting] = defaultUserSettings[setting]
        except Exception as err:
            Logger.warn(err)
            return False
        
        Logger.log(f"Added missing setting for {userId}")

        return True
        
    @staticmethod
    def handleExtraSetting(userId: int, setting: str) -> bool:
        try:
            del userSettings[str(userId)][setting]
        except Exception as err:
            Logger.warn(err)
            return False
        Logger.log(f"Removed extra setting for {userId}")

        return True
        
    @staticmethod
    def updateAllSettings(userId: int) -> bool:
        if not SManager.checkUserExist(userId):
            SManager.createUser(userId)

        # Check for missing settings
        for setting in settingOptions.keys():
            if setting not in userSettings[str(userId)]:
                SManager.handleMissingSetting(userId, setting)

        # Check for extra settings
        for setting in userSettings[str(userId)]:
            if setting not in settingOptions:
                SManager.handleExtraSetting(userId, setting)

        SManager.save()

        return True

    @staticmethod
    def resetDefault(userId: int) -> bool:
        try:
            userSettings[str(userId)] = defaultUserSettings
        except Exception as err:
            Logger.warn(err)
            return False
        SManager.save()
        return True
    

    @staticmethod
    def checkPrivacy(userId: int) -> bool:
        if not SManager.checkUserExist(userId):
            SManager.createUser(userId)

        if userSettings[str(userId)]["privacy"].lower() == "private":
            return False
        else:
            return True
        
    @staticmethod
    def checkAllowDMs(userId: int) -> bool:
        if not SManager.checkUserExist(userId):
            SManager.createUser(userId)

        return userSettings[str(userId)]["allowDMs"] == "True"
        
    @staticmethod
    def getSettings(userId: int) -> dict:
        # This is to check if user has all updated settings
        if not SManager.updateAllSettings(userId):
            Logger.warn("There was an error while updating someone's settings")
            return {"error": "Error"}

        return userSettings[str(userId)]
    
    @staticmethod
    def removeUser(userId: int) -> bool:
        if not SManager.checkUserExist(userId):
            SManager.createUser(userId)

        del userSettings[str(userId)]
        SManager.save()
        return True
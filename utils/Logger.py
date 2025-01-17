import os
import sys
from datetime import datetime
from colorama import Fore as fore

from utils import Config

DATE_COLOR, NORM_COLOR, LOCATION_COLOR, INFO_COLOR, WARN_COLOR, ERROR_COLOR = Config.LOGGER_DATE_COLOR, Config.LOGGER_NORM_COLOR, Config.LOGGER_LOCATION_COLOR, Config.LOGGER_INFO_COLOR, Config.LOGGER_WARN_COLOR, Config.LOGGER_ERROR_COLOR

class Logger:
    @staticmethod
    def saveToFile(location: str, message: str):
        # Default
        writingMode: str = "w"

        # Check if log file exists, if it does, turn on append mode
        if os.path.exists(f"{Config.PROGRAM_PATH}/data/logs.txt"):
            writingMode = "a"

        # Check if directory exists; if not, create on
        if not os.path.isdir(f"{Config.PROGRAM_PATH}/data"):
            os.makedirs(f"{Config.PROGRAM_PATH}/data")

        # Open file with the proper writing mode
        try:
            with open(f"{Config.PROGRAM_PATH}/data/logs.txt", writingMode) as f:
                f.write(f"{datetime.now().replace(microsecond=0)} | {location} | {message}\n")
        except Exception as err:
            print(err)

    @staticmethod
    def info(location: str, message: str):
        print(f"{DATE_COLOR}{datetime.now().replace(microsecond=0)}{NORM_COLOR} | {LOCATION_COLOR}{location}{NORM_COLOR} | {INFO_COLOR}{message}")
        Logger.saveToFile(location, message)
        return
    
    @staticmethod
    def warn(location: str, message: str):
        print(f"{DATE_COLOR}{datetime.now().replace(microsecond=0)}{NORM_COLOR} | {LOCATION_COLOR}{location}{NORM_COLOR} | {WARN_COLOR}{message}")
        Logger.saveToFile(location, message)
        return
    
    @staticmethod
    def error(location: str, message: str):
        print(f"{DATE_COLOR}{datetime.now().replace(microsecond=0)}{NORM_COLOR} | {LOCATION_COLOR}{location}{NORM_COLOR} | {ERROR_COLOR}{message}")
        Logger.saveToFile(location, message)
        return
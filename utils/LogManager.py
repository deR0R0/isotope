import datetime
import os
from colorama import Fore as fore

# Config
logFileName = "logs.txt"
logColor = fore.LIGHTBLUE_EX
warnColor = fore.LIGHTYELLOW_EX
errColor = fore.LIGHTRED_EX
cmdColor = fore.LIGHTBLUE_EX
servColor = fore.LIGHTBLUE_EX

# Get the path of the main process
progPath = ""


# Log Manager Class (for logging!)
class Logger:

    # Set Path
    @staticmethod
    def setPath(path: str) -> None:
        global progPath
        progPath = path
    
    # Save Logs
    @staticmethod
    def saveLogs(content: str) -> bool:
        # Attempt to write to file
        try:
            with open(rf"{progPath}/data/{logFileName}", 'a') as logFile:
                logFile.write(f"{content}\n")
        # When the file isn't found, write one
        except FileNotFoundError:
            with open(rf"{progPath}/data/{logFileName}", 'w') as logFile:
                logFile.write(f"{content}\n")
        # Any unknown exception will return false
        except Exception as err:
            print(err)
            return False
        
        return True
    
    # Default Log
    @staticmethod
    def log(message: str) -> None:
        global logColor
        # Print it out
        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {logColor}INFO | {fore.WHITE}{message}")
        # Save it
        if not Logger.saveLogs(f"{datetime.datetime.now().replace(microsecond=0)} INFO | {message}"):
            print("Error While Saving File")

    # Warn (handled errors)
    @staticmethod
    def warn(message: str) -> None:
        global warnColor

        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {warnColor}WARN | {fore.WHITE}{message}")
        if not Logger.saveLogs(f"{datetime.datetime.now().replace(microsecond=0)} WARN | {message}"):
            print("Error While Saving File")

    # Error (unhandled error)
    @staticmethod
    def err(message: str) -> None:
        global errColor

        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {errColor}ERR  | {fore.WHITE}{message}")
        if not Logger.saveLogs(f"{datetime.datetime.now().replace(microsecond=0)} ERR  | {message}"):
            print("Error While Saving File")

    # Command (button presses, used command)
    @staticmethod
    def cmd(message: str) -> None:
        global cmdColor

        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {cmdColor}CMD  | {fore.WHITE}{message}")
        if not Logger.saveLogs(f"{datetime.datetime.now().replace(microsecond=0)} CMD  | {message}"):
            print("Error While Saving File")

    # Server
    @staticmethod
    def serv(message: str) -> None:
        global servColor

        print(fore.LIGHTBLACK_EX + f"{datetime.datetime.now().replace(microsecond=0)} {servColor}SERV | {fore.WHITE}{message}")
        if not Logger.saveLogs(f"{datetime.datetime.now().replace(microsecond=0)} SERV | {message}"):
            print("Error While Saving File")

    @staticmethod
    def test() -> bool:
        try:
            Logger.log("Log")
            Logger.warn("Warn")
            Logger.err("Error")
            Logger.cmd("Cmd")
            return True
        except Exception:
            return False


if __name__ == "__main__":
    Logger.log("This file is not intended to be run. Please run the test using Logger.test()")
    
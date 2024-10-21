# Import system stuff
import sys
import os
import json
from colorama import Fore as fore

# Import Logmanager for logging
from utils.LogManager import Logger

# Config
testTxt = "Hello World"
testJson = {"Test": "Hello World"}
# Variables
progPath = ""


# File manager class 
class FManager:

    # Set Path
    @staticmethod
    def setPath(path: str) -> None:
        global progPath
        progPath = path
        Logger.log("Set path for FileManager")
    
    # Read the file and return the file contents
    @staticmethod
    def read(file: str) -> any:
        try:
            with open(rf"{progPath}/data/{file}", 'r') as fFile:
                Logger.log(f"Reading {file} file!")
                if ".txt" in file:
                    return fFile.read()
                elif ".json" in file:
                    return json.load(fFile)
                else:
                    Logger.warn(f"Unknown Data Type: {file}")
                    return
        except FileNotFoundError:
            Logger.log(f"Couldn't find file: {file}")

    # Write file
    @staticmethod
    def write(file: str, content: any) -> bool:
        try:
            with open(rf"{progPath}/data/{file}", 'w') as fFile:
                Logger.log(f"Writing file: {file}")
                if ".txt" in file:
                    fFile.write(content)
                elif ".json" in file:
                    json.dump(content, fFile, indent=4)
                else:
                    Logger.warn(f"Unknown Data Type: {file}")
                    return False
                
            return True
        except Exception as err:
            Logger.err(err)
            return False
        
    # Test
    @staticmethod
    def test() -> bool:
        try:
            # Test writing first
            if not FManager.write("test.txt", testTxt):
                Logger.warn("Error while testing writing test.txt")
                return False
            
            if not FManager.write("test.json", testJson):
                Logger.warn("Error while testing writing test.json")
                return False
            
            # Then test reading
            if FManager.read("test.txt") != testTxt:
                Logger.warn("Error while testing reading test.txt")
                return False
            
            if FManager.read("test.json") != testJson:
                Logger.warn("Error while testing reading test.json")
                return False
            
            return True
        except Exception as err:
            Logger.err(err)
            return False



if __name__ == "__main__":
    Logger.log("This file is not intended to be run. Please test this by using FManager.test()")
from flask import Flask, render_template, request
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import InvalidGrantError
import threading
import sys
import os
from utils.LogManager import Logger
from utils.Configuration import *
from utils.FileManager import FManager

# Config
oauthLink = "http://localhost:80/authorize"


app = Flask(__name__)

class WebServer:
    @staticmethod
    def startWebSever() -> None:
        t = threading.Thread(target=run)
        t.start()



@app.route('/')
def index():
    return ""
    #return render_template("./index.html")

@app.route('/authorize')
def authorize():
    global oauthUsers
    # If the code doesn't exist
    if len(request.args) == 0:
        return "Go to discord and click on the link"
    # Get auth code and token
    try:
        auth_code = request.args.get("code")
        state = request.args.get("state")
        Logger.serv(f"Recieved Get Request for {auth_code}")
        oauth = OAuth2Session(client_id=CLIENTID, redirect_uri=oauthLink, scope="read")
        token = oauth.fetch_token("https://ion.tjhsst.edu/oauth/token", code=auth_code, client_secret=OAUTHKEY)
    except InvalidGrantError:
        return {"Error": "Invalid Token, go back to discord!"}
    except Exception as err:
        Logger.err(err)
        return "An Unexpected Error has occured! Ping @deroro_ with the follow: " + str(err)
    
    # Now match and set
    oauthusersList = list(oauthUsers)
    for i in range(len(oauthusersList)):
        if oauthUsers[oauthusersList[i]] == state:
            oauthUsers[oauthusersList[i]] = oauth
            oauthUsersTokens[oauthusersList[i]] = token
            Logger.serv("Successfully added user!")

    oauthusersList = None
    oauth = None
    auth_code = None
    state = None
    # Write to File
    FManager.write("tokens.json", oauthUsersTokens)
    # Return
    return token
    #return render_template("./success/success.html")

def run():
    app.run(host="0.0.0.0", port=80)


if __name__ == "__main__":
    Logger.serv("This file is not meant to be run. Please use the main.py or main process to run this file")
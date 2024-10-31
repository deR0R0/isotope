from flask import Flask, render_template, request
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import InvalidGrantError
import threading
import sys
import os
from utils.LogManager import Logger
from utils.Configuration import *
from utils.FileManager import FManager
from utils.OauthManager import OManager

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
    auth_code = request.args.get("code")
    state = request.args.get("state")
    if OManager.linkOauth(authCode=auth_code, state=state):
        pass
    else:
        return "Unknown Error"

    # Return
    return "Successfully Connected, you now may close this page :)"
    #return render_template("./success/success.html")

def run():
    app.run(host="0.0.0.0", port=80)


if __name__ == "__main__":
    Logger.serv("This file is not meant to be run. Please use the main.py or main process to run this file")
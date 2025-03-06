import sys
from threading import Thread
from flask import Flask, request, render_template
from oauthlib.oauth2 import InvalidGrantError

sys.path.insert(1, sys.path[0].replace("commands", ""))
from utils import Logger, Config, DBManager, CUtils, OAuthHelper
from utils.Config import client, oauthSession

app = Flask(__name__)

"""
We are using normal flask for the webserver
We aren't expecting high traffic, otherwise we would use flask async
"""

@app.route("/")
def home():
    return "isotope, the home of terrible code :)"

@app.route("/authorize", methods=["GET"])
def authorize():
    Logger.info("app.authorize", "Authorize Page Called")

    # Check if command is disabled
    if CUtils.check_disabled("web_page"):
        return "authorization/verification is currently disabled"
    
    # Check if normal request
    if len(request.args) < 2:
        return "please use discord to authorize"

    # Grab request args
    code = request.args.get("code")
    state = request.args.get("state")

    if code == None or state == None:
        return "code/state is empty"

    # Fetch token and link with the user
    try:
        token = oauthSession.fetch_token(Config.ION_TOKEN_URL, code=code, client_secret=Config.ION_CLIENT_SECRET)
    except InvalidGrantError:
        return "nice try, use a real session now"
    except Exception as err:
        Logger.error("app.authorize", f"Error fetching token: {err}")
        return "err"
    
    user = DBManager.get_user_id_from_token(state)
    res = OAuthHelper.link_token_via_state(state, dict(token))

    # send the correct response back
    match res:
        case "sql_injection":
            return "nice try"
        case "not_real_session":
            return "use a real session"
        case _:
            return "success"


def run():
    app.run(host="0.0.0.0", port=1211)

def run_via_thread():
    t = Thread(target=run)
    t.start()
    return
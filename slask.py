from glob import glob
import importlib
import json
import os
import re
import sys
import traceback

from flask import Flask, request
app = Flask(__name__)

curdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curdir)

from config import config
from token import slack_token

slack = Slack(token)

@app.route("/", methods=['POST'])
def main():
    username = config.get("username", "slask")
    icon = config.get("icon", ":poop:")

    # ignore message we sent
    msguser = request.form.get("user_name", "").strip()
    if username == msguser or msguser.lower() == "slackbot":
        return ""

    text = "hi colin!"
    response = {
        "text": text,
        "username": username,
        "icon_emoji": icon,
        "parse": "full",
    }
    return json.dumps(response)

if __name__ == "__main__":
    app.run()

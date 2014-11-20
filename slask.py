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

import slask_utils
from config import config

def handle_message(message):
    if re.findall(r"^status", text, flags=re.IGNORECASE):
        return slack_utils.status_for_user(message.get("user_name"))
    return "nothing found :("

@app.route("/", methods=['POST'])
def main():
    username = config.get("username", "slask")
    icon = config.get("icon", ":poop:")

    # ignore message we sent
    msguser = request.form.get("user_name", "").strip()
    if username == msguser or msguser.lower() == "slackbot":
        return ""

    text = handle_message(request.form)

    response = {
        "text": text,
        "username": username,
        "icon_emoji": icon,
        "parse": "full",
    }
    return json.dumps(response)

if __name__ == "__main__":
    app.run()

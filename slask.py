from glob import glob
import importlib
import json
import os
import re
import sys
import traceback
import urllib

from flask import Flask, request

app = Flask(__name__)

curdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curdir)

import debt_utils
from config import config

def handle_message(message):
    if re.findall(r"^status", message.get("text", ""), flags=re.IGNORECASE):
        return debt_utils.status_for_user(message.get("user_id"))
    if re.findall(r"^transactions", message.get("text", ""), flags=re.IGNORECASE):
        transactions = debt_utils.transactions(message.get("user_id"))
        if len(transactions):
            return "\n".join([urllib.unquote(m.get("text", "")) for m in transactions])
    return "nothing found :("

@app.route("/", methods=['POST'])
def main():
    username = config.get("username", "slask")
    icon = config.get("icon", ":poop:")

    # ignore message we sent
    msguser = request.form.get("user_name", "").strip()
    if username == msguser or msguser.lower() == "slackbot":
        return ""

    text = repr(request.form)
    try:
        text += "\n\n" + handle_message(request.form) 
    except Exception as err:
        text += "\n\n" + str(err)

    response = {
        "text": text,
        "username": username,
        "icon_emoji": icon,
        "parse": "full",
    }
    return json.dumps(response)

if __name__ == "__main__":
    app.run()

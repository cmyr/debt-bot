import re
import traceback

from flask import Flask, request, jsonify


from . import debt_utils
from .config import config

app = Flask(__name__)


def handle_message(message):
    # 'help'
    if re.findall(r"^help", message.get("text", ""), flags=re.IGNORECASE):
        return debt_utils.help_message()
    # 'status'
    if re.findall(r"^status", message.get("text", ""), flags=re.IGNORECASE):
        return debt_utils.status_for_user(message.get("user_id"))
    # 'debug'
    if re.findall(r"^debug", message.get("text", ""), flags=re.IGNORECASE):
        errors = debt_utils.printable_transactions(message.get('user_id'), only_errors=True)
        return '\n'.join(errors)
    # 'transactions'
    if re.findall(r"^transactions", message.get("text", ""), flags=re.IGNORECASE):
        transactions = debt_utils.printable_transactions(message.get("user_id"))
        return "\n".join(transactions)

    return None


@app.route("/", methods=['POST'])
def main():
    username = config.get("username", "slask")
    icon = config.get("icon", ":poop:")

    # ignore message we sent
    msguser = request.form.get("user_name", "").strip()
    if username == msguser or msguser.lower() == "slackbot":
        return ""

    text = None
    try:
        text = handle_message(request.form)
    except Exception as err:
        text = str(msg.form) + traceback.format_exc()

    if not text:
        return ""

    response = {
        "text": text,
        "username": username,
        "icon_emoji": icon,
        "parse": "full",
    }
    return jsonify(response)


@app.route('/status')
def status():
    return '\n'.join(debt_utils.status_for_user('U0G3PBHQR'))

if __name__ == "__main__":
    app.run()

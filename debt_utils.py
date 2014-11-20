# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import re
from collections import defaultdict

from slacker import Slacker
from token import slack_token

slack = Slacker(slack_token)

DEBT_CHANNEL_ID = 'C02CWS8H0'

def list_channels():
    response = slack.channels.list()
    channels = [{'id': c['id'], 'name': c['name']} for c in response.body['channels']]
    print(channels)

def users():
    response = slack.users.list()
    return {m['id']: m['name'] for m in response.body['members']}

def get_channel_history(channel_id):
    response = slack.channels.history(channel = channel_id, count = 1000)
    return [m for m in response.body['messages'] if m.get('text')]

def parse_debt_message(message, user):
    parsed = re.search(r'<@(.*)>(.*)<@(.*?)>.?([0-9]+)\$?(.*)', message)
    if parsed:
        if parsed.group(1) == user:
             return (parsed.group(3), -int(parsed.group(4)))
        elif parsed.group(3) == user:
            return (parsed.group(1), int(parsed.group(4)))
        else:
            print(parsed.groups())
    # else:
        # print(message)

def status_for_user(user):
    user_list = users()
    balances = defaultdict(int)
    messages = get_channel_history(DEBT_CHANNEL_ID)
    messages = [m for m in messages if re.search(user, m.get('text', ''))]
    for m in messages:
        transaction = parse_debt_message(m.get('text'), user)
        if transaction:
            balances[transaction[0]] += transaction[1]
    
    responses = list()
    for user_id, value in balances.items():
        if value > 0:
            responses.append("%s owes you $%d" % (user_list[user_id], abs(value)))
        else:
            responses.append("you owe %s $%d" % (user_list[user_id], abs(value)))
    if len(responses):
        return "\n".join(responses)
    else:
        return "%s, you are ominously debt free" % user_list.get(user, user)

        
def main():
    print(status_for_user("U024H5KK7"))

if __name__ == "__main__":
    main()
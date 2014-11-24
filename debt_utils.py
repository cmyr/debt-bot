# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import re
from collections import defaultdict, namedtuple

from slacker import Slacker
from token import slack_token

slack = Slacker(slack_token)

DEBT_CHANNEL_ID = 'C02CWS8H0'

Transaction = namedtuple("Transaction", ["first_party", "operator", "second_party", "ammount", "more_info"])

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
    transaction = parse_transaction(message)
    if transaction:
        if transaction.first_party == user:
             return (transaction.second_party, -float(transaction.ammount))
        elif transaction.second_party == user:
            return (transaction.first_party, float(transaction.ammount))
        else:
            print('weird transaction: ', transaction)
    else:
        print("failed to find transaction:", message)


def transactions(user_id):
    messages = get_channel_history(DEBT_CHANNEL_ID)
    messages = [m for m in messages if re.search(user_id, m.get('text', ''))]
    return messages

def parse_transaction(text):
    parsed = re.search(r'<?@(\w+)>?\s*(\S*)\s*<?@(\w+)>?\s.?\$?([0-9\.]+)\$?(.*)', text)
    if parsed:
        return Transaction(parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(4), parsed.group(5))
    parsed = re.search(r'<?@(\w+)>?\s*(\S*)\s*<?@(\w+)>?\s(.*?)([0-9\.]+)', text)
    if parsed:
        return Transaction(parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(5), parsed.group(4))
    # parsed = re.search(r'(@\w*)(.*)<@(.*?)>(.*?)([0-9\.]+)', text)


def status_for_user(user_id):
    user_list = users()
    balances = defaultdict(float)
    unparsed = list()
    messages = transactions(user_id)
    for m in messages:
        transaction = parse_debt_message(m.get('text'), user_id)
        if transaction:
            balances[transaction[0]] += transaction[1]
        else: unparsed.append(m.get('text'))
    
    responses = list()
    response_str = ""
    for other_user_id, value in balances.items():
        if value > 0:
            responses.append("%s owes you $%0.2f" % (user_list.get(other_user_id, other_user_id), abs(value)))
        elif value < 0:
            responses.append("you owe %s $%0.2f" % (user_list.get(other_user_id, other_user_id), abs(value)))
    if len(responses):
        response_str = "\n".join(responses)
    else:
        response_str = "%s (%s), you are ominously debt free" % (user_list.get(user_id, "<$NAME NOT FOUND$>"), user_id)

    if len(unparsed):
        response_str += "\n" + "\n".join(["unabled to parse message: %s" % m for m in unparsed])

    return response_str


def _all_channel_posts():
    all_messages = get_channel_history(DEBT_CHANNEL_ID)
    for message in all_messages:
        text = message.get('text')
        parsed = re.search(r'<@(.*)>(.*)<@(.*?)>.?\$?([0-9\.]+)\$?(.*)', text)
        if parsed:
            transaction = Transaction(parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(4), parsed.group(5))
            print(transaction)
        else:
            parsed = re.search(r'<@(.*)>(.*)<@(.*?)>(.*?)([0-9\.]+)', text)
            if parsed:
                transaction = Transaction(parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(5), parsed.group(4))
                print(transaction)
            else:
                print(text)



def main():
    print(status_for_user("U02G8SVCB"))
    # print(transactions("U02G8SVCB"))
    # _all_channel_posts()

if __name__ == "__main__":
    main()
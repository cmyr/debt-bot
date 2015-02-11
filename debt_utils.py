# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import re
from collections import defaultdict, namedtuple
import operator

from slacker import Slacker
from token import slack_token
from aliases import DEBT_BOT_ALIASES

from transaction import Transaction
slack = Slacker(slack_token)

DEBT_CHANNEL_ID = 'C02CWS8H0'

def help_message():
    return """
    Welcome to #debt! I respond to the following commands:
    help: show this menu
    status: show your debtors and creditors
    transactions: show all of your transactions

    new transactions must be in the following format:
    (*user1*) (*operator*) *user2* (*value*) (*notes*), where:
    *user1 and *user2* are names, prefixed with an at-sign;
    *operator* is one of -> or <-;
    *value* is a numerical value;
    *notes* is a field for entering additional text.
    """

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

def transactions(user_id):
    messages = get_channel_history(DEBT_CHANNEL_ID)
    messages = [m for m in messages if re.search(user_id, m.get('text', ''))]
    return messages

def status_for_user(user_id, show_unparsed = False):
    user_list = users()
    balances = defaultdict(float)
    unparsed = list()
    messages = transactions(user_id)
    for m in messages:
        transaction = Transaction(m.get('text'))
        if transaction.parsed:
            value, party = transaction.obligation_to_user(user_id)
            balances[party] += value
        else: unparsed.append(m.get('text'))
   
    response = response_for_balances(balances, user_list)
    if show_unparsed and len(unparsed):
        response += "\n" + "\n".join(["unabled to parse message: %s" % m for m in unparsed])
    return response

def response_for_balances(balances, user_list):
    responses = list()
    response_str = ""
    for other_user_id, value in reversed(sorted(
        balances.items(),
        key=operator.itemgetter(1))):
        if value > 0:
            responses.append("*%s* owes you $%0.2f" % (user_name_for_id(other_user_id, user_list), abs(value)))
        elif value < 0:
            responses.append("you owe *%s* $%0.2f" % (user_name_for_id(other_user_id, user_list), abs(value)))
    if len(responses):
        response_str = "\n".join(responses)
    else:
        response_str = "%s (%s), you are ominously debt free" % (user_list.get(user_id, "<$NAME NOT FOUND$>"), user_id)
    return response_str
    
def user_name_for_id(user_id, user_list):
    user = user_list.get(user_id, user_id).lower()
    return DEBT_BOT_ALIASES.get(user, user())

# def _all_channel_posts():
#     all_messages = get_channel_history(DEBT_CHANNEL_ID)
#     for message in all_messages:
#         text = message.get('text')
#         parsed = re.search(r'<@(.*)>(.*)<@(.*?)>.?\$?([0-9\.]+)\$?(.*)', text)
#         if parsed:
#             transaction = Transaction(parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(4), parsed.group(5))
#             print(transaction)
#         else:
#             parsed = re.search(r'<@(.*)>(.*)<@(.*?)>(.*?)([0-9\.]+)', text)
#             if parsed:
#                 transaction = Transaction(parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(5), parsed.group(4))
#                 print(transaction)
#             else:
#                 print(text)


def all_transactions():
    all_messages = [m.get('text') for m in get_channel_history(DEBT_CHANNEL_ID)]
    return [Transaction(p) for p in all_messages if p != None]

def main():
    print(status_for_user("U024H5LFB", True))
    # print([u[1] for u in users().items()])
    # print(get_channel_history(DEBT_CHANNEL_ID))
    # print([h.get('text') for h in get_channel_history(DEBT_CHANNEL_ID)])
    # print(all_transactions(), sep='\n')
    # print(transactions("U02G8SVCB"))
    # _all_channel_posts()

    # transactions = all_transactions()
    # for t in transactions:
    #     if not t.parsed:
    #         print(t.raw_text, "|||", t)

if __name__ == "__main__":
    main()
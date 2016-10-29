# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import re
from collections import defaultdict, namedtuple
import operator
import sys
# import urllib
from HTMLParser import HTMLParser

from slacker import Slacker
from slack_token import slack_token
from aliases import DEBT_BOT_ALIASES

from transaction import Transaction, TransactionParseError
slack = Slacker(slack_token)

DEBT_CHANNEL_ID = 'C02CWS8H0'


def help_message():
    return """
    Welcome to #debt! I respond to the following commands:
    `help`: show this menu
    `status`: show your debtors and creditors
    `transactions`: show all of your transactions
    `debug`: print parse errors

    new transactions must be in the following format:
    (*user1*) (*operator*) *user2* (*value*) where:
    *user1 and *user2* are names, prefixed with an at-sign;
    *operator* is one of < or >;
    *value* is a numerical value;
    """


def list_channels():
    response = slack.channels.list()
    channels = [{'id': c['id'], 'name': c['name']}
                for c in response.body['channels']]
    print(channels)


def users():
    response = slack.users.list()
    return {m['id']: m['name'] for m in response.body['members']}


def get_channel_history(channel_id):
    response = slack.channels.history(channel=channel_id, count=1000)
    results = [m for m in response.body['messages'] if m.get('text')]

    while response.body['has_more']:
        oldest = min(m.get('ts') for m in response.body['messages'] if m.get('ts'))
        response = slack.channels.history(channel=channel_id, count=1000, latest=oldest)
        results.extend([m for m in response.body['messages'] if m.get('text')])
    # fix > etc:
    html = HTMLParser()
    for m in results:
        m['text'] = html.unescape(m['text'])
    return results


def transactions(user_id):
    messages = get_channel_history(DEBT_CHANNEL_ID)
    messages = [m for m in messages if re.search(user_id, m.get('text', ''))]
    return messages


def printable_transactions(user_id, only_errors=False):
    def stringify_transaction(t):
        try:
            t = Transaction(m.get('text'))
            if t.parsed and not only_errors:
                return m.get('text')
            if t.parsed and only_errors:
                return None
            else:
                return 'SKIPPED ' + m.get('text')
        except TransactionParseError as err:
            return '❌FAILED! {}\n error ({})'.format(
                m.get('text'), err)

    messages = transactions(user_id)
    results = [stringify_transaction(m.get('text')) for m in messages]
    return [r for r in results if r]


def sum_obligations(messages, user_id):
    balances = defaultdict(float)
    errors = list()
    for m in messages:
        try:
            t = Transaction(m)
            value, party = t.obligation_to_user(user_id)
            balances[party] += value
        except TransactionParseError as err:
            errors.append(err)
    return balances, errors


def status_for_user(user_id, show_unparsed=False):
    user_list = users()
    messages = transactions(user_id)
    balances, errors = sum_obligations([m.get('text') for m in messages], user_id)

    response = response_for_balances(balances, user_list, user_id)
    if show_unparsed and len(unparsed):
        response = "{}\n{}".format(
            response,
            "\n".join(["error %s in message %s" % (e, m) for e, m in errors]))

    total_value = sum(b for b in balances.values())
    decorator = decoration_for_balance(total_value)
    preamble = "%s status for %s %s\n" % (
        decorator, user_name_for_id(user_id, user_list), decorator)
    return preamble + response


def response_for_balances(balances, user_list, user_id):
    responses = list()
    response_str = ""
    for other_user_id, value in reversed(sorted(
            balances.items(),
            key=operator.itemgetter(1))):
        if value > 0:
            responses.append(
                "*%s* owes you $%0.2f" % (user_name_for_id(other_user_id, user_list), abs(value)))
        elif value < 0:
            responses.append(
                "you owe *%s* $%0.2f" % (user_name_for_id(other_user_id, user_list), abs(value)))
    if len(responses):
        response_str = "\n".join(responses)
    else:
        response_str = " %s (%s), you are ominously debt free" % (
            user_list.get(user_id, "<$NAME NOT FOUND$>"), user_id)
    return response_str


def decoration_for_balance(balance):
    if balance > 0:
        return "📈"
    else:
        return "📉"


def user_name_for_id(user_id, user_list):
    user = user_list.get(user_id, user_id).lower()
    return DEBT_BOT_ALIASES.get(user, user)


def all_transactions():
    all_messages = [m.get('text')
                    for m in get_channel_history(DEBT_CHANNEL_ID)]
    return [Transaction(p) for p in all_messages if p is not None]


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

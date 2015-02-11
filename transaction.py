# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals
import re
from collections import namedtuple

DEBUG = False

# these are operator types. This is annoying. I'd love an enum
FROM_KEY = "from"
TO_KEY = "to"

RawTransaction = namedtuple(
    "Transaction",
    ["first_party", "operator", "second_party", "value", "notes"])


class Transaction(object):

    """A transaction represents a debt relationship between two parties"""
    debtor = None
    creditor = None
    value = None
    currency = None
    notes = None

    raw_text = None
    raw_transaction = None

    @property
    def parsed(self):
        return True if self.raw_transaction else False

    def __init__(self, input_str):
        super(Transaction, self).__init__()
        self.raw_text = input_str
        self.raw_transaction = self.componentize_transaction(
            input_str,
            [self.componentize1, self.componentize2]
        )
        self.parse_components(self.raw_transaction)

    def __repr__(self):
        if self.parsed:
            return "%s %s %s %s %s" % (
                self.debtor, self.creditor, self.value,
                self.currency, self.notes)
        return "No Transaction"

    def obligation_to_user(self, user):
        if user == self.creditor:
            return self.value, self.debtor
        if user == self.debtor:
            return -self.value, self.creditor
        return 0, None

    def componentize_transaction(self, text, funcs):
        subbed = re.sub(r'<@(\w+)>', r'@\1 ', text)
        if DEBUG:
            print(text)
            print(subbed)
        for f in funcs:
            result = f(subbed)
            if result:
                return result

    def componentize1(self, text):
        parsed = re.search(
            r'@(\w+).?\s*(\S*)\s*@(\w+)\s+\$?([0-9\.]+)\$?(.*)', text)
        if parsed:
            return RawTransaction(
                parsed.group(1), parsed.group(2), parsed.group(3),
                parsed.group(4), parsed.group(5))

    def componentize2(self, text):
        parsed = re.search(r'@(\w+).?\s*(\S*)\s*(\w+)\s(.*?)([0-9\.]+)', text)
        if parsed:
            return RawTransaction(
                parsed.group(1), parsed.group(2), parsed.group(3),
                parsed.group(5), parsed.group(4))

    def parse_components(self, raw_transaction):
        if raw_transaction:
            if DEBUG:
                print(raw_transaction)
            operator = self.parse_operator(raw_transaction.operator)
            if operator == TO_KEY:
                self.debtor = raw_transaction.first_party
                self.creditor = raw_transaction.second_party
            elif operator == FROM_KEY:
                self.debtor = raw_transaction.second_party
                self.creditor = raw_transaction.first_party

            self.operator = raw_transaction.operator
            self.value = float(raw_transaction.value)
            if raw_transaction.notes != "":
                self.notes = raw_transaction.notes

    def parse_operator(self, operator_text):
        if operator_text == "-&gt;":
            return TO_KEY
        if operator_text == "-&lt;":
            return FROM_KEY


def test():
    tests = [
        '<@U024H4SR1> -&gt; <@U024H5LFB> $15 (thai food)',
        '<@U024H5KK7> -&gt; <@U024H5LFB> 20$',
        '<@U024H5KK7> -&gt; <@U024H5LFB> $10 sandwich place',
        '<@U024H5KK7> -&lt; <@U024H5LFB> $10 sandwich place',
        '<@U024H4SR1|will> set the channel topic: trying to incur \
        more debt to make the debt-bot more exciting',
    ]
    for t in tests:
        print(Transaction(t).obligation_to_user('U024H5LFB'))


if __name__ == '__main__':
    test()

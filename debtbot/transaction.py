# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals
import re
from collections import namedtuple

DEBUG = False

# these are operator types. This is annoying. I'd love an enum
FROM_KEY = "from"
TO_KEY = "to"


class TransactionParseError(Exception):
    pass


class Transaction(object):

    """A transaction represents a debt relationship between two parties"""
    debtor = None
    creditor = None
    value = None

    raw_text = None
    raw_transaction = None

    @property
    def parsed(self):
        return all([self.debtor, self.creditor, self.value])

    def __init__(self, input_str):
        super(Transaction, self).__init__()
        if input_str:
            self.raw_text = input_str
            self.parse(self.raw_text)

    def __repr__(self):
        msg = "debtor: {} creditor: {} value: {}".format(
            self.debtor or '',
            self.creditor or '',
            self.value or '')

        if not self.parsed:
            msg = 'FAILED TO PARSE: {}\n found {}'.format(
                self.raw_text, msg)
        return msg

    def obligation_to_user(self, user):
        if user == self.debtor:
            return self.value, self.creditor
        if user == self.creditor:
            return 0 - self.value, self.debtor
        return 0, None

    def _matches(self, text):
        '''split for testing'''
        return re.search(
            r'(?:<?@([0-9A-Za-z]+)>?.?\s*)([-<>]+)?(?:\s*<?@([0-9A-Za-z]+)>?)?(?:[^0-9\.]+)?([0-9\.]+)?',
            text)

    def parse(self, text):
        parsed = self._matches(text)

        if not parsed:
            return
        a, b, c, d = parsed.groups()

        # if we parse nothing, assume it's chat.
        parse_count = sum(x is not None for x in (a, b, c, d))
        if parse_count == 0:
            return None
        elif parse_count < 4:
            # if we parse something but not everything, toss exception
            raise TransactionParseError(
                'incomplete parse of {}, found {} '.format(
                    text, str(parsed.groups())))

        # figure out the operator:
        self.operator = self.parse_operator(b)
        if not self.operator:
            raise TransactionParseError(
                'Illegal operator ({}) in text {}'.format(
                    b, text))

        self.debtor = c if self.operator == TO_KEY else a
        self.creditor = a if self.operator == TO_KEY else c
        try:
            self.value = float(d)
        except ValueError:
            raise TransactionParseError(
                'failed to parse value ({}) in text: {}'.format(
                    d, text))

    def parse_operator(self, operator_text):
        credit = ">" in operator_text
        debit = "<" in operator_text

        if credit == debit:
            return None

        return TO_KEY if credit else FROM_KEY


def test():
    tests = [
        '<@U024H4SR1> -> <@U024H5LFB> $15 (thai food)',
        '<@U024H5KK7> -> <@U024H5LFB> 20$',
        '<@U024H5KK7> -> <@U024H5LFB> $10 sandwich place',
        '<@U024H5KK7> -< <@U024H5LFB> $10 sandwich place',
        '<@U024H4SR1> -> <@U024H5LFB> $7',
        '<@U024H4SR1> -> 56 money!',
        '<@U024H4SR1|will> set the channel topic: trying to incur \
        more debt to make the debt-bot more exciting',
    ]
    T = Transaction('<@U024H4SR1> -> <@U024H5LFB> $15 (thai food)')
    for t in tests:
        try:
            matches = T._matches(t)
            if matches:
                print(matches.groups())

            transaction = Transaction(t)
            print(transaction)
            print(transaction.obligation_to_user('U024H5LFB'))
        except TransactionParseError as err:
            print(err)


if __name__ == '__main__':
    test()

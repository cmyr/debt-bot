# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals
import re
from collections import namedtuple

DEBUG = False

# these are operator types. This is annoying. I'd love an enum
FROM_KEY = "from"
TO_KEY = "to"

# RawTransaction = namedtuple(
#     "Transaction",
#     ["first_party", "operator", "second_party", "value", "notes"])


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
        self.raw_text = input_str
        self.parse(self.raw_text)
        # raw_transaction = self.parse(self.input_str)
        # self.raw_transaction = self.componentize_transaction(
        #     input_str,
        #     [self.componentize1, self.componentize2]
        # )
        # self.parse_components(self.raw_transaction)

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
        if user == self.creditor:
            return self.value, self.debtor
        if user == self.debtor:
            return 0 - self.value, self.creditor
        return 0, None

    # def componentize_transaction(self, text, funcs):
    #     subbed = re.sub(r'<@(\w+)>', r'@\1 ', text)
    #     if DEBUG:
    #         print(text)
    #         print(subbed)
    #     for f in funcs:
    #         result = f(subbed)
    #         if result:
    #             return result

    def _matches(self, text):
        '''split for testing'''
        return re.search(
            r'(?:<@([0-9A-Z]+)>.?\s*)(\S*)?(?:\s*<@([0-9A-Z]+)>)?(?:[^0-9\.]+)?([0-9\.]+)?',
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

        self.debtor = a if self.operator == TO_KEY else c
        self.creditor = c if self.operator == TO_KEY else a
        try:
            self.value = float(d)
        except ValueError:
            raise TransactionParseError(
                'failed to parse value ({}) in text: {}'.format(
                    d, text))

    # def componentize1(self, text):
    #     parsed = re.search(
    #         r'<@(\w+)>.?\s*(\S*)\s*<@(\w+)>\s+([^0-9\.]+)?([0-9\.]+)\$?(.*)',
    #         text)
    #     if parsed:
    #         return RawTransaction(
    #             parsed.group(1), parsed.group(2), parsed.group(3),
    #             parsed.group(4), parsed.group(5))

    # def componentize2(self, text):
    #     parsed = re.search(r'@(\w+).?\s*(\S*)\s*(\w+)\s(.*?)([0-9\.]+)', text)
    #     if parsed:
    #         return RawTransaction(
    #             parsed.group(1), parsed.group(2), parsed.group(3),
    #             parsed.group(5), parsed.group(4))

    # def parse_components(self, raw_transaction):
    #     if raw_transaction:
    #         if DEBUG:
    #             print(raw_transaction)
    #         operator = self.parse_operator(raw_transaction.operator)
    #         if operator == TO_KEY:
    #             self.debtor = raw_transaction.first_party
    #             self.creditor = raw_transaction.second_party
    #         elif operator == FROM_KEY:
    #             self.debtor = raw_transaction.second_party
    #             self.creditor = raw_transaction.first_party

    #         self.operator = raw_transaction.operator
    #         self.value = float(raw_transaction.value)
    #         if raw_transaction.notes != "":
    #             self.notes = raw_transaction.notes

    def parse_operator(self, operator_text):
        credit = "&gt;" in operator_text
        debit = "&lt;" in operator_text

        if credit == debit:
            return None

        return TO_KEY if credit else FROM_KEY


def test():
    tests = [
        '<@U024H4SR1> -&gt; <@U024H5LFB> $15 (thai food)',
        '<@U024H5KK7> -&gt; <@U024H5LFB> 20$',
        '<@U024H5KK7> -&gt; <@U024H5LFB> $10 sandwich place',
        '<@U024H5KK7> -&lt; <@U024H5LFB> $10 sandwich place',
        '<@U024H4SR1> -&gt; <@U024H5LFB> $7',
        '<@U024H4SR1> -&gt; 56 money!',
        '<@U024H4SR1|will> set the channel topic: trying to incur \
        more debt to make the debt-bot more exciting',
    ]
    T = Transaction('<@U024H4SR1> -&gt; <@U024H5LFB> $15 (thai food)')
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

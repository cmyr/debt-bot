# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals
import re
from collections import namedtuple

DEBUG = False

# these are operator types. This is annoying. I'd love an enum
FROM_KEY = "from"
TO_KEY = "to"

RawTransaction = namedtuple("Transaction", ["first_party", "operator", "second_party", "value", "notes"])

class Transaction(object):
    """A transaction represents a debt relationship between two parties"""
    debtor = None
    creditor = None
    value = None
    currency = None
    notes = None

    raw_text = None
    raw_transaction = None

    def __init__(self, input_str):
        super(Transaction, self).__init__()
        raw_text = input_str
        raw_transaction = self.componentize_transaction(
            input_str, 
            [self.componentize1, self.componentize2]
            )
        self.parse_components(raw_transaction)

    def __repr__(self):
        return "%s %s %s %s %s" % (
            self.debtor, self.creditor, self.value,
            self.currency, self.notes)

    def componentize_transaction(self, text, funcs):
        if DEBUG:
            print(text)
        for f in funcs:
            result = f(text)
            if result:
                return result

    def componentize1(self, text):
        parsed = re.search(r'<?@(\w+)>?\s*(\S*)\s*<?@(\w+)>?\s?\$?([0-9\.]+)\$?(.*)', text)
        if parsed:
            return RawTransaction(parsed.group(1), parsed.group(2), parsed.group(3),
             parsed.group(4), parsed.group(5))

    def componentize2(self, text):
        parsed = re.search(r'<?@(\w+)>?\s*(\S*)\s*<?@(\w+)>?\s(.*?)([0-9\.]+)', text)
        if parsed:
            return RawTransaction(parsed.group(1), parsed.group(2), parsed.group(3),
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
                self.creditor = RawTransaction.first_party

            self.operator = raw_transaction.operator
            self.value = raw_transaction.value
            self.notes = raw_transaction.notes


    def parse_operator(self, operator_text):
        if operator_text == "-&gt;":
            return TO_KEY
        if operator_text == "-&lt;":
            return FROM_KEY

def test():
 test_string = '<@U024H4SR1> -&gt; <@U024H5LFB> $15 (thai food)'
 print(Transaction(test_string))


if __name__ == '__main__':
    test()
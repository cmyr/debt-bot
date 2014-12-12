# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals
import re

# these are operator types. This is annoying. I'd love an enum
FROM_KEY = "from"
TO_KEY = "to"

class Transaction(object):
    """A transaction represents a debt relationship between two parties"""
    debtor = ""
    creditor = ""
    value = None
    currency = "$"
    notes = ""

    _first_party = None
    _second_party = None
    _operator = None
    _value = None
    _notes = None

    def __init__(self, input_str):
        super(Transaction, self).__init__()
        self.parse_transaction(input_str)

    def __repr__(self):
        return "%s %s %s %s %s" % (
            self._first_party, self._second_party, self._operator,
            self._value, self._notes)

    def parse_transaction(self, text):
        parsed = re.search(r'<?@(\w+)>?\s*(\S*)\s*<?@(\w+)>?\s.?\$?([0-9\.]+)\$?(.*)', text)
        if parsed:
            self._first_party = parsed.group(1)
            self._second_party = parsed.group(3)
            self._operator = parsed.group(2)
            self._value = parsed.group(4)
            self._notes = parsed.group(5)
            return

        parsed = re.search(r'<?@(\w+)>?\s*(\S*)\s*<?@(\w+)>?\s(.*?)([0-9\.]+)', text)
        if parsed:
            self._first_party = parsed.group(1)
            self._second_party = parsed.group(3)
            self._operator = parsed.group(2)
            self._value = parsed.group(4)
            self._notes = parsed.group(5)
            return

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
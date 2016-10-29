# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from transaction import *
from collections import namedtuple
import re

TestExpectation = namedtuple(
    "TransactionTestResult",
    ["debtor", "creditor", "value", "currency", "notes"])


def run_test(item, expectation):
    result = Transaction(item)

    assert result.debtor == expectation.debtor, "incorrect debtor"
    assert result.creditor == expectation.creditor, "incorrect creditor"
    assert result.value == expectation.value, "incorrect value"
    assert result.currency == expectation.currency, "incorrect currency"
    assert result.notes == expectation.notes, "incorrect notes"

# :minuum: -&gt; <@U024H5LFB> dinner
test_cases = [
    ('<@U024H4SR1> -&gt; <@U024H5LFB> $15 (thai food)',
        TestExpectation('U024H4SR1', 'U024H5LFB', 15, None, ' (thai food)')),
    ('<@U024H5KK7> -&gt; <@U024H5LFB> 20$',
        TestExpectation('U024H5KK7', 'U024H5LFB', 20, None, None)),
    ('<@U024H4SR1> -&gt; <@U024H5LFB> $7',
        TestExpectation('U024H4SR1', 'U024H5LFB', 7, None, None)),
    ('<@U02BMUNJ7> -&gt; <@U024H4SR1> 8ish pho',
        TestExpectation('U02BMUNJ7', 'U024H4SR1', 8, None, 'ish pho')),
    ('<@U02BMUNJ7>  -&gt; <@U02G8SVCB> $15',
        TestExpectation('U02BMUNJ7', 'U02G8SVCB', 15, None, None)),
    ('<@U02BMUNJ7> -&gt; <@U024H5LFB> white wine : 9.75',
        TestExpectation('U02BMUNJ7', 'U024H5LFB', 9.75, None, ' : white wine : '))
    ]

#   r'@([0-9A-Z]+).?\s*([ -><]+)\s*@([0-9A-Z]+):?\s+\$?([0-9\.]+)\$?(.*)', text)

def main():
    for item, expectation in test_cases:
        found = re.search(
            r'<@(\w+)>.?\s*(\S*)\s*<@(\w+)>(?:[^0-9\.]+)?([0-9\.]+)', item)
        # r'<@(\w+)>.?\s*(\S*)\s*<@(\w+)>\s+([^0-9\.]+)?([0-9\.]+)', item)
            # r'@(\w+).?\s*(\S*)\s*(\w+)\s(.*?)([0-9\.]+)', item)
        if found:
            print(found.groups())
        else:
            print('nothing found for item: \n %s' % item)
    #     try:
    #         run_test(item, expectation)
    #     except AssertionError as err:
    #         print(err, item, Transaction(item))
    #         raise

    # print("%d tests passed" % len(test_cases))

if __name__ == "__main__":
    main()
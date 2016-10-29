# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import debtbot.transaction
from debtbot import transaction


def test_symbol_clash():
    inp = '<@U024H4SR1> -&gt;&lt; <@U024H5LFB> $15 (thai food)'
    try:
        t = transaction.Transaction(inp)
        assert False
    except transaction.TransactionParseError:
        assert True


def test_transaction_1():
    inp = '<@U024H4SR1> -&gt; <@U024H5LFB> $15 (thai food)'
    t = transaction.Transaction(inp)
    assert t.debtor == 'U024H5LFB'
    assert t.creditor == 'U024H4SR1'
    assert t.value == 15


def test_transaction_2():
    inp = '<@U024H4SR1> -&lt; <@U024H5LFB> $15 (thai food)'
    t = transaction.Transaction(inp)
    assert t.parsed
    assert t.debtor == 'U024H4SR1'


def test_transaction_fail_1():
    inp = '<@U024H4SR1> -&gt; 56 money!'
    try:
        t = transaction.Transaction(inp)
        assert False
    except transaction.TransactionParseError:
        assert True


def test_value():
    inp = '<@U024H5KK7> -&lt; <@U024H5LFB> $10 sandwich place'
    t = transaction.Transaction(inp)
    assert t.value == 10


def test_value_2():
    inp = '<@U024H5KK7> -&lt; <@U024H5LFB> 10.5$ sandwich place'
    t = transaction.Transaction(inp)
    assert t.value == 10.5


def test_value_3():
    inp = '<@U024H5KK7> -&lt; <@U024H5LFB> sandwich place $10.5$ yow'
    t = transaction.Transaction(inp)
    assert t.value == 10.5

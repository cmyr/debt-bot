# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import debtbot.transaction
from debtbot import transaction


def test_symbol_clash():
    inp = '<@U024H4SR1> ->< <@U024H5LFB> $15 (thai food)'
    try:
        t = transaction.Transaction(inp)
        assert False
    except transaction.TransactionParseError:
        assert True


def test_parse_operator():
    for inp in [
            '@colin -> @other 5',
            '@colin --> @other 5',
            '@colin <- @other 5',
            '@colin < @other 5',
            '@colin > @other 5'
            ]:
        t = transaction.Transaction(inp)
        assert t.value == 5, inp


def test_handle_colon():
    inp = '<@U024H4SR1>: -> <@U024H5LFB> $15 (thai food)'
    t = transaction.Transaction(inp)
    assert t.creditor == "U024H4SR1"

    inp = '@colin: -> <@U024H5LFB> $15 (thai food)'
    t = transaction.Transaction(inp)
    assert t.creditor == 'colin'


def test_transaction_1():
    inp = '<@U024H4SR1> -> <@U024H5LFB> $15 (thai food)'
    t = transaction.Transaction(inp)
    assert t.debtor == 'U024H5LFB'
    assert t.creditor == 'U024H4SR1'
    assert t.value == 15


def test_transaction_2():
    inp = '<@U024H4SR1> <- <@U024H5LFB> $15 (thai food)'
    t = transaction.Transaction(inp)
    assert t.parsed
    assert t.debtor == 'U024H4SR1'


def test_transaction_fail_1():
    inp = '<@U024H4SR1> -> 56 money!'
    try:
        t = transaction.Transaction(inp)
        assert False
    except transaction.TransactionParseError:
        assert True


def test_value():
    inp = '<@U024H5KK7> <- <@U024H5LFB> $10 sandwich place'
    t = transaction.Transaction(inp)
    assert t.value == 10


def test_value_2():
    inp = '<@U024H5KK7> <- <@U024H5LFB> 10.5$ sandwich place'
    t = transaction.Transaction(inp)
    assert t.value == 10.5


def test_value_3():
    inp = '<@U024H5KK7> <- <@U024H5LFB> sandwich place $10.5$ yow'
    t = transaction.Transaction(inp)
    assert t.value == 10.5


def test_names():
    inp = '@will -> @colin 35'
    t = transaction.Transaction(inp)
    assert t.debtor == 'colin'
    assert t.creditor == 'will'
    assert t.value == 35



# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from debtbot import slask, debt_utils


def test_status():
    msg = {'text': 'status', 'user_id': 'U024H4SR1'}
    result = slask.handle_message(msg)
    assert "status for" in result


def test_transactions():
    msg = {'text': 'transactions', 'user_id': 'U024H4SR1'}
    result = slask.handle_message(msg)
    assert len(result.splitlines()) > 10, 'this test is very fuzzy'


def test_errors():
    msg = {'text': 'debug', 'user_id': 'U024H4SR1'}
    result = slask.handle_message(msg)
    assert result is not None


def test_calculation():
    transactions = [
        '@colin -> @will 20',
        '@will -> @colin 15',
        '@colin -> @sparky 5',
        '@colin <- @stew 2.5 '
    ]

    balances, errors = debt_utils.sum_obligations(transactions, 'colin')
    assert len(errors) == 0
    assert balances['will'] == -5
    assert balances['sparky'] == -5
    assert balances['stew'] == 2.5


def test_validate_input():
    message = {'channel_id': debt_utils.DEBT_CHANNEL_ID, 'text': '@colin -> @joe $4.20'}
    result = slask.handle_message(message)
    assert not result


def test_validate_input_fail():
    message = {'channel_id': debt_utils.DEBT_CHANNEL_ID, 'text': '@colin <-> @joe $4.20'}
    result = slask.handle_message(message)
    assert "error" in result

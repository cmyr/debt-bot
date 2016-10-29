# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from debtbot import slask


def test_status():
    msg = {'text': 'status', 'user_id': 'U024H4SR1'}
    result = slask.handle_message(msg)
    assert "status for" in result

# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


class Transaction(object):
    """A transaction represents a debt relationship between two parties"""
    debtor = ""
    creditor = ""
    value = None
    currency = "$"
    notes ""

    def __init__(self, input_str):
        super(Transaction, self).__init__()

        
####################################################################################################
#
# pyFinancialSimulator - A Financial Simulator
# Copyright (C) 2015 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

import logging

####################################################################################################

from ..Journal import DebitMixin, CreditMixin

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Transaction(object):

    ##############################################

    def __init__(self, date, description, amount, type_):

        self._date = date
        self._description = description
        self._amount = amount
        self._type = type_

    ##############################################

    @property
    def date(self):
        return self._date

    @property
    def description(self):
        return self._description

    @property
    def amount(self):
        return self._amount

    @property
    def type(self):
        return self._type

    ##############################################

    def __str__(self):

        return '{0._date} | {0._type} | {0._amount} € | {0._description}'.format(self)

####################################################################################################

class DebitTransaction(DebitMixin, Transaction):
    pass

class CreditTransaction(CreditMixin, Transaction):
    pass

####################################################################################################

class BankStatement(object):

    ##############################################

    def __init__(self, bank_account_number, date,
                 balance,
                 previous_balance=None):
        # transactions=None):

        self._bank_account_number = bank_account_number
        self._date = date
        self._previous_balance = previous_balance
        self._balance = balance
        self._transactions_balance = 0
        
        self._transactions = []
        # if transactions is not None:
        #     for transaction in transactions:
        #         self.add_transaction(transaction)

    ##############################################

    @property
    def bank_account_number(self):
        return self._bank_account_number

    @property
    def date(self):
        return self._date

    @property
    def previous_balance(self):
        return self._previous_balance

    @property
    def balance(self):
        return self._balance

    @property
    def transactions_balance(self):
        return self._transactions_balance

    ##############################################

    def __iter__(self):

        return iter(self._transactions)

    ##############################################

    def add_transaction(self, date, description, amount, type_):

        if amount < 0:
            transaction_class = DebitTransaction
        else:
            transaction_class = CreditTransaction
        transaction = transaction_class(date, description, abs(amount), type_)
        
        self._transactions.append(transaction)
        if transaction.is_debit():
            self._transactions_balance -= transaction.amount
        else:
            self._transactions_balance += transaction.amount

    ##############################################

    def check(self):

        if self._previous_balance is not None:
            return self._balance - self._previous_balance == self._transactions_balance
        else:
            return None

####################################################################################################
#
# End
#
####################################################################################################

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

import datetime
import logging
from collections import OrderedDict

####################################################################################################

from ..Journal import DebitMixin, CreditMixin

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Transaction(object):

    # Fixme: check duplicated code in Journal

    ##############################################

    def __init__(self, sequence_number, date, description, amount, type_):

        self._sequence_number = sequence_number
        self._date = date
        self._description = description
        self._amount = amount
        self._type = type_

        self._reconciliation_id = None # clearing
        self._reconciliation_date = None

    ##############################################

    @property
    def sequence_number(self):
        return self._sequence_number

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

    @property
    def reconciliation_id(self):
        return self._reconciliation_id

    ##############################################

    @property
    def reconciliation_date(self):
        return self._reconciliation_date

    ##############################################

    def __str__(self):

        return '{0._date} | {0._type} | {0._amount} € | {0._description}'.format(self)

    ##############################################

    def reconcile(self, reconciliation_id):

        if self._reconciliation_date is not None:
            self._reconciliation_id = reconciliation_id
            self._reconciliation_date = datetime.datetime.utcnow()
        else:
            raise NameError('Journal entry is already cleared')

    ##############################################

    def cleared(self):
        
        return self._reconciliation_id is not None

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

        self._bank_account_number = bank_account_number
        self._date = date
        self._previous_balance = previous_balance
        self._balance = balance
        
        self._transactions_balance = 0
        self._debit_transactions = []
        self._credit_transactions = []
        self._transactions = []

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

    @property
    def debits(self):
        return iter(self._debit_transactions)

    @property
    def credits(self):
        return iter(self._credit_transactions)

    ##############################################

    def __len__(self):

        return len(self._transactions)

    ##############################################

    def __getitem__(self, slice_):

        return self._transactions[slice_]

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
            self._debit_transactions.append(transaction)
        else:
            self._transactions_balance += transaction.amount
            self._credit_transactions.append(transaction)

    ##############################################

    def check(self):

        if self._previous_balance is not None:
            return self._balance - self._previous_balance == self._transactions_balance
        else:
            return None

####################################################################################################

class AmountList(object):

    ##############################################

    def __init__(self, transaction):

        self._amount = transaction.amount
        self._transactions = [transaction]

    ##############################################

    @property
    def amount(self):
        return self._amount

    ##############################################

    def __iter__(self):
        return iter(self._transactions)

    ##############################################

    def append(self, transaction):

        if transaction.amount == self._amount:
            self._transactions.append(transaction)
        else:
            raise ValueError

    ##############################################

    def sort(self):
        self._transactions.sort(key=lambda x: x.date)

####################################################################################################

def _sort_amount_dict(amount_dict):
    amount_lists = list(amount_dict.values())
    for amount_list in amount_lists:
        amount_list.sort()
    amount_lists.sort(key=lambda x: x.amount) # Fixme: simpler
    return OrderedDict([(amount_list.amount, amount_list) for amount_list in amount_lists])

####################################################################################################

class Reconciliator(object):

    ##############################################

    def __init__(self, bank_statement):

        self._bank_statement = bank_statement

        (self._debit_amounts,
         self._credit_amounts) = self._make_amount_dict(self._bank_statement)

    ##############################################

    def _make_amount_dict(self, transactions):

        debit_amounts = {}
        credit_amounts = {}
        for transaction in transactions:
            if transaction.is_debit():
                d = debit_amounts
            else:
                d = credit_amounts
            amount = transaction.amount
            if amount in d:
                d[amount].append(transaction)
            else:
                d[amount] = AmountList(transaction)
        debit_amounts = _sort_amount_dict(debit_amounts)
        credit_amounts = _sort_amount_dict(credit_amounts)

        return debit_amounts, credit_amounts

    ##############################################

    def reconcille(self, transactions):

        # a bank transaction should match one or several imputations
        # dates should be close to each other

        # try to match exact amount with close date
        # try to merge imputations to match a transaction amount

        bank_debit_amounts, bank_credit_amounts = self._debit_amounts, self._credit_amounts
        my_debit_amounts, my_credit_amounts = self._make_amount_dict(transactions)

        self._reconcile_exact_amount(bank_debit_amounts, my_debit_amounts)
        self._reconcile_exact_amount(bank_credit_amounts, my_credit_amounts)

    ##############################################

    def _reconcile_exact_amount(self, bank_amounts, my_amounts):

        for amount, amount_list in bank_amounts.items():
            if amount in my_amounts:
                for bank_transaction in amount_list:
                    for my_transaction in my_amounts[amount]:
                        print (bank_transaction.date - my_transaction.date)
                        # ...

####################################################################################################
#
# End
#
####################################################################################################

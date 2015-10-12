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

from FinancialSimulator.Units import round_currency

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Imputation(object):

    __letter__ = ''

    ##############################################

    def __init__(self, transaction, account, amount):

        self._transaction = transaction
        self._account = account
        self._amount = amount

    ##############################################

    @property
    def description(self):
        return self._transaction.description

    @property
    def account(self):
        return self._account

    @property
    def amount(self):
        return self._amount

    ##############################################

    def run(self):

        self._account.run_imputation(self)

    ##############################################

    def __str__(self):

        return '{} {}: {} {}'.format(self.__letter__, self._account.code,
                                     self._amount, self._account.devise)

####################################################################################################

class DebitImputation(Imputation):
    __letter__ = 'D'

####################################################################################################

class CreditImputation(Imputation):
    __letter__ = 'C'

####################################################################################################

class UnplannedTransaction(object):

    ##############################################

    def __init__(self, debit_pairs, credit_pairs, description):

        self._description = description
        
        # Fixme: keep debit/credit ?
        self._debit = {account.code:DebitImputation(self, account, float(amount))
                       for account, amount in debit_pairs}
        self._credit = {account.code:CreditImputation(self, account, float(amount))
                       for account, amount in credit_pairs}
        self._imputations = dict(self._debit)
        self._imputations.update(self._credit)
        
        sum_of_debits = self.sum_of_debits()
        sum_of_credits = self.sum_of_credits()
        if sum_of_debits != sum_of_credits:
            message = "Transaction '{}' is not balanced D{} C{}"
            raise NameError(message.format(self._description,
                                           sum_of_debits,
                                           sum_of_credits))

    ##############################################

    @property
    def description(self):
        return self._description

    ##############################################

    def _sum_of_imputations(self, imputations):
        return round_currency(sum([imputation.amount for imputation in imputations.values()]))

    ##############################################

    def sum_of_debits(self):
        return self._sum_of_imputations(self._debit)

    ##############################################

    def sum_of_credits(self):
        return self._sum_of_imputations(self._credit)

    ##############################################

    def __iter__(self):

        return iter(self._imputations.values())

    ##############################################

    def __getitem__(self, account):

        return self._imputations[account.code]

    ##############################################

    def run(self):

        for imputation in self._imputations.values():
            imputation.run()

    # ##############################################

    def plan(self, date):

        obj = Transaction.__new__(Transaction)
        obj.__dict__.update(self.__dict__)
        obj._date = date
        
        return obj

####################################################################################################

class Transaction(UnplannedTransaction):

    ##############################################

    def __init__(self, date, debit_pairs, credit_pairs, description):

        super(Transaction, self).__init__(debit_pairs, credit_pairs, description)

        self._date = date

    ##############################################

    @property
    def date(self):
        return self._date

    ##############################################

    def __str__(self):

        message = 'Transaction on {}: {}\n'.format(self._date, self._description)
        for imputations in self._debit, self._credit:
            message += '\n'.join([str(imputation) for imputation in imputations.values()])
            message += '\n'
        return message

####################################################################################################

class Account(object):

    _logger = _module_logger.getChild('Account')

    ##############################################

    def __init__(self, code, name, parent=None, initial_balance=0, devise='€'):

        self._name = name
        self._code = code
        
        self._parent = parent
        self._siblings = set()
        if parent is not None:
            parent.add_child(self)
        
        self._initial_balance = initial_balance
        self._devise = devise
        
        self.reset()

    ##############################################

    def reset(self):

        self._inner_credit = 0
        self._inner_debit = 0
        self._inner_balance = None
        
        self._credit = None
        self._debit = None
        self._balance = None

    ##############################################

    @property
    def name(self):
        return self._name

    ##############################################

    @property
    def code(self):
        return self._code

    ##############################################

    @property
    def devise(self):
        return self._devise

    ##############################################

    def __str__(self):
        return '#' + self._code

    ##############################################

    def __repr__(self):
        return str(self)

    ##############################################

    def add_child(self, child):

        self.balance_is_dirty()
        self._siblings.add(child)

    ##############################################

    @property
    def parent(self):
        return self._parent

    ##############################################

    @property
    def siblings(self):
        return self._siblings

    ##############################################

    def balance_is_dirty(self):
        self._balance = None

    ##############################################

    def inner_balance_is_dirty(self):

        self._inner_balance = None
        self._balance = None

    ##############################################

    def _parent_is_dirty(self):

        if self._parent is not None:
            self._parent.balance_is_dirty()

    ##############################################

    def _compute_balance(self):

        if self._inner_balance is None:
            self._inner_balance = self._inner_credit - self._inner_debit
        
        if self._balance is None:
            self._credit = self._inner_credit
            self._debit = self._inner_debit
            for child in self._siblings:
                self._credit += child.credit
                self._debit += child.debit
            self._balance = self._credit - self._debit

    ##############################################

    @property
    def balance(self):

        if self._balance is None:
            self._compute_balance()
        return self._balance

    ##############################################

    @property
    def credit(self):

        # Fxime: solde créditeur
        if self._balance is None:
            self._compute_balance()
        return self._credit

    ##############################################

    @property
    def debit(self):

        if self._balance is None:
            self._compute_balance()
        return self._debit

    ##############################################

    def run_imputation(self, imputation):

        # Fixme:
        # imputation: (account, type, amount) -> update
        # -> debit/credit function
        # move code to imputation ?

        if imputation.account is not self:
            raise NameError("Account mismatch")
        
        self.inner_balance_is_dirty()
        if isinstance(imputation, DebitImputation):
            operation = 'Debit'
            self._inner_debit += imputation.amount
        else:
            operation = 'Credit'
            self._inner_credit += imputation.amount
        message = '{} on {}: {} {} ({})'.format(operation,
                                                self._code,
                                                imputation.amount,
                                                self._devise,
                                                imputation.description,
        )
        self._logger.info(message)

####################################################################################################

class AccountChart(object):

    ##############################################

    def __init__(self, name):

        self._name = name
        self._accounts = {}
        self._flat_hierarchy = None

    ##############################################

    @property
    def name(self):

        return self._name

    ##############################################

    def add_account(self, account):

        self._accounts[account.code] = account

    ##############################################

    def __getitem__(self, code):

        return self._accounts[code]

    ##############################################

    def __iter__(self):

        if self._flat_hierarchy is None:
            self._build_hierarchy()
        return iter(self._flat_hierarchy)

    ##############################################

    def _build_sibling_hierarchy(self, account):

        siblings = list(account.siblings)
        siblings.sort(key=lambda x: x.code)
        for sibling in siblings:
            yield sibling
            yield from self._build_sibling_hierarchy(sibling)

    ##############################################

    def _build_hierarchy(self):

        root_accounts = []
        for account in self._accounts.values():
            if account.parent is None:
                root_accounts.append(account)
        root_accounts.sort(key=lambda x: x.code)
        
        flat_hierarchy = []
        for account in root_accounts:
            flat_hierarchy.append(account)
            for item in self._build_sibling_hierarchy(account):
                flat_hierarchy.append(item)
        self._flat_hierarchy = flat_hierarchy

    ##############################################

    def reset(self):

        for account in self._flat_hierarchy:
            account.reset()

####################################################################################################

class Journal(object):

    ##############################################

    def __init__(self, name, account_chart):

        self._name = name
        self._account_chart = account_chart
        self._transactions = []

    ##############################################

    @property
    def name(self):

        return self._name

    ##############################################

    def run(self):

        self._account_chart.reset()
        for transaction in self._transactions:
            transaction.run()

    ##############################################

    def log_transaction_object(self, transaction):

        self._transactions.append(transaction)
        transaction.run()

    ##############################################

    def _make_imputation_pairs(self, imputations):

        return [(self._account_chart[account_code], amount)
                for account_code, amount in imputations.items()]

    ##############################################

    def log_transaction(self, date, debit, credit, description):

        # Fixme:
        #  DebitImputation(account, amount)
        #  DebitImputation(account_code, amount)

        transaction = Transaction(date,
                                  self._make_imputation_pairs(debit),
                                  self._make_imputation_pairs(credit),
                                  description)
        self.log_transaction_object(transaction)

####################################################################################################
#
# End
#
####################################################################################################

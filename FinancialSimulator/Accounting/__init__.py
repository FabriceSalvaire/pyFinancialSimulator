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

class Transaction(object):

    ##############################################

    def __init__(self, source, description=''):

        self._source = source
        self._description = description

    ##############################################

    @property
    def source(self):
        return self._source

    ##############################################

    @property
    def description(self):
        return self._description

####################################################################################################

class SimpleTransaction(Transaction):

    ##############################################

    def __init__(self, source, destination, amount, description=''):

        super(SimpleTransaction, self).__init__(source, description)
        self._destination = destination
        self._amount = amount

    ##############################################

    @property
    def destination(self):
        return self._destination

    ##############################################

    @property
    def amount(self):
        return self._amount

    ##############################################

    def is_debit_for(self, account):
        return self._source is account

    ##############################################

    def is_credit_for(self, account):
        return self._destination is account

####################################################################################################

class TransactionDistribution(object):

    ##############################################

    def __init__(self, destination, amount):

        self._destination = destination
        self._amount = amount

    ##############################################

    @property
    def destination(self):
        return self._destination

    ##############################################

    @property
    def amount(self):
        return self._amount

####################################################################################################

class DistributedTransaction(Transaction):

    ##############################################

    def __init__(self, source, description='', *args):

        super(DistributedTransaction, self).__init__(source, description)
        self._distribution = args

    ##############################################

    def __iter__(self):

        for item in self._distribution:
            yield SimpleTransaction(self._source, item.destination, item.amount, self._description)

    ##############################################

    @property
    def amount(self):
        # Fixme: cache ?
        return sum([item.amount for item in self._distribution])

####################################################################################################

class Account(object):

    ##############################################

    def __init__(self, code, name, parent = None, initial_balance=0):

        self._name = name
        self._code = code
        
        self._parent = parent
        self._childs = set()
        parent.add_child(self)
        
        self._journal = []
        self._initial_balance = initial_balance
        
        self._inner_credit = None
        self._inner_debit = None
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

    def add_child(self, child):

        self.balance_is_dirty()
        self._childs.add(child)

    ##############################################

    @property
    def parent(self):

        return self._parent

    ##############################################

    def balance_is_dirty(self):

        self._balance = None

    ##############################################

    def inner_balance_is_dirty(self):

        self._inner_balance = None
        self.balance_is_dirty()

    ##############################################

    def _parent_is_dirty(self):

        if self._parent is not None:
            self._parent.balance_is_dirty()

    ##############################################

    def _compute_balance(self):

        if self._inner_balance is None:
            self._inner_credit = 0
            self._inner_debit = 0
            for transaction in self._journal:
                self._run_transaction(transaction)
            self._inner_balance = self._inner_credit - self._inner_debit
        
        if self._balance is None:
            self._credit = self._inner_credit
            self._debit = self._inner_debit
            for child in self._childs:
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

    def _run_simple_transaction(self, transaction):

        if transaction.is_debit_for(self):
            self._inner_debit += transaction.amount
        elif transaction.is_credit_for(self):
            self._inner_credit += transaction.amount
        else:
            raise NameError("transaction don't involve the account")

    ##############################################

    def _run_transaction(self, transaction):

        self._parent_is_dirty()
        if isinstance(transaction, DistributedTransaction):
            for item in transaction:
                self._run_simple_transaction(item)
        else:
            self._run_simple_transaction(transaction)

    ##############################################

    def log_transaction(self, transaction):

        self._journal.append(transaction)
        self._run_transaction(transaction)

    ##############################################

    def log_debit(self, destination, amount, description=''):

        transaction = SimpleTransaction(self, destination, amount, description)
        self.log_transaction(transaction)
        destination.log_transaction(transaction)

    ##############################################

    def log_credit(self, source, amount, description=''):

        transaction = SimpleTransaction(source, self, amount, description)
        self.log_transaction(transaction)
        source.log_transaction(transaction)

####################################################################################################

class Journal(object):

    ##############################################

    def __init__(self, name):

        self._name = name

    ##############################################

    @property
    def name(self):

        return self._name

####################################################################################################
#
# End
#
####################################################################################################

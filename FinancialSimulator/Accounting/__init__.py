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
import os

####################################################################################################

_module_logger = logging.getLogger(__name__)

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

    ##############################################

    def __str__(self):

        # Fixme: devise
        return '{} -> {} {} €'.format(self._source, self._destination, self._amount)

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

    def __init__(self, source, pairs, description=''):

        super(DistributedTransaction, self).__init__(source, description)
        # pairs = [(args[i], args[i+1]) for i in range(len(args -1))]
        self._distribution = [TransactionDistribution(destination, amount)
                              for destination, amount in pairs]

    ##############################################

    def __len__(self):

        return len(self._distribution)

    ##############################################

    def __iter__(self):

        for sub_transaction in self._distribution:
            yield SimpleTransaction(self._source, sub_transaction.destination,
                                    sub_transaction.amount, self._description)

    ##############################################

    @property
    def amount(self):
        # Fixme: cache ?
        return sum([sub_transaction.amount for sub_transaction in self._distribution])

####################################################################################################

class Account(object):

    _logger = _module_logger.getChild('Account')

    ##############################################

    def __init__(self, code, name, parent=None, initial_balance=0, devise='€'):

        self._name = name
        self._code = code
        
        self._parent = parent
        self._childs = set()
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

    def __str__(self):

        return '#' + self._code

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

    def run_transaction(self, transaction):

        if isinstance(transaction, DistributedTransaction):
            raise NameError('An account cannot run a distributed transaction')
        
        self.inner_balance_is_dirty()
        if transaction.is_debit_for(self):
            sign = '+'
            self._inner_debit += transaction.amount
        elif transaction.is_credit_for(self):
            sign = '-'
            self._inner_credit += transaction.amount
        else:
            raise NameError("transaction don't involve the account")
        message = 'Run transaction {} -> {} {}{} {}'.format(transaction.source,
                                                            transaction.destination,
                                                            sign,
                                                            transaction.amount,
                                                            self._devise
        )
        self._logger.info(message)

####################################################################################################

class AccountChart(object):

    ##############################################

    def __init__(self, name):

        self._name = name
        self._accounts = {}

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

        return iter(self._accounts.values())

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

        for account in self._account_chart:
            account.reset()
        for transaction in self._transactions:
            self._run_transaction(transaction)

    ##############################################

    def _run_transaction(self, transaction):

        source = transaction.source
        if isinstance(transaction, DistributedTransaction):
            for sub_transaction in transaction:
                source.run_transaction(sub_transaction)
                sub_transaction.destination.run_transaction(sub_transaction)
        else:
            source.run_transaction(transaction)
            transaction.destination.run_transaction(transaction)

    ##############################################

    def log_transaction_object(self, transaction):

        self._transactions.append(transaction)
        self._run_transaction(transaction)

    ##############################################

    def log_transaction(self, source, kwargs, description=''):

        pairs = [(self._account_chart[destination], amount)
                  for destination, amount in kwargs.items()]
        transaction = DistributedTransaction(self._account_chart[source], pairs,
                                             description=description)
        self.log_transaction_object(transaction)

####################################################################################################

_account_charts = {
    'FR': 'plan-comptable-français.txt',
}

def load_account_chart(country_code):

    txt_file = os.path.join(os.path.dirname(__file__), _account_charts[country_code])
    with open(txt_file) as f:
        lines = f.readlines()
        
    kwargs = {}
    i = 0
    while not lines[i].startswith('#'):
        name, value = [x.strip() for x in lines[i].split(':')]
        kwargs[name] = value
        i += 1
    account_chart = AccountChart(**kwargs)
    
    previous = None
    parent = [None]
    current_level = 1
    for line in lines[i+1:]:
        code, name = [x.strip() for x in line.split('|')]
        item_level = len(code)
        if item_level > current_level:
            parent.append(previous)
            current_level = item_level
        elif item_level < current_level:
            parent = parent[:item_level-current_level]
            current_level = item_level
        account = Account(code, name, parent=parent[-1])
        account_chart.add_account(account)
        previous = account
    
    return account_chart

####################################################################################################
#
# End
#
####################################################################################################

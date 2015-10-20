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

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Account(object):

    _logger = _module_logger.getChild('Account')

    ##############################################

    def __init__(self, number, description,
                 parent=None,
                 devise='€',
                 comment='',
                 system=''):

        self._number = number
        self._description = description
        self._comment = comment
        self._system = system # PCG Fr: classe, base, abrégé, développé
        self._devise = devise
        self._parent = parent
        #
        self._siblings = set()
        if parent is not None:
            parent.add_child(self)

    ##############################################

    @property
    def description(self):
        return self._description

    ##############################################

    @property
    def number(self):
        return self._number

    ##############################################

    @property
    def comment(self):
        return self._comment

    ##############################################

    @property
    def system(self):
        return self._system

    ##############################################

    @property
    def devise(self):
        return self._devise

    ##############################################

    @property
    def parent(self):
        return self._parent

    ##############################################

    @property
    def siblings(self):
        return self._siblings

    ##############################################

    def __str__(self):
        return '#' + self._number

    ##############################################

    def __repr__(self):
        return str(self)

    ##############################################

    def __lt__(self, other):

        number1 = str(self._number)
        number2 = str(other._number)
        return number1 < number2
        # for d1, d2 in zip(number1, number2):
        #     if d1 < d2:
        #         return True
        #     elif d1 > d2:
        #         return False

    ##############################################

    def add_child(self, child):

        # Fixme: self.balance_is_dirty()
        self._siblings.add(child)

####################################################################################################

class AccountChart(object):

    ##############################################

    def __init__(self, name):

        self._name = name
        self._accounts = {}
        self._flat_hierarchy = None
        self._root_accounts = []

    ##############################################

    @property
    def name(self):

        return self._name

    ##############################################

    def add_account(self, account):

        self._accounts[account.number] = account

    ##############################################

    def _build_sibling_hierarchy(self, account):

        siblings = list(account.siblings)
        siblings.sort(key=lambda x: x.number)
        for sibling in siblings:
            yield sibling
            yield from self._build_sibling_hierarchy(sibling)

    ##############################################

    def _build_hierarchy(self):

        # Fixme: can simplify using str sort

        root_accounts = []
        for account in self._accounts.values():
            if account.parent is None:
                root_accounts.append(account)
        root_accounts.sort(key=lambda x: x.number)
        
        flat_hierarchy = []
        for account in root_accounts:
            flat_hierarchy.append(account)
            for item in self._build_sibling_hierarchy(account):
                flat_hierarchy.append(item)
        
        self._root_accounts = root_accounts
        self._flat_hierarchy = flat_hierarchy

    ##############################################

    def __getitem__(self, number):

        return self._accounts[number]

    ##############################################

    def __iter__(self):

        if self._flat_hierarchy is None:
            self._build_hierarchy()
        return iter(self._flat_hierarchy)

    ##############################################

    def _breadth_first_search(self, node, visitor):

        visitor(node)
        for sibling in node.siblings:
            visitor(sibling)
            self._breadth_first_search(sibling)

    ##############################################

    def breadth_first_search(self, visitor):

        if self._flat_hierarchy is None:
            self._build_hierarchy()
        for root in self._root_accounts:
            self._breadth_first_search(root, visitor)

####################################################################################################

class AccountSnapshot(Account):

    _logger = _module_logger.getChild('AccountSnapshot')

    ##############################################

    def __init__(self, account, debit=0, credit=0):

        super(AccountSnapshot, self). __init__(account.number,
                                               account.description,
                                               account.devise,
                                               account.comment,
                                               account.system)
        
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

    def add_child(self, child):

        self.balance_is_dirty()
        super(AccountSnapshot, self).add_child(child)

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

        # Fixme: solde créditeur
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

    def has_imputations(self):

        return self._inner_debit or self._inner_credit

    ##############################################

    def run_imputation(self, imputation):

        # Fixme:
        # imputation: (account, type, amount) -> update
        # -> debit/credit function
        # move number to imputation ?

        if imputation.account is not self:
            raise NameError("Account mismatch")
        
        self.inner_balance_is_dirty()
        if imputation.is_debit():
            operation = 'Debit'
            self._inner_debit += imputation.amount
        else:
            operation = 'Credit'
            self._inner_credit += imputation.amount
        message = '{} on {}: {} {} ({})'.format(operation,
                                                self._number,
                                                imputation.amount,
                                                self._devise,
                                                imputation.description,
        )
        self._logger.info(message)

####################################################################################################

class AccountChartSnapshot(object):

    ##############################################

    def __init__(self, account_chart):

    ##############################################

    def reset(self):

        for account in self._flat_hierarchy:
            account.reset()

####################################################################################################
#
# End
#
####################################################################################################

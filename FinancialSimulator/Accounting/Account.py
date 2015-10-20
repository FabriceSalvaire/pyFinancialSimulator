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

from FinancialSimulator.Tools.Hierarchy import Node, Hierarchy

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Account(Node):

    _logger = _module_logger.getChild('Account')

    ##############################################

    def __init__(self, number, description,
                 parent=None,
                 devise='€',
                 comment='',
                 system=''):

        self._number = number
        super(Account, self).__init__(parent)
        self._description = description
        self._comment = comment
        self._system = system # PCG Fr: classe, base, abrégé, développé
        self._devise = devise

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

    def __hash__(self):

        # Fixme:
        return int(self._number)

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

    def __str__(self):
        return '#{}'.format(self._number)

    ##############################################

    def __repr__(self):
        return str(self)

####################################################################################################

class AccountChart(Hierarchy):

    ##############################################

    def __init__(self, name):

        super(AccountChart, self).__init__()
        
        self._name = name

    ##############################################

    @property
    def name(self):

        return self._name

####################################################################################################

class AccountSnapshot(Account):

    _logger = _module_logger.getChild('AccountSnapshot')

    ##############################################

    def __init__(self, account, parent=None):

        # , debit=0, credit=0

        super(AccountSnapshot, self). __init__(account.number,
                                               account.description,
                                               parent,
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

    def add_sibling(self, sibling):

        self.balance_is_dirty()
        super(AccountSnapshot, self).add_sibling(sibling)

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

class AccountChartSnapshot(AccountChart):

    ##############################################

    def __init__(self, account_chart):

        super(AccountChartSnapshot, self).__init__(account_chart.name)
        
        for account in account_chart:
            parent = account.parent
            if parent is not None:
                parent = self[parent.number]
            else:
                parent = None
            account_snapshot = AccountSnapshot(account, parent)
            self.add_node(account_snapshot)

    ##############################################

    def reset(self):

        for account in self:
            account.reset()

####################################################################################################
#
# End
#
####################################################################################################

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

from .AccountChart import Account, AccountChart
from .Journal import Journals

####################################################################################################

_module_logger = logging.getLogger(__name__)

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

class FinancialPeriod(object):

    ##############################################

    def __init__(self,
                 account_chart,
                 journals,
                 start_date,
                 stop_date
    ):

        self._account_chart = AccountChartSnapshot(account_chart)
        self._journals = Journals(self._account_chart, journals)
        
        self._start_date = start_date
        self._stop_date = stop_date

    ##############################################

    @property
    def account_chart(self):
        return self._account_chart

    ##############################################

    @property
    def journals(self):
        return self._journals

    ##############################################

    @property
    def start_date(self):
        return self._start_date

    ##############################################

    @property
    def stop_date(self):
        return self._stop_date

####################################################################################################
#
# End
#
####################################################################################################

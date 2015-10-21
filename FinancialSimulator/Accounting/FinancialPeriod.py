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
from .Journal import Journal
from FinancialSimulator.Tools.Currency import format_currency

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class AccountSnapshot(Account):

    # Fixme: AccountSnapshot / AccountBalance ?

    _logger = _module_logger.getChild('AccountSnapshot')

    ##############################################

    def __init__(self, account, parent=None):

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

    @property
    def debit_str(self):

        return format_currency(self.debit)

    ##############################################

    @property
    def credit_str(self):

        return format_currency(self.credit)

    ##############################################

    @property
    def balance_str(self):

        return format_currency(self.balance)

    ##############################################

    def has_imputations(self):

        return self._inner_debit or self._inner_credit

    ##############################################

    def _apply_debit_credit(self, amount):

        # Fixme: <=
        if amount < 0:
            raise ValueError("Amount must be positive")
        self.inner_balance_is_dirty()

    ##############################################

    def apply_debit(self, amount):

        self._apply_debit_credit(amount)
        self._inner_debit += amount

    ##############################################

    def apply_credit(self, amount):

        self._apply_debit_credit(amount)
        self._inner_credit += amount

    ##############################################

    def force_balance(self, debit=0, credit=0):

        if debit < 0 or credit < 0:
            raise ValueError("Amount must be positive")
        self.inner_balance_is_dirty()
        self._inner_debit = debit
        self._inner_credit = credit

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

class Journals(object):

    ##############################################

    def __init__(self, account_chart, journals):

        self._journals = {label:Journal(label, description, account_chart)
                          for label, description in journals}

    ##############################################

    def __getitem__(self, label):

        return self._journals[label]

    ##############################################

    def __iter__(self):

        return iter(self._journals.values())

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

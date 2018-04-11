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

from .FinancialPeriod import AccountBalance
from FinancialSimulator.Tools.Currency import format_currency
from FinancialSimulator.Tools.DateIndexer import DateIndexer

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class AccountBalanceSnapshot:

    ##############################################

    def __init__(self, imputation, account):

        # imputation holds account/analytic_account

        # Fixme: pass debit, credit ???
        # debit or inner_debit

        self._imputation = imputation
        self._account = account
        self._debit = account.inner_debit
        self._credit = account.inner_credit

    ##############################################

    @property
    def imputation(self):
        return self._imputation

    ##############################################

    @property
    def journal_label(self):
        return self._imputation.journal_entry.journal.label

    ##############################################

    @property
    def sequence_number(self):
        return self._imputation.journal_entry.sequence_number

    ##############################################

    @property
    def date(self):
        return self._imputation.date

    ##############################################

    @property
    def account(self):
        return self._account

    ##############################################

    @property
    def debit(self):
        return self._debit

    ##############################################

    @property
    def credit(self):
        return self._credit

    ##############################################

    @property
    def debit_str(self):
        return format_currency(self._debit)

    ##############################################

    @property
    def credit_str(self):
        return format_currency(self._credit)

    ##############################################

    @property
    def balance(self):
        return self._credit - self._debit

    ##############################################

    @property
    def balance_str(self):
        return format_currency(self.balance)

    ##############################################

    def to_json(self, with_account=True):

        d = {
            'journal': self.journal_label,
            'sequence_number': self.sequence_number,
            'debit': self._debit,
            'credit': self._credit,
            'date': str(self.date),
        }
        if with_account:
            d['account_number'] = self._account.number

        return d

####################################################################################################

class AccountBalanceHistory(DateIndexer):

    # purpose
    #  - cache balance for each imputation

    # use case:
    # simulation: run transactions and update imputed accounts, but not the hierarchy to speedup the process (laziness)
    # live: could update the hierarchy
    # history: journal for account, balance cache

    ##############################################

    def __init__(self, account):

        super(). __init__()
        self._account = account

    ##############################################

    @property
    def account(self):
        return self._account

    ##############################################

    def save(self, imputation):

        snapshot = AccountBalanceSnapshot(imputation, self._account)
        self.append(snapshot)

####################################################################################################

class AccountBalanceWithHistory(AccountBalance):

    ##############################################

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._history = None

    ##############################################

    @property
    def history(self):

        if self._history is None:
            # Lazy creation
            self._history = AccountBalanceHistory(self)
        return self._history

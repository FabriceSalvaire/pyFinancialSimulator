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
from FinancialSimulator.Tools.DateIndexer import DateIndexer
from FinancialSimulator.Tools.Observer import Observer

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class AccountBalance(Account, Observer):

    _logger = _module_logger.getChild('AccountBalance')

    ##############################################

    def __init__(self, account, parent=None):

        """ This class stores the account balance. """

        # Fixme: inheritance ?
        Account. __init__(self,
                          account.number,
                          account.description,
                          parent,
                          account.devise,
                          account.comment,
                          account.system)
        Observer.__init__(self)

        self._history = None
        self.reset()

    ##############################################

    def reset(self):

        self._inner_credit = 0
        self._inner_debit = 0
        self._inner_balance = None
        
        self._credit = None
        self._debit = None
        self._balance = None

        self.reseted()

    ##############################################

    def add_sibling(self, sibling):

        self.balance_is_dirty()
        super().add_sibling(sibling)

    ##############################################

    def balance_is_dirty(self):

        self._balance = None
        # self.changed()

    ##############################################

    def inner_balance_is_dirty(self):

        self._inner_balance = None
        self._balance = None
        self.changed()

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
        # return float()

    ##############################################

    def apply_debit(self, amount):

        self._apply_debit_credit(amount)
        self._inner_debit += amount
        # Fixme: imputation ?
        # self._history.save()

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

    ##############################################

    @property
    def history(self):

        # Fixme: place here ???
        if self._history is None:
            # Lazy creation
            self._history = AccountBalanceHistory(self)
        return self._history

    ##############################################

    def to_json(self):

        d = {
            'number': self._number,
            'inner_debit': self._inner_debit,
            'inner_credit': self._inner_credit,
        }

        return d

####################################################################################################

class AccountBalanceSnapshot:

    ##############################################

    def __init__(self, imputation, debit, credit):

        self._imputation = imputation
        self._debit = debit
        self._credit = credit

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
        }
        if with_account:
            d['account_number'] = self._imputation.account.number

        return d

####################################################################################################

class AccountBalanceHistory(DateIndexer):

    # purpose
    #  - cache balance for each imputation

    # use case:
    # simulation: run transactions and update imputed accounts, but not the hierarchy to speedup the process (laziness)
    # live: could update the hierarchy
    # history: journal for account, balance cache

    def __init__(self, account):

        super(). __init__()
        self._account = account

    ##############################################

    @property
    def account(self):
        return self._account

    ##############################################

    def save(self, imputation):

        # Fixme: pass debit, credit ???
        snapshot = AccountBalanceSnapshot(imputation, self._account.debit, self._account.credit)
        self.append(snapshot)

####################################################################################################

class AccountChartBalance(AccountChart):

    ##############################################

    def __init__(self, account_chart):

        super().__init__(account_chart.name)
        
        for account in account_chart:
            parent = account.parent
            if parent is not None:
                parent = self[parent.number]
            else:
                parent = None
            account_snapshot = AccountBalance(account, parent)
            self.add_node(account_snapshot)

    ##############################################

    def reset(self):

        for account in self:
            account.reset()

    ##############################################

    def to_json(self):

        return [account.to_json() for account in self if account.has_imputations()]

    ##############################################

    def force_balance_from_json(self, data):

        for d in data:
            account = self[d['number']]
            account.force_balance(d['inner_debit'], d['inner_credit'])

####################################################################################################

class Journals:

    ##############################################

    def __init__(self, financial_period, journals):

        self._journals = {label:Journal(label, description, financial_period)
                          for label, description in journals}

    ##############################################

    def __getitem__(self, label):

        return self._journals[label]

    ##############################################

    def __iter__(self):

        return iter(self._journals.values())

    ##############################################

    def to_json(self):

        return {journal.label: journal.to_json()
                for journal in self
                if journal}

    ##############################################

    def load_json(self, data):

        for label, journal_entries in data.items():
            journal = self[label]
            journal.load_json(journal_entries)

####################################################################################################

class FinancialPeriod:

    ##############################################

    def __init__(self,
                 account_chart,
                 analytic_account_chart,
                 journals,
                 start_date,
                 stop_date
    ):

        self._start_date = start_date
        self._stop_date = stop_date
        
        # self._history = AccountChartHistory(start_date, stop_date)
        
        self._account_chart = AccountChartBalance(account_chart)
        if analytic_account_chart is not None:
            self._analytic_account_chart = AccountChartBalance(analytic_account_chart)
        else:
            self._analytic_account_chart = None
        self._journals = Journals(self, journals)

    ##############################################

    @property
    def account_chart(self):
        return self._account_chart

    ##############################################

    @property
    def analytic_account_chart(self):
        return self._analytic_account_chart

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

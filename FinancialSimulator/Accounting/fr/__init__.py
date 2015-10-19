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

class AccountingDocument(object):

    ##############################################

    def __init__(self, number, date):

        self._number = number # Fixme: id
        self._date = date

    ##############################################

    @property
    def number(self):
        return self._number

    ##############################################

    @property
    def date(self):
        return self._date

####################################################################################################

class Imputation(object):

    __letter__ = ''

    ##############################################

    def __init__(self, _journal_entry, account, amount):

        self._journal_entry = _journal_entry
        self._account = account
        self._amount = amount

    ##############################################

    @property
    def description(self):
        return self._journal_entry.description

    @property
    def account(self):
        return self._account

    @property
    def amount(self):
        return self._amount

    @property
    def devise(self):
        return self._account.devise

    ##############################################

    def __str__(self):

        return '{} {:>10}: {:>10} {}'.format(self.__letter__, self._account.number,
                                             self._amount, self._account.devise)

    ##############################################

    def run(self):

        # Fixme: simulation vs accounting
        self._account.run_imputation(self)

####################################################################################################

class DebitImputation(Imputation):
    __letter__ = 'D'

####################################################################################################

class CreditImputation(Imputation):
    __letter__ = 'C'

####################################################################################################

class UnplannedJournalEntry(object):

    ##############################################

    def __init__(self, description, debit_pairs, credit_pairs):

        # Fixme: for simulation

        self._description = description
        
        # Fixme: keep debit/credit ?
        self._debit = {account.number:DebitImputation(self, account, float(amount))
                       for account, amount in debit_pairs}
        self._credit = {account.number:CreditImputation(self, account, float(amount))
                       for account, amount in credit_pairs}
        self._imputations = dict(self._debit)
        self._imputations.update(self._credit)
        
        sum_of_debits = self.sum_of_debits()
        sum_of_credits = self.sum_of_credits()
        if sum_of_debits != sum_of_credits:
            message = "Journal Entry '{}' is not balanced D {} != C {}"
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

        return self._imputations[account.number]

    ##############################################

    def _iter_on_imputations(self, imputations):

        imputations = list(imputations.values())
        imputations.sort(key=lambda x: x.account)
        return iter(imputations)

    ##############################################

    def iter_on_debits(self):

        # return iter(self._debit.values())
        return self._iter_on_imputations(self._debit)

    ##############################################

    def iter_on_credits(self):

        # return iter(self._credit.values())
        return self._iter_on_imputations(self._credit)

    ##############################################

    @property
    def debits(self):
        return self._debit.values()

    ##############################################

    @property
    def credits(self):
        return self._credit.values()

    ##############################################

    def run(self):

        # Fixme: simulation
        for imputation in self._imputations.values():
            imputation.run()

    # ##############################################

    def plan(self, date):

        obj = JournalEntry.__new__(JournalEntry)
        obj.__dict__.update(self.__dict__)
        obj._date = date
        
        return obj

####################################################################################################

class JournalEntry(UnplannedJournalEntry):

    ##############################################

    def __init__(self, sequence_number, date, description, document, debit_pairs, credit_pairs):

        super(JournalEntry, self).__init__(description, debit_pairs, credit_pairs, description)

        self._id = sequence_number
        self._date = date
        self._document = document # accounting document
        self._validation_date = None
        self._reconciliation_id = None # clearing
        self._reconciliation_date = None

    ##############################################

    @property
    def sequence_number(self):
        return self._id

    ##############################################

    @property
    def date(self):
        return self._date

    ##############################################

    @property
    def document(self):
        return self._document

    ##############################################

    @property
    def validation_date(self):
        return self._validation_date

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

        message = 'Journal Entry on {}: {}\n'.format(self._date, self._description)
        for imputations in self._debit, self._credit:
            message += '\n'.join([str(imputation) for imputation in imputations.values()])
            message += '\n'
        return message

####################################################################################################

class Account(object):

    _logger = _module_logger.getChild('Account')

    ##############################################

    def __init__(self, number, description,
                 parent=None,
                 devise='€',
                 comment='',
                 system='',
                 initial_balance=0):

        self._description = description
        self._number = number
        self._comment = comment
        self._system = system
        
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
        if isinstance(imputation, DebitImputation):
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

        self._accounts[account.number] = account

    ##############################################

    def __getitem__(self, number):

        return self._accounts[number]

    ##############################################

    def __iter__(self):

        if self._flat_hierarchy is None:
            self._build_hierarchy()
        return iter(self._flat_hierarchy)

    ##############################################

    def _build_sibling_hierarchy(self, account):

        siblings = list(account.siblings)
        siblings.sort(key=lambda x: x.number)
        for sibling in siblings:
            yield sibling
            yield from self._build_sibling_hierarchy(sibling)

    ##############################################

    def _build_hierarchy(self):

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
        self._flat_hierarchy = flat_hierarchy

    ##############################################

    def reset(self):

        for account in self._flat_hierarchy:
            account.reset()

####################################################################################################

class Journal(object):

    ##############################################

    def __init__(self, label, description, account_chart):

        self._label = label
        self._description = description
        self._account_chart = account_chart
        
        self._last_id = 0
        self._journal_entries = []

    ##############################################

    @property
    def label(self):
        return self._label

    ##############################################

    @property
    def description(self):
        return self._description

    ##############################################

    def __iter__(self):

        return iter(self._journal_entries)

    ##############################################

    def run(self):

        self._account_chart.reset()
        for journal_entry in self._journal_entries:
            journal_entry.run()

    ##############################################

    def log_journal_entry_object(self, journal_entry):

        self._journal_entries.append(journal_entry)
        journal_entry.run()
        self._last_id += 1

    ##############################################

    def _make_imputation_pairs(self, imputations):

        return [(self._account_chart[account_number], amount)
                for account_number, amount in imputations.items()]

    ##############################################

    def log_journal_entry(self, date, description, debit, credit, document=None):

        # Fixme:
        #  DebitImputation(account, amount)
        #  DebitImputation(account_number, amount)

        sequence_number = self._last_id
        journal_entry = JournalEntry(sequence_number,
                                     date,
                                     description,
                                     document,
                                     self._make_imputation_pairs(debit),
                                     self._make_imputation_pairs(credit)
        )
        self.log_journal_entry_object(journal_entry)

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

        return self._journals.values()

####################################################################################################

class FinancialPeriod(object):

    ##############################################

    def __init__(self,
                 account_chart,
                 journals,
                 start_date,
                 stop_date
    ):

        # Fixme: template
        self._account_chart = account_chart
        self._journals = Journals(account_chart, journals)
        
        self._start_date = start_date
        self._stop_date = stop_date

    ##############################################

    @property
    def account_chart(self):
        return self._account_chart

    ##############################################

    @property
    def jounrals(self):
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

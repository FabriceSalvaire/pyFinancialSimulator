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

import datetime
import logging

####################################################################################################

from FinancialSimulator.Units import round_currency

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Imputation(object):

    _logger = _module_logger.getChild('Imputation')

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

    def is_debit(self):
        raise NotImplementedError

    ##############################################

    def is_credit(self):
        return not self.is_debit()

    ##############################################

    def __str__(self):

        if self.is_debit():
            letter = 'D'
        else:
            letter = 'C'
        string_format = '{} {:>10}: {:>10} {}'
        return string_format.format(letter, self._account.number,
                                    self._amount, self._account.devise)

    ##############################################

    def run(self):

        # Fixme: simulation vs accounting
        # apply

        if self.is_debit():
            operation = 'Debit'
        else:
            operation = 'Credit'
        message = '{} on {}: {} {} ({})'.format(operation,
                                                self._account.number,
                                                self.amount,
                                                self._account.devise,
                                                self.description,
        )
        self._logger.info(message)
        
        self._account.run_imputation(self)

####################################################################################################

class DebitImputation(Imputation):

    ##############################################

    def is_debit(self):
        return True

####################################################################################################

class CreditImputation(Imputation):

    ##############################################

    def is_debit(self):
        return False

####################################################################################################

class UnplannedJournalEntry(object):

    ##############################################

    def __init__(self, description, debit_pairs, credit_pairs):

        # Fixme: for simulation

        self._description = description
        
        self._debit = {account.number:DebitImputation(self, account, float(amount))
                       for account, amount in debit_pairs}
        self._credit = {account.number:CreditImputation(self, account, float(amount))
                       for account, amount in credit_pairs}
        self._imputations = dict(self._debit)
        self._imputations.update(self._credit)
        
        self._check()

    ##############################################

    def _check(self):

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
        # Fixme: !!!
        obj._id = 1
        obj._document = ''
        obj._validation_date = '2016-01-01'
        obj._reconciliation_id = '1'
        obj._reconciliation_date = '2016-01-01'
        
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

    ##############################################

    def validate(self):

        if self._validation_date is not None:
            self._validation_date = datetime.datetime.utcnow()
        else:
            raise NameError('Journal entry is already validated')

    ##############################################

    def reconcile(self, reconciliation_id):

        if self._reconciliation_date is not None:
            self._reconciliation_id = reconciliation_id
            self._reconciliation_date = datetime.datetime.utcnow()
        else:
            raise NameError('Journal entry is already cleared')

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

    def log_entry_object(self, journal_entry):

        self._journal_entries.append(journal_entry)
        journal_entry.run()
        self._last_id += 1

    ##############################################

    def _make_imputation_pairs(self, imputations):

        return [(self._account_chart[account_number], amount)
                for account_number, amount in imputations.items()]

    ##############################################

    def log_entry(self, date, description, debit, credit, document=None):

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
        self.log_entry_object(journal_entry)

####################################################################################################
#
# End
#
####################################################################################################

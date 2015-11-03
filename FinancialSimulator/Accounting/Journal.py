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

from FinancialSimulator.Tools.Currency import format_currency
from FinancialSimulator.Tools.Date import parse_date, parse_datetime
from FinancialSimulator.Tools.Hierarchy import NonExistingNodeError
from FinancialSimulator.Tools.Observer import Observer
from FinancialSimulator.Tools.SequentialId import SequentialId
from FinancialSimulator.Units import round_currency
# from FinancialSimulator.Tools.DateIndexer import DateIndexer

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: move
class NegativeAmountError(ValueError):
    pass

class UnbalancedEntryError(NameError):
    pass

class DuplicatedEntryError(NameError):
    pass

####################################################################################################

class DebitMixin:
    def is_debit(self):
        return True
    def is_credit(self):
        return False

class CreditMixin:
    def is_debit(self):
        return False
    def is_credit(self):
        return True

####################################################################################################

class ImputationData:

    """This class defines an imputation template."""

    __imputation_class__ = None

    ##############################################

    def __init__(self, account, amount, analytic_account):

        # Fixme: account is a number here
        self.account = account
        self.analytic_account = analytic_account
        self.amount = float(amount) # Fixme: float or class ?

    ##############################################

    def resolve(self, account_chart, analytic_account_chart):

        # Fixme: pass a super/aggregation class
        account = account_chart[self.account]
        if self.analytic_account is not None:
            analytic_account = analytic_account_chart[self.analytic_account]
        else:
            analytic_account = None
        # Fixme: account are resolved now !
        return self.__class__(account, self.amount, analytic_account)

    ##############################################

    def to_imputation(self, journal_entry):

        # called in JournalEntryMixin.__init__
        return self.__imputation_class__(journal_entry,
                                         self.account, self.amount, self.analytic_account)

####################################################################################################

class Imputation:

    _logger = _module_logger.getChild('Imputation')

    ##############################################

    def __init__(self, journal_entry, account, amount, analytic_account):

        # Fixme: float()
        if amount < 0:
            raise NegativeAmountError()

        self._journal_entry = journal_entry
        self._account = account
        self._analytic_account = analytic_account
        self._amount = amount

    ##############################################

    @property
    def journal_entry(self):
        return self._journal_entry

    @property
    def date(self):
        return self._journal_entry.date

    @property
    def description(self):
        return self._journal_entry.description

    @property
    def account(self):
        return self._account

    @property
    def devise(self):
        return self._account.devise

    @property
    def analytic_account(self):
        return self._analytic_account

    @property
    def amount(self):
        return self._amount

    ##############################################

    @property
    def amount_str(self):

        return format_currency(self._amount)

    ##############################################

    @property
    def debit_str(self):

        if self.is_debit():
            return self.amount_str
        else:
            return ''

    ##############################################

    @property
    def credit_str(self):

        if self.is_credit():
            return self.amount_str
        else:
            return ''

    ##############################################

    def to_imputation(self, journal_entry):

        # Fixme: template -> 
        # called in JournalEntryMixin.__init__, overloaded
        return self.__class__(journal_entry,
                              self.account, self.amount, self.analytic_account)

    ##############################################

    def is_debit(self):
        raise NotImplementedError

    def is_credit(self):
        raise NotImplementedError

    ##############################################

    def __str__(self):

        if self.is_debit():
            letter = 'D'
        else:
            letter = 'C'
        string_format = '{} {:>10}: {:>10}'
        return string_format.format(letter, self._account.number, self.amount_str)

    ##############################################

    def apply(self):

        # Fixme: simulation vs accounting

        self._logger.info(str(self))
        
        if self.is_debit():
            self._account.apply_debit(self.amount)
        else:
            self._account.apply_credit(self.amount)
        self._account.history.save(self)
        
        if self._analytic_account is not None:
            if self.is_debit():
                self._analytic_account.apply_debit(self.amount)
            else:
                self._analytic_account.apply_credit(self.amount)
            self._analytic_account.history.save(self)

    ##############################################

    def to_json(self):

        d = {'account':self._account.number, 'amount':self._amount}
        if self._analytic_account is not None:
            d['analytic_account'] = self._analytic_account.number
        d['operation'] = 'D' if self.is_debit() else 'C'

        return d

####################################################################################################

class DebitImputation(DebitMixin, Imputation):
    pass

class CreditImputation(CreditMixin, Imputation):
    pass

class DebitImputationData(DebitMixin, ImputationData):
    __imputation_class__ = DebitImputation

class CreditImputationData(CreditMixin, ImputationData):
    __imputation_class__ = CreditImputation

####################################################################################################

class JournalEntryMixin:

    """This class defines a jounrnal entry template."""

    _logger = _module_logger.getChild('JournalEntryMixin')

    ##############################################

    def __init__(self, description, imputation_datas):

        self._description = description

        self._imputations = [imputation.to_imputation(self) for imputation in imputation_datas]
        self._imputations.sort(key=lambda x: x.account)
        self._debits = [imputation for imputation in self._imputations if imputation.is_debit()]
        self._credits = [imputation for imputation in self._imputations if imputation.is_credit()]
        
        self._check()

    ##############################################

    def _check(self):

        account_counter = {}
        account_numbers = [imputation.account for imputation in self._imputations]
        for account_number in account_numbers:
            if account_number in account_counter:
                self._logger.error(str(self))
                raise DuplicatedEntryError(account_number)
            else:
                account_counter[account_number] = 1
        
        sum_of_debits = self.sum_of_debits()
        sum_of_credits = self.sum_of_credits()
        if sum_of_debits != sum_of_credits:
            self._logger.error(str(self))
            message = "Journal Entry '{}' is not balanced D {} != C {}"
            raise UnbalancedEntryError(message.format(self._description,
                                                      sum_of_debits,
                                                      sum_of_credits))

    ##############################################

    @property
    def description(self):
        return self._description

    ##############################################

    def __str__(self):

        message = 'Journal Entry: {}\n'.format(self._description)
        # Fixme: duplicate
        for imputations in (self.debits, self.credits):
            message += '\n'.join([str(imputation) for imputation in imputations])
            message += '\n'
        return message

    ##############################################

    def _sum_of_imputations(self, imputations):
        return round_currency(sum([imputation.amount for imputation in imputations]))

    ##############################################

    def sum_of_debits(self):
        return self._sum_of_imputations(self._debits)

    ##############################################

    def sum_of_credits(self):
        return self._sum_of_imputations(self._credits)

    ##############################################

    def __iter__(self):
        return iter(self._imputations)

    ##############################################

    @property
    def imputations(self):
        # alias of __iter__
        return iter(self._imputations)

    ##############################################

    @property
    def debits(self):
        return iter(self._debits)

    ##############################################

    @property
    def credits(self):
        return iter(self._credits)

####################################################################################################

class JournalEntryTemplate(JournalEntryMixin):
    pass

####################################################################################################

class JournalEntry(JournalEntryMixin, Observer):

    ##############################################

    def __init__(self,
                 journal, sequence_number, date, description, document, imputations,
                 _internal_data=None,
    ):

        JournalEntryMixin.__init__(self, description, imputations)
        Observer.__init__(self)
        
        self._journal = journal
        self._id = sequence_number
        self._date = date
        self._document = document # accounting document

        if _internal_data is not None:
            self._validation_date = _internal_data['validation_date']
            self._reconciliation_id = _internal_data['reconciliation_id']
            self._reconciliation_date = _internal_data['reconciliation_date']
        else:
            self._validation_date = None
            self._reconciliation_id = None # clearing
            self._reconciliation_date = None

    ##############################################

    @property
    def journal(self):
        return self._journal

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
        for imputations in (self.debits, self.credits):
            message += '\n'.join([str(imputation) for imputation in imputations])
            message += '\n'
        return message

    ##############################################

    def apply(self):

        for imputation in self._imputations:
            imputation.apply()

    ##############################################

    def validate(self):

        if self._validation_date is None:
            self._validation_date = datetime.datetime.utcnow()
            self.changed()
        else:
            raise NameError('Journal entry is already validated')

    ##############################################

    def reconcile(self, reconciliation_id):

        if self._reconciliation_date is not None:
            self._reconciliation_id = reconciliation_id
            self._reconciliation_date = datetime.datetime.utcnow()
            self.changed()
        else:
            raise NameError('Journal entry is already cleared')

    ##############################################

    def to_json(self):

        d = {
            'journal': self._journal.label,
            'sequence_number': self._id,
            'date': str(self._date), # datetime is handled by pymongo
            'description': self._description,
            # 'document': = self._document
            'validation_date': str(self._validation_date),
            'reconciliation_id': self._reconciliation_id,
            'reconciliation_date': str(self._reconciliation_date),
            'debits': [imputation.to_json() for imputation in self._debits],
            'credits': [imputation.to_json() for imputation in self._credits],
        }

        return d

####################################################################################################

class Journal:

    # Fixme:
    # add/save entry = transaction
    # how to rollback ? backup/restore snapshot
    # update sequence number
    # update account chart snapshot / update date

    # Fixme:
    # journal -> period ?

    ##############################################

    def __init__(self, label, description, financial_period):

        self._label = label
        self._description = description
        
        self._account_chart = financial_period.account_chart
        self._analytic_account_chart = financial_period.analytic_account_chart
        # self._history = financial_period.history
        
        self._next_id = SequentialId() # Fixme: init from store
        self._journal_entries = [] # Fixme: data provider
        # self._date_indexer = DateIndexer(start, stop)

    ##############################################

    @property
    def label(self):
        return self._label

    ##############################################

    @property
    def description(self):
        return self._description

    ##############################################

    def run(self):

        self._account_chart.reset()
        for journal_entry in self._journal_entries:
            journal_entry.apply()

    ##############################################

    def _make_entry(self, date, description, imputations, document=None):

        sequence_number = self._next_id.increment()
        journal_entry = JournalEntry(self,
                                     sequence_number,
                                     date,
                                     description,
                                     document,
                                     imputations
        )
        self._append_entry(journal_entry)
        journal_entry.apply()
        
        return journal_entry

    ##############################################

    def log_entry(self, date, description, imputations, document=None):

        try:
            resolved_imputations = [imputation.resolve(self._account_chart, self._analytic_account_chart)
                                    for imputation in imputations]
            return self._make_entry(date, description, resolved_imputations, document)
        except NonExistingNodeError:
            raise

    ##############################################

    def log_template(self, date, template, document=None):

        return self._make_entry(date,
                               template.description,
                               template.imputations,
                               document,
        )

    ##############################################

    def _append_entry(self, journal_entry):

        self._journal_entries.append(journal_entry)

    ##############################################

    def __getitem__(self, slice_):

        return self._journal_entries[slice_]

    ##############################################

    def __iter__(self):

        return iter(self._journal_entries)

    ##############################################

    def filter(self, account=None, start_date=None, stop_date=None):

        # Fixme: use index

        for journal_entry in self._journal_entries:
            match = True
            # nA + A.B
            if account is not None and journal_entry.account != account:
                match = False
            if start_date is not None and start_date <= journal_entry.date:
                match = False
            if stop_date is not None and journal_entry.date <= stop_date:
                match = False
            if match:
                yield journal_entry

    ##############################################

    def journal_entry_from_json(self, data):

        date = parse_date(data['date'])
        validation_date = parse_datetime(data['validation_date'])
        reconciliation_date = data['reconciliation_date']
        if reconciliation_date != 'None':
            reconciliation_date = parse_datetime(reconciliation_date)
        else:
            reconciliation_date = None
        
        internal_data = {
            'validation_date': validation_date,
            'reconciliation_date': reconciliation_date,
            'reconciliation_id': data['reconciliation_id'],
        }
        
        imputations = []
        for imputation_jsons in data['debits'], data['credits']:
            for imputation_json in imputation_jsons:
                if imputation_json['operation'] == 'D':
                    imputation_data_class = DebitImputationData
                else:
                    imputation_data_class = CreditImputationData
                del imputation_json['operation'] # Fixme
                imputation_json.setdefault('analytic_account', None)
                imputation = imputation_data_class(**imputation_json)
                imputation.resolve(self._account_chart, self._analytic_account_chart)
                imputations.append(imputation)
        
        journal_entry = JournalEntry(self,
                                     data['sequence_number'],
                                     date,
                                     data['description'],
                                     None, # data['document'],
                                     imputations,
                                     _internal_data=internal_data,
        )
        
        return journal_entry

####################################################################################################
#
# End
#
####################################################################################################

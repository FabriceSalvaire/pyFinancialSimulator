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

from .Journal import Journal
from FinancialSimulator.Tools.SequentialId import SequentialId

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class JournalInMemory(Journal):

    ##############################################

    def __init__(self, label, description, financial_period):

        super().__init__(label, description, financial_period)
        
        self._next_id = SequentialId() # Fixme: init from store
        self._journal_entries = [] # Fixme: data provider
        # self._date_indexer = DateIndexer(start, stop)

    ##############################################

    def __bool__(self):

        return bool(len(self._journal_entries))

    ##############################################

    def __len__(self):

        return len(self._journal_entries)

    ##############################################

    def __getitem__(self, slice_):

        return self._journal_entries[slice_]

    ##############################################

    def __iter__(self):

        return iter(self._journal_entries)

    ##############################################

    def generate_sequence_number(self):

        return self._next_id.increment()

    ##############################################

    def write_entry(self, journal_entry):

        self._journal_entries.append(journal_entry)

    ##############################################

    def run(self):

        # Fixme: not here
        # self._account_chart.reset()
        # self._analytic_account_chart.reset()
        for journal_entry in self._journal_entries:
            journal_entry.apply()

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

    def to_json(self):

        """Save the journal to JSON"""

        return [journal_entry.to_json() for journal_entry in self]

    ##############################################

    def load_json(self, data):

        """Load a journal entry from JSON""" # but not: and apply it

        for journal_entry_json in data:
            journal_entry = self.journal_entry_from_json(journal_entry_json)
            self.write_entry(journal_entry)
        # Fixme: in-order !!!
        self._next_id = SequentialId(self._journal_entries[-1].sequence_number)

####################################################################################################
#
# End
#
####################################################################################################

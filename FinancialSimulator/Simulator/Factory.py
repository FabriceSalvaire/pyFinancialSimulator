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

from FinancialSimulator.Accounting import UnplannedTransaction
from .Actions import (SingleTransactionAction,
                      MonthlyTransactionAction,
                      QuaterlyTransactionAction,
                      AnnualTransactionAction,
)

####################################################################################################

class TransactionActionFactory(object):

    ##############################################

    def __init__(self, journals):

        self._journals = journals

    ##############################################

    def make_transaction_actions(self, yaml_loader, scheduler):

        for yaml_unit in yaml_loader:
            for transaction_definition in yaml_unit:
                action = self.make_transaction_action(transaction_definition)
                scheduler.add_action(action)

    ##############################################

    def make_transaction_action(self, transaction_definition):

        recurrence = transaction_definition.recurrence
        if recurrence == 'single':
            class_action = SingleTransactionAction
        elif recurrence == 'mensuel':
            class_action = MonthlyTransactionAction
        elif recurrence == 'trimestriel':
            class_action = QuaterlyTransactionAction
        elif recurrence == 'annuel':
            class_action = AnnualTransactionAction
        else:
            raise NameError(recurrence)

        journal = self._journals[transaction_definition.journal]
        # Fixme:
        debit = journal._make_imputation_pairs(transaction_definition.debit)
        credit = journal._make_imputation_pairs(transaction_definition.credit)
        transaction = UnplannedTransaction(debit, credit, transaction_definition.description)

        return  class_action(journal, transaction_definition.date, transaction)

####################################################################################################
#
# End
#
####################################################################################################

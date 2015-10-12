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

from FinancialSimulator.Scheduler import (SingleAction,
                                          MonthlyAction,
                                          QuaterlyAction,
                                          AnnualAction,
)

####################################################################################################

class TransactionActionMixin(object):

    ##############################################

    def __init__(self, journal, transaction):

        self._journal = journal
        self._transaction = transaction # unplanned

    ##############################################

    def run(self, date):

        self._journal.log_transaction_object(self._transaction.plan(date))

####################################################################################################

class SingleTransactionAction(TransactionActionMixin, SingleAction):

    ##############################################

    def __init__(self, journal, date, transaction):

        # Fixme: transaction has date
        SingleAction.__init__(self, date, transaction.description)
        TransactionActionMixin.__init__(self, journal, transaction)

####################################################################################################

class MonthlyTransactionAction(TransactionActionMixin, MonthlyAction):

    ##############################################

    def __init__(self, journal, date, transaction):

        # Fixme: transaction has date
        MonthlyAction.__init__(self, date, transaction.description)
        TransactionActionMixin.__init__(self, journal, transaction)

####################################################################################################

class QuaterlyTransactionAction(TransactionActionMixin, QuaterlyAction):

    ##############################################

    def __init__(self, journal, date, transaction):

        QuaterlyAction.__init__(self, date, transaction.description)
        TransactionActionMixin.__init__(self, journal, transaction)

####################################################################################################

class AnnualTransactionAction(TransactionActionMixin, AnnualAction):

    ##############################################

    def __init__(self, journal, date, transaction):

        AnnualAction.__init__(self, date, transaction.description)
        TransactionActionMixin.__init__(self, journal, transaction)

####################################################################################################
#
# End
#
####################################################################################################

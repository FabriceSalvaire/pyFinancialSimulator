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
#
# Logging
#

import FinancialSimulator.Logging.Logging as Logging

logger = Logging.setup_logging('financial-simulator')

####################################################################################################

import datetime
import unittest

####################################################################################################

from FinancialSimulator.Accounting import (load_account_chart,
                                           Journal,
                                           SimpleJournalEntry, DistributedJournalEntry
)
from FinancialSimulator.Scheduler import (SingleAction, ReccurentAction, MonthlyAction, Scheduler)

####################################################################################################

class TestSimulation(unittest.TestCase):

    def test(self):

        account_chart = load_account_chart('fr')

        journal_ventes = Journal('Ventes', account_chart)
        # AN   | Journal d'ouverture             | Journal de situation ouverture/clôture
        # BNK  | Liquidités                      | Liquidités
        # BNK  | Banque                          | Banques et chèques
        # ECNJ | Journal des avoirs d'achats     | Avoir fournisseur
        # EXJ  | Journal des achats              | Achat
        # OD   | Journal des opérations diverses | Général
        # SAJ  | Journal des ventes              | Vente
        # SCNJ | Journal des avoirs de ventes    | Avoir de vente

        journal_ventes.log_transaction('512',
                                       {'706':80, '44571':20},
                                       description='vente'
        )

        for account in account_chart:
            # print('{.code} {.name} {.balance}'.format(account))
            if account.debit or account.credit:
                print('{}-{} : {} €'.format(account.code, account.name, account.balance))

        # year = 2016
        # start_day = datetime.date(year, 3, 1)
        # stop_day = datetime.date(year +1, 6, 1)
        # day_timedelta = datetime.timedelta(1)

        # scheduler = Scheduler()
        # scheduler.add_action(SingleAction(datetime.date(year, 2, 1), label='action 1'))
        # scheduler.add_action(SingleAction(datetime.date(year, 2, 10), label='action 2'))
        # # scheduler.add_action(ReccurentAction(datetime.date(year, 1, 1),
        # #                                      datetime.timedelta(30),
        # #                                      label='reccurent action 1'))
        # scheduler.add_action(MonthlyAction(datetime.date(year, 1, 1),
        #                                    5,
        #                                    label='monthly action 1'))
        # scheduler.run(start_day, stop_day)

####################################################################################################

if __name__ == '__main__':

    unittest.main()

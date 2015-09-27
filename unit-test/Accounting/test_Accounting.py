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

import unittest

####################################################################################################

from FinancialSimulator.Accounting import (AccountChart, Account, Journal,
                                           SimpleTransaction, DistributedTransaction
)

####################################################################################################

class TestAccounting(unittest.TestCase):

    def test(self):

        # Plan comptable Français :
        #  44571 TVA collectée
        #  701 Ventes de produits finis
        #  702 Ventes de produits intermédiaires
        #  703 Ventes de produits résiduels
        #  706 Prestations de services
        #  707 Ventes de marchandises
        
        # Enregistrement d'une vente
        #  débit 512 Banques
        #  crédit 7 Ventes
        #  crédit 44571 TVA collectée
        
        account_chart = AccountChart('Plan Comptable Français')
        account_chart.add_account(Account('512', 'Banques'))
        account_chart.add_account(Account('706', 'Ventes de marchandises'))
        account_chart.add_account(Account('44571', 'TVA collectée'))
        
        journal_ventes = Journal('Ventes', account_chart)
        
        journal_ventes.log_transaction('512',
                                       {'706':80, '44571':20},
                                       description='vente'
        )
        
        for account in account_chart:
            # print('{.code} {.name} {.balance}'.format(account))
            print('{}-{} : {} €'.format(account.code, account.name, account.balance))

####################################################################################################

if __name__ == '__main__':

    unittest.main()

####################################################################################################
#
# End
#
####################################################################################################

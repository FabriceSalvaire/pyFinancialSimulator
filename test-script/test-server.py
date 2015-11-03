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

import FinancialSimulator.Logging.Logging as Logging

logger = Logging.setup_logging('financial-simulator')
_module_logger = logger

####################################################################################################

import datetime
import os

####################################################################################################

from FinancialSimulator.Accounting import Journal
from FinancialSimulator.Accounting.AccountChart import load_account_chart
from FinancialSimulator.WebApplication.Application import create_application

####################################################################################################

account_chart = load_account_chart('fr')

journals = {}
for code, label in (
        ('JSOC', "Journal d'ouverture"), # Journal de situation ouverture/clôture
        ('Liq', 'Liquidités'), # Liquidités
        ('Ban', 'Banque'), # Banques et chèques
        ('JAA', "Journal des avoirs d'achats"), # Avoir fournisseur
        ('JA', 'Journal des achats'), # Achat
        ('JOD', 'Journal des opérations diverses'), # Général
        ('JV', 'Journal des ventes'), # Vente
        ('JAV', 'Journal des avoirs de ventes'), # Avoir de vente
        ):
    journals[code] = Journal(label, account_chart)

####################################################################################################

journals['JV'].log_transaction(date=datetime.date(2016, 1, 1),
                               debit={'706':80, '44571':20},
                               credit={'512':100},
                               description='vente'
)

####################################################################################################

# Fixme: if DEBUG = True then reload ...

config_path = os.path.join(os.path.dirname(__file__), 'config.py')
application = create_application(config_path, account_chart, journals)
application.run()

####################################################################################################
#
# End
#
####################################################################################################

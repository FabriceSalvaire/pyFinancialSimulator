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

from pathlib import Path
import datetime

####################################################################################################

from FinancialSimulator.Accounting.FinancialPeriod import FinancialPeriod
from FinancialSimulator.Accounting.AccountChartLoader import load_account_chart_for_country
from FinancialSimulator.Accounting.Journal import DebitImputationData, CreditImputationData

from FinancialSimulator.WebApplication.Application import create_application

####################################################################################################

account_chart = load_account_chart_for_country('fr')

journal_definitions = (
    ('JSOC', "Journal d'ouverture"), # Journal de situation ouverture/clôture
    ('Liq', 'Liquidités'), # Liquidités
    ('Ban', 'Banque'), # Banques et chèques
    ('JAA', "Journal des avoirs d'achats"), # Avoir fournisseur
    ('JA', 'Journal des achats'), # Achat
    ('JOD', 'Journal des opérations diverses'), # Général
    ('JV', 'Journal des ventes'), # Vente
    ('JAV', 'Journal des avoirs de ventes'), # Avoir de vente
)

year = 2016
start_date = datetime.date(year, 1, 1)
stop_date = datetime.date(year, 12, 31)

financial_period = FinancialPeriod(account_chart, None, journal_definitions, start_date, stop_date)
account_chart = financial_period.account_chart
journals = financial_period.journals

####################################################################################################

# Fixme:
# File "/home/fabrice/home/developpement/python/financial-simulator/FinancialSimulator/Accounting/Journal.py", line 547, in generate_sequence_number
#    raise NotImplementedError
journals['JV'].log_entry(
    date=datetime.date(2016, 1, 1),
    description='vente',
    imputations=(
        DebitImputationData(706, 80, None, resolved=False),
        DebitImputationData(44571, 20, None, resolved=False),
        CreditImputationData(512, 100, None, resolved=False),
    )
)

####################################################################################################

# Fixme: if DEBUG = True then reload ...

root_path = Path(__file__).absolute().parents[1]
config_path = root_path.joinpath('FinancialSimulator', 'WebApplication', 'config.py')
application = create_application(config_path, account_chart, None, journals)
application.run()

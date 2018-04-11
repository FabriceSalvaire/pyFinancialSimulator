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

import json

####################################################################################################

class AccountingStore:

    ##############################################

    @staticmethod
    def save(financial_period, path):

        data = {
            'journals': financial_period.journals.to_json(),
            'accounts': financial_period.account_chart.to_json(),
            'analytic_accounts': financial_period.analytic_account_chart.to_json(),
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    ##############################################

    @staticmethod
    def load(financial_period, path):

        with open(path) as f:
            data = json.load(f)

        financial_period.journals.load_json(data['journals'])

        for journal in financial_period.journals:
            journal.run()

        # financial_period.account_chart.force_balance_from_json(data['accounts'])
        # financial_period.analytic_account_chart.force_balance_from_json(data['analytic_accounts'])

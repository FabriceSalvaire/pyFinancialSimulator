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

class Model:

    ##############################################

    def __init__(self, application=None):

        self._application = application
        if application is not None:
            self.init_app(application)

    ##############################################

    def init_app(self, application):

        self._application = application
        # Fixme: FinancialPeriod
        self._account_chart = self._application.config['account_chart']
        self._analytic_account_chart = self._application.config['analytic_account_chart']
        self._journals = self._application.config['journals']

    ##############################################

    @property
    def account_chart(self):
        return self._account_chart

    ##############################################

    @property
    def analytic_account_chart(self):
        return self._analytic_account_chart

    ##############################################

    @property
    def journals(self):
        return self._journals

####################################################################################################

model = Model()

####################################################################################################
#
# End
#
####################################################################################################

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

from .Journal import Journals

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class FinancialPeriod(object):

    ##############################################

    def __init__(self,
                 account_chart,
                 journals,
                 start_date,
                 stop_date
    ):

        # Fixme: template
        self._account_chart = account_chart
        self._journals = Journals(account_chart, journals)
        
        self._start_date = start_date
        self._stop_date = stop_date

    ##############################################

    @property
    def account_chart(self):
        return self._account_chart

    ##############################################

    @property
    def journals(self):
        return self._journals

    ##############################################

    @property
    def start_date(self):
        return self._start_date

    ##############################################

    @property
    def stop_date(self):
        return self._stop_date

####################################################################################################
#
# End
#
####################################################################################################

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

from FinancialSimulator.Scheduler import (SingleAction,
                                          ReccurentAction,
                                          MonthlyAction,
                                          WeeklyAction,
                                          Scheduler)

####################################################################################################

class TestAccounting(unittest.TestCase):

    def test(self):

        year = 2016
        start_day = datetime.date(year, 3, 1)
        stop_day = datetime.date(year +1, 6, 1)
        day_timedelta = datetime.timedelta(1)

        scheduler = Scheduler()
        # scheduler.add_action(SingleAction(datetime.date(year, 2, 1), label='action 1'))
        # scheduler.add_action(SingleAction(datetime.date(year, 2, 10), label='action 2'))
        # scheduler.add_action(MonthlyAction(datetime.date(year, 1, 5),
        #                                    label='monthly action 1'))
        scheduler.add_action(WeeklyAction(datetime.date(year, 1, 5),
                                          label='monthly action 1'))
        for planned_action in scheduler.iter(start_day, stop_day):
            print(planned_action)

####################################################################################################

if __name__ == '__main__':

    unittest.main()

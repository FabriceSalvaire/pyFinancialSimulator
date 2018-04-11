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

import datetime
import unittest

####################################################################################################

from FinancialSimulator.Tools.Date import date_iterator
from FinancialSimulator.Tools.DateIndexer import DateIndexer

####################################################################################################

class DateObj:

    ##############################################

    def __init__(self, date):

        self._date = date

    ##############################################

    @property
    def date(self):
        return self._date

####################################################################################################

class TestDateIndexer(unittest.TestCase):

    def test(self):

        start = datetime.date(2016, 1, 1)
        stop = datetime.date(2116, 12, 31) # 245 MB

        date_indexer = DateIndexer(start, stop)
        for date in date_iterator(start, stop):
            for i in range(date.day):
                date_indexer.append(DateObj(date))
        for date_list in date_indexer:
            self.assertEqual(len(date_list), date_list.date.day)

        # import time
        # for i in range(1000000):
        #     time.sleep(.001)

####################################################################################################

if __name__ == '__main__':

    unittest.main()

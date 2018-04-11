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

from .Date import clone_date, date_iterator, monthly_iterator, date_iterator_in_month

####################################################################################################

class OutOfDateError(ValueError):
    pass

####################################################################################################

class DateList(list):

    ##############################################

    def __init__(self, date):

        super().__init__()
        self._date = clone_date(date)

    ##############################################

    @property
    def date(self):
        return self._date

####################################################################################################

class DateIndexer:

    # Fixme: month/year iterator

    ##############################################

    def __init__(self):

        self._start = None
        self._stop = None
        self._dates = {}

    ##############################################

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    ##############################################

    def __getitem__(self, date):

        if self._start <= date <= self._stop:
            key = date.toordinal()
            if key in self._dates:
                return self._dates[key]
            else:
                return None
        else:
            raise OutOfDateError

    ##############################################

    def append(self, obj):

        date = clone_date(obj.date) # costly but sure
        if self._start is None:
            self._start = self._stop = date
        else:
            self._start = min(self._start, date)
            self._stop = max(self._stop, date)

        key = date.toordinal()
        if key not in self._dates:
            self._dates[key] = DateList(date)
        self._dates[key].append(obj)

    ##############################################

    def __len__(self):
        return len(self._dates)

    ##############################################

    def __iter__(self):

        for date in date_iterator(self._start, self._stop):
            yield from self.iter_on_date(date)

    ##############################################

    def iter_on_date(self, date):

        date_list = self[date]
        if date_list is not None:
            yield from iter(date_list)
        else:
            raise StopIteration

    ##############################################

    def monthly_iter(self):

        for month_date in monthly_iterator(self._start, self._stop):
            dates = []
            for date in date_iterator_in_month(month_date):
                date_list = self[date]
                if date_list is not None:
                    dates.append(date_list)
            if dates:
                yield month_date, dates

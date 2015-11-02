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

####################################################################################################

from .Date import clone_date, date_iterator

####################################################################################################

class OutOfDateError(ValueError):
    pass

####################################################################################################

class DateList(list):

    ##############################################

    def __init__(self, date):

        super().__init__()
        self._date = date

    ##############################################

    @property
    def date(self):
        return self._date

####################################################################################################

class DatePeriodIndexer:

    # Fixme: month/year iterator

    ##############################################

    def __init__(self, start, stop):

        self._start = clone_date(start)
        self._stop = clone_date(stop)
        # Fixme: cf. infra (list):
        self._dates = [DateList(date) for date in date_iterator(self._start, self._stop)]

    ##############################################

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    ##############################################

    def __len__(self):
        return len(self._dates)

    ##############################################
    
    def __iter__(self):
        return iter(self._dates)

    ##############################################

    def date_to_index(self, date):

        return (date - self._start).days

    ##############################################

    def __getitem__(self, date):

        if self._start <= date <= self._stop:
            return self._dates[self.date_to_index(date)]
        else:
            raise OutOfDateError

    ##############################################

    def append(self, obj):

        self[obj.date].append(obj)

    ##############################################

    def iter_on_date(self, date):

        return iter(self[date])

####################################################################################################

class DateIndexer:

    # Fixme: month/year iterator

    ##############################################

    def __init__(self, epoch=datetime.date(1900, 1, 1)):

        self._epoch = epoch
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

    def __len__(self):
        return len(self._dates)

    ##############################################
    
    def __iter__(self):

        # return iter(self._dates)
        for date in date_iterator(self._start, self._stop):
            date_list = self[date]
            if date_list is not None:
                yield from iter(date_list)

    ##############################################

    def date_to_index(self, date):

        # Fixme: fast ?
        return (date - self._epoch).days

    ##############################################

    def __getitem__(self, date):

        if self._start <= date <= self._stop:
            key = self.date_to_index(date)
            if key in self._dates:
                return self._dates[key]
            else:
                return None
        else:
            raise OutOfDateError

    ##############################################

    def append(self, obj):

        # Fixme: clone_date
        date = obj.date
        if self._start is None:
            self._start = self._stop = date
        else:
            self._start = min(self._start, date)
            self._stop = max(self._stop, date)
        
        key = self.date_to_index(date)
        if key not in self._dates:
            self._dates[key] = DateList(date)
        self._dates[key].append(obj)

    ##############################################

    def iter_on_date(self, date):

        return iter(self[date])

####################################################################################################
#
# End
#
####################################################################################################

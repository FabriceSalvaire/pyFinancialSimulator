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

import calendar
import datetime

####################################################################################################

def clone_date(date):
    return datetime.date(date.year, date.month, date.day)

####################################################################################################

def fist_month_day_of(date):
    return date.replace(day=1)

####################################################################################################

# iter_on_date / date_iterator

def date_iterator(start, stop, step=datetime.timedelta(days=1)):
    date = start
    while date <= stop:
        yield date
        date += step

####################################################################################################

def monthly_iterator(start, stop):
    # cf. calendar Calendar.itermonthdates
    start = fist_month_day_of(start)
    for year in range(start.year, stop.year +1):
        # can do more for first and last year
        for month in range(1, 13):
            date = datetime.date(year, month, 1)
            if start <= date <= stop:
                yield date

####################################################################################################

def date_iterator_in_month(date):
    first_day, last_day = calendar.monthrange(date.year, date.month)
    for day in range(first_day, last_day):
        yield date.replace(day=day)

####################################################################################################

def parse_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

####################################################################################################

def parse_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

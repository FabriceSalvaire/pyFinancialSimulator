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
import datetime

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def date_iterator(start, stop, step):
    date = start
    while date < stop:
        yield date
        date += step

####################################################################################################

class Action(object):

    ##############################################

    def __init__(self, label=''):

        self._label = label

    ##############################################

    @property
    def label(self):

        return self._label

    ##############################################

    def next_dates(self, start_date, stop_date):

        raise NotImplementedError

    ##############################################

    def run(self, date):

        # self._logger.info(str(self))
        # raise NotImplementedError
        pass

####################################################################################################

class SingleAction(Action):

    _logger = _module_logger.getChild('SingleAction')

    ##############################################

    def __init__(self, date, label=''):

        super(SingleAction, self).__init__(label)
        self._date = date

    ##############################################

    def __str__(self):

        return 'Action {} @{}'.format(self._label, self._date)

    ##############################################

    def next_dates(self, start_date, stop_date):

        if start_date <= self._date <= stop_date:
            yield self._date
        else:
            raise StopIteration

####################################################################################################

class ReccurentAction(Action):

    _logger = _module_logger.getChild('ReccurentAction')

    ##############################################

    def __init__(self, start_date, period, label=''):

        super(ReccurentAction, self).__init__(label)
        self._start_date = start_date
        self._period = period

    ##############################################

    def next_dates(self, start_date, stop_date):

        date = self._start_date
        while date <= stop_date:
            if start_date <= date:
                yield date
            date += self._period

####################################################################################################

class MonthlyAction(Action):

    _logger = _module_logger.getChild('MonthlyAction')

    ##############################################

    def __init__(self, start_date, day_number, label=''):

        super(MonthlyAction, self).__init__(label)
        self._start_date = start_date
        self._day_number = day_number

    ##############################################

    def next_dates(self, start_date, stop_date):

        date = datetime.date(start_date.year, start_date.month, self._day_number)
        while date <= stop_date:
            if start_date <= date:
                yield date
            if date.month == 12:
                date = datetime.date(date.year +1, 1, self._day_number)
            else:
                date = datetime.date(date.year, date.month +1, self._day_number)

####################################################################################################

class RandomAction(Action):

    _logger = _module_logger.getChild('RandomAction')

    ##############################################

    def __init__(self, start_date, label=''):

        super(RandomAction, self).__init__(label)
        self._start_date = start_date

    ##############################################

    def next_dates(self, start_date, stop_date):

        # slope:
        #   flat
        #   increasing
        #   decreasing
        #   increasing -> decreasing
        # Gaussian noise
        
        pass
        # date = datetime.date(start_date.year, start_date.month, self._day_number)
        # while date <= stop_date:
        #     if start_date <= date:
        #         yield date

####################################################################################################

class PlannedAction(object):

    _logger = _module_logger.getChild('PlannedAction')

    ##############################################

    def __init__(self, action, date):

        self._action = action
        self._date = date

    ##############################################

    def __lt__(self, other):

        return self._date < other._date

    ##############################################

    def run(self):

        self._logger.info('Run {} @{}'.format(self._action.label, self._date))
        self._action.run(self._date)

####################################################################################################

class PlannedActions(dict):

    _logger = _module_logger.getChild('SingleAction')

    ##############################################

    def __init__(self, start_date):

        super(PlannedActions, self).__init__()

        self._start_date = start_date

    ##############################################

    def add_action(self, action, date):

        delta_day = (date - self._start_date).days
        planned_action = PlannedAction(action, date)
        if delta_day in self:
            self[delta_day].append(planned_action)
        else:
            self[delta_day] = [planned_action]

    ##############################################

    def sort(self):

        for item in self.values():
            item.sort()

####################################################################################################

class Scheduler(object):

    _logger = _module_logger.getChild('Scheduler')

    ##############################################

    def __init__(self):

        self._actions = []

    ##############################################

    def add_action(self, action):

        self._actions.append(action)

    ##############################################

    def run(self, start_date, stop_date):

        planned_actions = PlannedActions(start_date)
        for action in self._actions:
            for next_date in action.next_dates(start_date, stop_date):
                planned_actions.add_action(action, next_date)
        planned_actions.sort()
        
        number_of_days = (stop_date - start_date).days +1
        for delta_day in range(number_of_days):
            if delta_day in planned_actions:
                day_planned_actions = planned_actions[delta_day]
                for planned_action in day_planned_actions:
                    planned_action.run()

####################################################################################################
#
# End
#
####################################################################################################

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

from FinancialSimulator.Tools.Hierarchy import Node, Hierarchy

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Account(Node):

    _logger = _module_logger.getChild('Account')

    ##############################################

    def __init__(self, number, description,
                 parent=None,
                 devise='€',
                 comment='',
                 system=''):

        self._number = number
        super().__init__(parent)
        self._description = description
        self._comment = comment
        self._system = system # PCG Fr: classe, base, abrégé, développé
        self._devise = devise

    ##############################################

    @property
    def description(self):
        return self._description

    ##############################################

    @property
    def number(self):
        return self._number

    ##############################################

    @property
    def comment(self):
        return self._comment

    ##############################################

    @property
    def system(self):
        return self._system

    ##############################################

    @property
    def devise(self):
        return self._devise

    ##############################################

    def __hash__(self):

        # Fixme:
        return int(self._number)

    ##############################################

    def __lt__(self, other):

        number1 = str(self._number)
        number2 = str(other._number)
        return number1 < number2
        # for d1, d2 in zip(number1, number2):
        #     if d1 < d2:
        #         return True
        #     elif d1 > d2:
        #         return False

    ##############################################

    def __str__(self):
        return '#{}'.format(self._number)

    ##############################################

    def __repr__(self):
        return str(self)

####################################################################################################

class AccountChart(Hierarchy):

    ##############################################

    def __init__(self, name):

        super().__init__()
        
        self._name = name

    ##############################################

    @property
    def name(self):

        return self._name

####################################################################################################
#
# End
#
####################################################################################################

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

from atomiclong import AtomicLong

####################################################################################################

class SequentialId:

    ##############################################

    def __init__(self, start_id=0):

        self._id = AtomicLong(start_id)

    ##############################################

    def __int__(self):
        return self._id.value

    ##############################################

    def increment(self):
        # right ?
        # value = self._id.value
        self._id += 1
        value = self._id.value
        return value

####################################################################################################
#
# End
#
####################################################################################################

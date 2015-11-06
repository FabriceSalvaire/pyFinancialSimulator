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

from .IterTools import pairwise

####################################################################################################

class Slicer:

    ##############################################

    def __init__(self, slices):

        self._check(slices)
        self._thresholds = tuple(slices)
        self._slices = tuple([t2 - t1 for t1, t2 in pairwise([0] + list(self._thresholds))])

    ##############################################

    def _check(self, slices):

        previous_slice = slices[0]
        for current_slice in slices[1:]:
            if current_slice < previous_slice:
                raise ValueError
            previous_slice = current_slice

    ##############################################

    def slice(self, value):

        slices = []
        for slice_ in self._slices:
            if slice_ < value:
                slices.append(slice_)
                value -= slice_
                if not value:
                    break
            else:
                slices.append(value)
                break
        
        return slices

####################################################################################################
#
# End
#
####################################################################################################

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

class Observer:

    __global_listeners__ = []

    ##############################################

    def __init__(self):

        self._changed = False
        self._listeners = []

    ##############################################

    def attach_listener(self, listener, is_global=True):

        if is_global:
            listeners = self.__global_listeners__
        else:
            listeners = self._listeners
        if listener not in listeners:
            listeners.append(listener)
        # else

    ##############################################

    def detach_listener(self, listener, is_global=True):

        if is_global:
            listeners = self.__global_listeners__
        else:
            listeners = self._listeners
        listeners.remove(listener)

    ##############################################

    def has_changed(self):
        return self._changed

    ##############################################

    def changed(self):

        # thread safe
        self._changed = True
        for listeners in self._listeners, self.__global_listeners__:
            for listener in listeners:
                # Fixme: self notify listener
                listener.notify(self)

####################################################################################################
#
# End
#
####################################################################################################

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

import unittest

####################################################################################################

from FinancialSimulator.Tools.Observer import Observer, Signal, receiver_decorator

####################################################################################################

class Emitter:

    signal = Signal()

    ##############################################

    def __repr__(self):
        return "<Emitter at 0x{:x}>".format(id(self))

    ##############################################

    def emit(self, message):

        return self.signal.send(sender=self, message=message)

####################################################################################################

class Receiver:

    ##############################################

    # @receiver_decorator(Emitter.signal)
    # def global_slot(signal, sender, message):

    #     print(signal, sender, message)

    ##############################################

    def slot(self, signal, sender, message):

        print(signal, sender, message)
        return self

####################################################################################################

class TestSignal(unittest.TestCase):

    def test(self):

        emitter = Emitter()
        receiver1 = Receiver()
        receiver2 = Receiver()
        emitter.signal.connect(receiver1.slot)
        emitter.signal.connect(receiver2.slot)

        self.assertTrue(emitter.signal.has_listeners())

        self.assertListEqual(emitter.emit('a message'),
                             [(receiver1.slot, receiver1),
                              (receiver2.slot, receiver2),
                             ])

        del receiver1
        self.assertTrue(emitter.signal.has_listeners())

        del receiver2
        self.assertFalse(emitter.signal.has_listeners())

####################################################################################################

if __name__ == '__main__':

    unittest.main()

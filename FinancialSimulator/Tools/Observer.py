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

# metaclass
#
# obj.signal.emit(*args, **kwargs)
# obj.signal.connect(slot)
#

####################################################################################################

import logging
import threading
import weakref

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Observer:

    __global_listeners__ = []

    _logger = _module_logger.getChild('Observer')

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

    def _listener_iter(self):

        for listeners in self._listeners, self.__global_listeners__:
            for listener in listeners:
                yield listener

    ##############################################

    def changed(self):

        """Signal to indicate a modification"""

        # self._logger.info('')
        # thread safe
        self._changed = True
        for listener in self._listener_iter():
            listener.on_change(self)

    ##############################################

    def reseted(self):

        """Signal to indicate a wipe"""

        self._changed = True
        for listener in self._listener_iter():
            listener.on_reset(self)

####################################################################################################

class Signal:

    ##############################################

    def __init__(self):

        self._lock = threading.Lock()
        self._receivers = []
        self._dead_receivers = True

    ##############################################

    def connect(self, receiver):

        # Check for bound methods
        if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
            ref = weakref.WeakMethod
            receiver_object = receiver.__self__
        else:
            ref = weakref.ref
            receiver_object = receiver
        receiver_ref = ref(receiver)
        weakref.finalize(receiver_object, self._remove_receiver)

        with self._lock:
            self._clear_dead_receivers()
            if receiver not in self._receivers:
                self._receivers.append(receiver_ref)

    ##############################################

    def disconnect(self, receiver):

        with self._lock:
            self._clear_dead_receivers()
            try:
                self._receivers.remove(receiver)
            except ValueError:
                pass

    ##############################################

    def has_listeners(self):

        self._clear_dead_receivers()
        return bool(self._receivers)

    ##############################################

    def send(self, sender, **kwargs):

        # return [(receiver, receiver(signal=self, sender=sender, **kwargs))
        #         for receiver in self._receivers]

        self._clear_dead_receivers()
        responses = []
        for receiver_ref in self._receivers:
            receiver = receiver_ref()
            response = receiver(signal=self, sender=sender, **kwargs)
            responses.append((receiver, response))

        return responses

    ##############################################

    def _remove_receiver(self):

        # Mark that the self.receivers list has dead weakrefs. If so, we will clean those up in
        # connect, disconnect and _live_receivers while holding self.lock.

        # Note that doing the cleanup here isn't a good idea, _remove_receiver() will be called as
        # side effect of garbage collection, and so the call can happen while we are already holding
        # self.lock.

        self._dead_receivers = True

    ##############################################

    def _clear_dead_receivers(self):

        # Note: caller is assumed to hold self.lock.

        if self._dead_receivers:
            self._dead_receivers = False
            self._receivers = [receiver
                               for receiver in self._receivers
                               if receiver() is not None]

####################################################################################################

def receiver_decorator(signal, **kwargs):

    """A decorator for connecting receivers to signals. Used by passing in the signal (or list of
    signals) and keyword arguments to connect::

        @receiver(post_save)
        def signal_receiver(sender, **kwargs):
            ...

        @receiver([post_save, post_delete])
        def signals_receiver(sender, **kwargs):
            ...

    """

    def _decorator(func):
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func

    return _decorator

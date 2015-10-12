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

def round_currency(x):
    return round(x, 2)

####################################################################################################

class AmountValue(object):

    ##############################################

    def __init__(self, currency, value, vat_rate=0, is_inclusive=None):

        self._currency = currency
        self._vat_rate = vat_rate
        self._is_inclusive = is_inclusive
        
        if is_inclusive:
            value = value / (1 + vat_rate / 100)
        self._value = round_currency(value)

    ##############################################

    def __str__(self):

        if self._is_inclusive is None:
            vat_suffix = ''
        elif self._is_inclusive:
            vat_suffix = 'TTC'
        else:
            vat_suffix = 'HT'
        
        return '{:.2f} {} {}'.format(float(self), self._currency, vat_suffix)

    ##############################################

    def __float__(self):

        if self._is_inclusive is None:
            return self._value
        elif self._is_inclusive:
            return self.to_inclusive()
        else:
            return self._value

    ##############################################

    @property
    def currency(self):
        return self._currency

    ##############################################

    @property
    def is_inclusive(self):
        return self._is_inclusive

    ##############################################

    @property
    def vat_rate(self):
        return self._vat_rate

    ##############################################

    @property
    def exclusive(self):
        return AmountValue(self._currency, self._value, self._vat_rate, is_inclusive=False)

    ##############################################

    @property
    def vat(self):
        value = self._value * self.vat_rate / 100
        return AmountValue(self._currency, value)

    ##############################################

    def to_inclusive(self):
        return round_currency(self._value * (1 + self._vat_rate / 100))

    ##############################################

    @property
    def inclusive(self):
        value = self._value * (1 + self._vat_rate / 100)
        return AmountValue(self._currency, value, self._vat_rate, is_inclusive=True)

    ##############################################

    ht = exclusive
    ttc = inclusive
    tva = vat
    taux_tva = vat_rate

    ##############################################

    def __mul__(self, x):

        value = float(self._value) * float(x)
        return AmountValue(self._currency, value, self._vat_rate, self._is_inclusive)

####################################################################################################

class PercentValue(object):

    ##############################################

    def __init__(self, value):

        self._value = value / 100

    ##############################################

    def __str__(self):

        return '{} %'.format(self._value * 100)

    ##############################################

    def __float__(self):

        return self._value

    ##############################################

    def __rsub__(self, x):

        return PercentValue((float(x) - self._value) * 100)

####################################################################################################
#
# End
#
####################################################################################################

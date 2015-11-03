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

import re

####################################################################################################

from FinancialSimulator.Units import AmountValue, PercentValue

####################################################################################################

class ParseError(Exception):
    pass

####################################################################################################

class AmountValueParser:

    ##############################################

    def parse(self, value_string):

        value_string = value_string.replace(',', '.')
        if '€' in value_string:
            return self._parse_euro(value_string)
        elif '$' in value_string:
            return self._parse_usd(value_string)
        else:
            raise ParseError('Unknown currency')

        # , taxe
        # if taxe == 'ach-20':
        #     self._vat_rate = 20

    ##############################################

    def _parse_euro(self, value_string):

        m = re.match(r'(\d+\.?\d*) €( (HT|TTC))?( @(N))?', value_string)
        if m is not None:
            currency = '€'
            value = float(m.group(1))
            prefix = m.group(3)
            if prefix is None:
                is_inclusive = None
            else:
                is_inclusive = prefix == 'TTC'
            vat_rate = m.group(5)
            if vat_rate == 'N':
                vat_rate = 20
            else:
                vat_rate = 0
            return AmountValue(currency, value, vat_rate, is_inclusive)
        else:
            raise ParseError('Bad euro amount')

    ##############################################

    def _parse_usd(self, value_string):

        m = re.match(r'\$(\d+\.?\d*) USD', value_string)
        if m is not None:
            currency = 'USD'
            value = float(m.group(1))
            is_inclusive = False
            return AmountValue(currency, value, 0, is_inclusive)
        else:
            raise ParseError('Bad USD amount')


####################################################################################################

class PercentValueParser:

    ##############################################

    def parse(self, value):

        value = value.replace(',', '.')
        m = re.match(r'(\d+\.?\d*) *%', value)
        if m is not None:
            percentage = float(m.group(1))
            return PercentValue(percentage)
        else:
            raise ParseError(value)

####################################################################################################

class ValueParser:

    ##############################################

    def __init__(self):

        self._percent_parser = PercentValueParser()
        self._amount_parser = AmountValueParser()
        
        self._parsers = [
            self._percent_parser,
            self._amount_parser,
        ]

    ##############################################

    def parse(self, value):

        for parser in self._parsers:
            try:
                return parser.parse(value)
            except ParseError:
                pass
        raise NameError('Cannot parse {}'.format(value))

####################################################################################################
#
# End
#
####################################################################################################

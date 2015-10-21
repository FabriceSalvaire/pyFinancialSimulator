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

import locale

# Fixme:
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

####################################################################################################

def format_currency(value, symbol='€'):
    if value:
        if value < 0:
            sign = '- '
        else:
            sign = ''
        formatted_value = locale.currency(abs(value), grouping=True, symbol=False)
        return sign + formatted_value + ' ' + symbol
    else:
        return ''

####################################################################################################
#
# End
#
####################################################################################################

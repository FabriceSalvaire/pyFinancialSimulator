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

def digit_iterator(x):

    while True:
        x, d = divmod(x, 10)
        yield d
        if not x:
            break

####################################################################################################

def luhn_checksum(x):
    digits = list(digit_iterator(int(x)))
    odd_digits = digits[0::2]
    even_digits = digits[1::2]
    s = sum(odd_digits) + sum(sum(divmod(d*2,10)) for d in even_digits)
    return s % 10

####################################################################################################

def is_luhn_valid(x):
    return luhn_checksum(x) == 0

####################################################################################################

def luhn_checksum_digit(x):
    checksum = luhn_checksum(int(x) * 10)
    if checksum == 0:
        return 0
    else:
        return 10 - checksum

####################################################################################################

def append_luhn_checksum(x):
    return int(x) * 10 + luhn_checksum_digit(x)

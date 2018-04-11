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

# branch = guichet

####################################################################################################

_rib_letter_to_number = {}
for i in range(0, 10):
    _rib_letter_to_number[str(i)] = str(i)
for k in ('A', 'J'):
    _rib_letter_to_number[k] = '1'
for k in ('B', 'K', 'S'):
    _rib_letter_to_number[k] = '2'
for k in ('C', 'L', 'T'):
    _rib_letter_to_number[k] = '3'
for k in ('D', 'M', 'U'):
    _rib_letter_to_number[k] = '4'
for k in ('E', 'N', 'V'):
    _rib_letter_to_number[k] = '5'
for k in ('F', 'O', 'W'):
    _rib_letter_to_number[k] = '6'
for k in ('G', 'P', 'X'):
    _rib_letter_to_number[k] = '7'
for k in ('H', 'Q', 'Y'):
    _rib_letter_to_number[k] = '8'
for k in ('I', 'R', 'Z'):
    _rib_letter_to_number[k] = '9'

####################################################################################################

def _rib_to_number(x):
    return int(''.join([_rib_letter_to_number[d] for d in str(x)]))

####################################################################################################

_iban_letter_to_number = {}
for i in range(0, 10):
    _iban_letter_to_number[str(i)] = str(i)
for i in range(ord('A'), ord('Z') +1):
    _iban_letter_to_number[chr(i)] = str(i - ord('A') +10)

####################################################################################################

def _remove_space(text):
    return text.replace(' ', '').replace('-', '')

####################################################################################################

def check_iban(iban):

    iban_ = _remove_space(iban)
    n = int(''.join([_iban_letter_to_number[d] for d in iban_[4:] + iban_[:4]]))

    return n % 97 == 1

####################################################################################################

class BankAccountNumber:

    ##############################################

    def __init__(self, bank_id, branch_id, account_id, key=None, country_code=None):

        self._bank_id = bank_id
        self._branch_id = branch_id
        self._account_id = account_id
        self._country_code = country_code

        computed_key = self._make_checksum()
        if key is not None and key != computed_key:
            raise NameError("Wrong key")
        self._key = computed_key

    ##############################################

    @property
    def bank_id(self):
        return self._bank_id

    @property
    def branch_id(self):
        return self._branch_id

    @property
    def account_id(self):
        return self._account_id

    @property
    def key(self):
        return self._key

    @property
    def country_code(self):
        return self._country_code

    ##############################################

    def _make_checksum(self):

        bank_id = _rib_to_number(self._bank_id)
        branch_id = _rib_to_number(self._branch_id)
        account_id = _rib_to_number(self._account_id)

        return 97 - ((89 * bank_id + 15 * branch_id + 3 * account_id) % 97)

    ##############################################

    @property
    def bban(self):

        return '{0._bank_id:05} {0._branch_id:05} {0._account_id:11} {0._key:2}'.format(self)

    ##############################################

    @property
    def iban(self):

        # France (27) Format IBAN : FRkk BBBB BGGG GGCC CCCC CCCC CKK
        #
        # B = code banque, G = code guichet, C = numéro de compte, K = clef
        #
        # Note: le BBAN correspond au RIB. Si ce dernier ne comporte que des chiffres, l'IBAN commence
        # par FR76 suivi du RIB scindé en groupes de quatre caractères (voir la section Exemples
        # ci-dessous).

        country_code = self._country_code.upper()
        # bban = bban.upper()
        bban_ = _remove_space(self.bban)
        n = int(''.join([_iban_letter_to_number[d] for d in bban_ + country_code + '00']))
        checksum = 98 - n % 97
        iban = country_code + str(checksum) + bban_

        return ' '.join([iban[i:i+4] for i in range(0, len(iban), 4)])

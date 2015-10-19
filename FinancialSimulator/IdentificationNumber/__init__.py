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

from .LuhnChecksum import append_luhn_checksum

####################################################################################################

def format_siren(siren):

    siren = str(siren)
    return ' '.join((siren[:3], siren[3:6], siren[6:9]))

####################################################################################################

def format_siret(siret):

    siret = str(siret)
    return ' '.join((siret[:3], siret[3:6], siret[6:9], siret[9:]))

####################################################################################################

def compute_fr_vat_key(siren):

    return (12 + 3 * (int(siren) % 97)) % 97

####################################################################################################

def make_fr_vat(siren):

    return ' '.join(('FR', str(compute_fr_vat_key(siren)), format_siren(siren)))

####################################################################################################

def make_siret(siren, etablissement):

    return append_luhn_checksum(siren * 10000 + etablissement)

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

def make_rib_checksum(bank_code, code_guichet, account_code):

    bank_code = _rib_to_number(bank_code)
    code_guichet = _rib_to_number(code_guichet)
    account_code = _rib_to_number(account_code)

    return 97 - ((89 * bank_code + 15 * code_guichet + 3 * account_code) % 97)

####################################################################################################

_iban_letter_to_number = {}
for i in range(0, 10):
    _iban_letter_to_number[str(i)] = str(i)
for i in range(ord('A'), ord('Z') +1):
    _iban_letter_to_number[chr(i)] = str(i - ord('A') +10)

####################################################################################################

def make_bban(bank_code, code_guichet, account_code):

    checksum = make_rib_checksum(bank_code, code_guichet, account_code)
    return '{:05} {:05} {:11} {:2}'.format(bank_code, code_guichet, account_code, checksum)

####################################################################################################

def make_iban(code_coutry, bban):

    # France (27) Format IBAN : FRkk BBBB BGGG GGCC CCCC CCCC CKK
    #
    # B = code banque, G = code guichet, C = numéro de compte, K = clef
    #
    # Note: le BBAN correspond au RIB. Si ce dernier ne comporte que des chiffres, l'IBAN commence
    # par FR76 suivi du RIB scindé en groupes de quatre caractères (voir la section Exemples
    # ci-dessous).

    code_coutry = code_coutry.upper()
    # bban = bban.upper()
    bban_ = bban.replace(' ', '').replace('-', '')
    n = int(''.join([_iban_letter_to_number[d] for d in bban_ + code_coutry + '00']))
    checksum = 98 - n % 97
    iban = code_coutry + str(checksum) + bban_
    
    return ' '.join([iban[i:i+4] for i in range(0, len(iban), 4)])

####################################################################################################

def check_iban(iban):

    iban_ = iban.replace(' ', '').replace('-', '')
    n = int(''.join([_iban_letter_to_number[d] for d in iban_[4:] + iban_[:4]]))
    
    return n % 97 == 1

####################################################################################################
#
# End
#
####################################################################################################

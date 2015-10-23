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
#
# End
#
####################################################################################################

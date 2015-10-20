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

import os
import yaml

####################################################################################################

from .Account import Account, AccountChart

####################################################################################################

_account_charts = {
    'fr': 'plan-comptable-francais.yml',
}

def load_account_chart(country_code):

    yaml_path = os.path.join(os.path.dirname(__file__), country_code, _account_charts[country_code])
    with open(yaml_path, 'r') as f:
        data = yaml.load(f.read())

    metadata = data['metadata']
    account_chart = AccountChart(name=metadata['name'])
    
    previous = None
    parent = [None]
    current_level = 1
    for account_definition in data['plan']:
        number = int(account_definition['code'])
        description = account_definition['description']
        comment = account_definition.get('commentaire', '')
        system = account_definition['système']
        item_level = len(str(number))
        if item_level > current_level:
            parent.append(previous)
            current_level = item_level
        elif item_level < current_level:
            parent = parent[:item_level-current_level]
            current_level = item_level
        account = Account(number, description, parent=parent[-1], comment=comment, system=system)
        account_chart.add_node(account)
        previous = account
    
    return account_chart

####################################################################################################
#
# End
#
####################################################################################################

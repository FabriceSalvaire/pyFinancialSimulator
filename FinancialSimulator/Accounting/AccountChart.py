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

####################################################################################################

from FinancialSimulator.Accounting import Account, AccountChart

####################################################################################################

_account_charts = {
    'fr': 'plan-comptable-français.txt',
}

def load_account_chart(country_code):

    txt_file = os.path.join(os.path.dirname(__file__), _account_charts[country_code])
    with open(txt_file) as f:
        lines = f.readlines()
    
    kwargs = {}
    i = 0
    while not lines[i].startswith('#'):
        name, value = [x.strip() for x in lines[i].split(':')]
        kwargs[name] = value
        i += 1
    account_chart = AccountChart(**kwargs)
    
    previous = None
    parent = [None]
    current_level = 1
    for line in lines[i+1:]:
        code, name = [x.strip() for x in line.split('|')]
        item_level = len(code)
        if item_level > current_level:
            parent.append(previous)
            current_level = item_level
        elif item_level < current_level:
            parent = parent[:item_level-current_level]
            current_level = item_level
        account = Account(code, name, parent=parent[-1])
        account_chart.add_account(account)
        previous = account
    
    return account_chart

####################################################################################################
#
# End
#
####################################################################################################

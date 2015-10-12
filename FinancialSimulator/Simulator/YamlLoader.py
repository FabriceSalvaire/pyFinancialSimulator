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

import yaml
import logging

####################################################################################################

from .Parser import ValueParser

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

_value_parser = ValueParser()

####################################################################################################

class Parameters(dict):

    _logger = _module_logger.getChild('Parameters')

    ##############################################

    def __init__(self, definitions):

        super(Parameters, self).__init__()
        
        for name, value_string in definitions.items():
            value = _value_parser.parse(value_string)
            self[name] = value
            self._logger.info('{} = {}'.format(name, value))

####################################################################################################

class Variables(dict):

    _logger = _module_logger.getChild('Variables')

    ##############################################

    def __init__(self, definitions, parameters):

        super(Variables, self).__init__(parameters)
        
        for name, value_string in definitions.items():
            value = eval(value_string, self)
            self[name] = value
            self._logger.info('{} = {}'.format(name, value))

####################################################################################################

class TransactionDefinition(object):

    _logger = _module_logger.getChild('Transactions')

    ##############################################

    def __init__(self, definition):

        # self._logger.info(str(definition))
        self._definition = definition

        self._debit = {}
        self._credit = {}
        for key, value in self._definition.items():
            if key.startswith('debit'):
                account_code = key[len('debit '):]
                self._debit[account_code] = value
            elif key.startswith('credit'):
                account_code = key[len('credit '):]
                self._credit[account_code] = value

    ##############################################

    @property
    def journal(self):
        return 'JOD'

    @property
    def date(self):
        return self._definition['date']

    @property
    def recurrence(self):
        return self._definition.get('recurrence', 'single')

    @property
    def description(self):
        return self._definition['label']

    @property
    def debit(self):
        return self._debit

    @property
    def credit(self):
        return self._credit

####################################################################################################

class YamlUnit(object):

    _logger = _module_logger.getChild('YamlUnit')

    ##############################################

    def __init__(self, path):

        self._path = path
        
        self._logger.info('load {}'.format(path))
        with open(path, 'r') as f:
            data = yaml.load(f.read())
        if data is not None:
            self._parameters = Parameters(data.get('parameters', {}))
            self._variables = Variables(data.get('variables', {}), self._parameters)
            transactions = data.get('transactions', [])
            self._transactions = [self._parse_transaction(transaction)
                                  for transaction in transactions
                                  if not transaction.get('skip', False)]
        else:
            self._parameters = None
            self._variables = None
            self._transactions = []

    ##############################################

    def _parse_transaction(self, transaction):

        local_variables = dict(self._variables)
        for key, value_string in transaction.items():
            if key.startswith('local '):
                name = key[len('local_'):]
                value = _value_parser.parse(value_string)
                local_variables[name] = value
                self._logger.info('{} = {}'.format(name, value))
        
        for key, value_string in transaction.items():
            if key.startswith('debit ') or key.startswith('credit '):
                name = key[key.find(' ')+1:]
                value = eval(value_string, local_variables)
                transaction[key] = value
                self._logger.info('{} = {}'.format(key, value))
        
        return TransactionDefinition(transaction)

    ##############################################

    def __iter__(self):

        return iter(self._transactions)

####################################################################################################

class YamlLoader(object):

    ##############################################

    def __init__(self):

        self._yaml_units = []

    ##############################################

    def load(self, path):

        self._yaml_units.append(YamlUnit(path))

    ##############################################

    def __iter__(self):

        return iter(self._yaml_units)

####################################################################################################
#
# End
#
####################################################################################################

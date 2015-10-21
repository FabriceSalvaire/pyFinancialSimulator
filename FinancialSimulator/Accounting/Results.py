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

import logging
import os
import yaml

####################################################################################################

from FinancialSimulator.HDL.HdlParser import HdlAccountParser
from FinancialSimulator.HDL.Evaluator import AccountEvaluator
from FinancialSimulator.Tools import Hierarchy

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Node(Hierarchy.Node):

    ##############################################

    def __init__(self, level=0):

        super(Node, self).__init__()
        self._level = level

    ##############################################

    @property
    def level(self):
        return self._level

####################################################################################################

class EmptyRow(Node):

    ##############################################

    def __init__(self, level, number_of_lines):

        super(EmptyRow, self).__init__(level)
        
        self._number_of_lines = number_of_lines

####################################################################################################

class Row(Node):

    ##############################################

    def __init__(self, level, title, show=True):

        super(Row, self).__init__(level)
        
        self._title = title
        self._show = show

    ##############################################

    @property
    def title(self):
        return self._title

    ##############################################

    @property
    def show(self):
        return self._show

####################################################################################################

class ValueRow(Row):

    ##############################################

    def __init__(self, level, title, computation=None):

        super(ValueRow, self).__init__(level, title)
        
        self._computation = computation

    ##############################################

    @property
    def computation(self):
        return self._computation

    ##############################################

    def compute(self, evaluator):

        if self._computation is not None:
            return evaluator.run_ast_program(self._computation)
        else:
            return 0

####################################################################################################

class SumRow(Row):

    ##############################################

    def __init__(self, level, title, show, position):

        super(SumRow, self).__init__(level, title, show)
        
        self._position = position

####################################################################################################

class ComputationVisitor(object):

    ##############################################

    def __init__(self, account_chart):

        self._evaluator = AccountEvaluator(account_chart)
        self.reset()

    ##############################################

    def reset(self):

        self._cache = {}

    ##############################################

    def compute(self, node):

        node_id = id(node)
        if node_id in self._cache:
            return self._cache[node_id]
        else:
            # Fixme: better ?
            if isinstance(node, SumRow):
                value = sum([self.compute(sibling) for sibling in node])
            elif isinstance(node, Row):
                value = node.compute(self._evaluator)
            else:
                value = 0
            self._cache[node_id] = value
            return value

    ##############################################

    def __getitem__(self, node):

        return self.compute(node)

####################################################################################################

class Table(object):

    ##############################################

    def __init__(self, title):

        self._title = title
        self._columns = []

    ##############################################

    def append_column(self, column):
        self._columns.append(column)

    ##############################################

    def __iter__(self):

        return iter(self._columns)

####################################################################################################

class Column(object):

    ##############################################

    def __init__(self, title, node):

        self._title = title
        self._node = node
        self._rows = []

    ##############################################

    @property
    def title(self):
        return self._title

    ##############################################

    @property
    def node(self):
        return self._node

    ##############################################

    def append_empty_row(self):
        self._rows.append(None)

    ##############################################

    def append_row(self, row):
        self._rows.append(row)

    ##############################################

    def __iter__(self):

        return iter(self._rows)

####################################################################################################

hdl_parser = HdlAccountParser()

class YamlLoader(object):

    _logger = _module_logger.getChild('YamlLoader')

    ##############################################

    def __init__(self, yaml_file):

        country_code = 'fr'
        yaml_path = os.path.join(os.path.dirname(__file__), country_code, yaml_file)
        with open(yaml_path, 'r') as f:
            data = yaml.load(f.read())
        
        self._table = Table('')
        for title, items in data.items():
            node = Node()
            self._column = Column(title, node)
            for item in items:
                sibling = self._process_node(item)
                if sibling is not None:
                    node.add_sibling(sibling)
            self._table.append_column(self._column)

    ##############################################

    def _process_node(self, node_data, level=0):

        # self._logger.info(str(node_data))
        if 'childs' in node_data:
            title = node_data['title']
            position = node_data.get('position', 'before')
            show = node_data.get('show', False)
            self._logger.info('Node ' + title)
            row = SumRow(level, title, show, position)
            if position == 'before':
                self._column.append_row(row)
            for child_data in node_data['childs']:
                sibling = self._process_node(child_data, level +1)
                if sibling is not None:
                    row.add_sibling(sibling)
            if position == 'after':
                self._column.append_row(row)
            return row
        elif 'padding' in node_data:
            number_of_lines = int(node_data['padding'])
            for i in range(number_of_lines):
                self._column.append_empty_row()
            return EmptyRow(level, number_of_lines)
        else:
            title = node_data['title']
            self._logger.info('Row ' + title)
            if 'computation' in node_data:
                computation = hdl_parser.parse(str(node_data['computation']))
            else:
                computation = None
            row = ValueRow(level, title, computation)
            self._column.append_row(row)
            return row

    ##############################################

    @property
    def table(self):
        return self._table

####################################################################################################
#
# End
#
####################################################################################################

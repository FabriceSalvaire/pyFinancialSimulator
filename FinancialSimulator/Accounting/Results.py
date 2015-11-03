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

from FinancialSimulator.HDL.Ast import Variable, Assignation
from FinancialSimulator.HDL.HdlParser import HdlAccountParser
from FinancialSimulator.HDL.Evaluator import AccountEvaluator, AccountSetEvaluator
from FinancialSimulator.Tools import Hierarchy
from FinancialSimulator.Tools.Currency import format_currency
import FinancialSimulator.Config.ConfigInstall as ConfigInstall

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Node(Hierarchy.Node):

    # Fixme: Leaf

    ##############################################

    def __init__(self, level=0):

        super().__init__()
        self._level = level

    ##############################################

    @property
    def level(self):
        return self._level

####################################################################################################

class EmptyRow(Node):

    ##############################################

    def __init__(self, level, number_of_lines):

        super().__init__(level)
        
        self._number_of_lines = number_of_lines

    ##############################################

    def compute(self, visitor):

        if visitor.set_evaluator:
            return set()
        else:
            return 0

####################################################################################################

class Row(Node):

    ##############################################

    def __init__(self, level, title, show=True):

        super().__init__(level)
        
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

        super().__init__(level, title)
        
        self._computation = computation

    ##############################################

    @property
    def computation(self):
        return self._computation

    ##############################################

    def compute(self, visitor):

        if self._computation is not None:
            return visitor.evaluator.run_ast_program(self._computation)
        else:
            if visitor.set_evaluator:
                return set()
            else:
                return 0

####################################################################################################

class SumRow(Row):

    ##############################################

    def __init__(self, level, title, show, position, variable=None):

        super().__init__(level, title, show)
        
        self._position = position
        self._variable = variable

    ##############################################

    @property
    def variable(self):
        return self._variable

    ##############################################

    def compute(self, visitor):

        if visitor.set_evaluator:
            value = set()
            for sibling in self:
                print(sibling.title)
                value |= visitor.compute(sibling)
        else:
            value = sum([visitor.compute(sibling) for sibling in self])
        if self._variable is not None:
            visitor.evaluator[self._variable] = value
        return value

####################################################################################################

class DependencyNode(Hierarchy.Node):

    ##############################################

    def __init__(self, variable, row):

        super().__init__()
        
        self._variable = variable
        self._row = row

    ##############################################

    @property
    def variable(self):
        return self._variable

    ##############################################

    @property
    def row(self):
        return self._row

####################################################################################################

class ComputationVisitor:

    ##############################################

    def __init__(self, account_chart, set_evaluator=False):

        self._set_evaluator = set_evaluator
        if set_evaluator:
            evaluator = AccountSetEvaluator
        else:
            evaluator = AccountEvaluator
        self._evaluator = evaluator(account_chart)
        self.reset()

    ##############################################

    @property
    def set_evaluator(self):
        return self._set_evaluator

    ##############################################

    @property
    def evaluator(self):
        return self._evaluator

    ##############################################

    def reset(self):

        self._cache = {}

    ##############################################

    def compute(self, node):

        node_id = id(node)
        if node_id in self._cache:
            return self._cache[node_id]
        else:
            value = node.compute(self)
            self._cache[node_id] = value
            return value

    ##############################################

    def __getitem__(self, node):

        return self.compute(node)

    ##############################################

    def str_value(self, node):

        return format_currency(self.compute(node))

####################################################################################################

class Table:

    _logger = _module_logger.getChild('Table')

    ##############################################

    def __init__(self, title):

        self._title = title
        self._columns = []
        
        self._variable_to_row = None
        self._assignation_to_row = None
        self._variable_to_dependency_node = None

    ##############################################

    def append_column(self, column):
        self._columns.append(column)

    ##############################################

    def __iter__(self):

        return iter(self._columns)

    ##############################################

    def make_dependency_graph(self):

        self._variable_to_row = {}
        self._assignation_to_row = {}
        for column in self:
            for row in column.node.depth_first_search():
                if isinstance(row, SumRow):
                    self._process_sum_row(row)
                elif isinstance(row, ValueRow):
                    self._process_value_row(row)
        
        variables = dict(self._variable_to_row)
        variables.update(self._assignation_to_row)
        variable_to_dependency_node = {variable:DependencyNode(variable, node)
                                       for variable, node in variables.items()}
        for variable, row in self._assignation_to_row.items():
            ast = row.computation[0]
            operands = [str(node) for node in ast.depth_first_search() if isinstance(node, Variable)]
            node = variable_to_dependency_node[variable]
            for operand in operands:
                node.add_sibling(variable_to_dependency_node[operand])
        self._variable_to_dependency_node = variable_to_dependency_node

    ##############################################

    def _process_sum_row(self, row):

        if row.variable is not None:
            self._variable_to_row[str(row.variable)] = row

    ##############################################

    def _process_value_row(self, row):

        if row.computation is not None:
            ast = row.computation[0]
            if isinstance(ast, Assignation):
                self._assignation_to_row[str(ast.destination)] = row

    ##############################################

    def compute(self, account_chart, **kwargs):

        computation_visitor = ComputationVisitor(account_chart, **kwargs)
        for root_node in self._variable_to_dependency_node.values():
            for dependency_node in root_node.depth_first_search_sibling():
                # self._logger.info('{} = ...'.format(dependency_node.variable))
                value = computation_visitor.compute(dependency_node.row)
                self._logger.info('{} = {}'.format(dependency_node.variable, value))
        return computation_visitor

####################################################################################################

class Column:

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

class YamlLoader:

    _logger = _module_logger.getChild('YamlLoader')

    ##############################################

    def __init__(self, yaml_file):

        country_code = 'fr'
        yaml_path = os.path.join(ConfigInstall.Path.accounting_data_directory,
                                 country_code, yaml_file)
        with open(yaml_path, 'r') as f:
            data = yaml.load(f.read())
        
        self._table = Table('')
        # for title, items in data.items():
        for title in sorted(data.keys()):
            items = data[title]
            node = Node()
            self._column = Column(title, node)
            for item in items:
                sibling = self._process_node(item)
                if sibling is not None:
                    node.add_sibling(sibling)
            self._table.append_column(self._column)
        
        self._table.make_dependency_graph()

    ##############################################

    def _process_node(self, node_data, level=0):

        # self._logger.info(str(node_data))
        if 'childs' in node_data:
            return self._process_sum_row(node_data, level)
        elif 'padding' in node_data:
            return self._process_empty_row(node_data, level)
        else:
            return self._process_value_row(node_data, level)

    ##############################################

    def _process_sum_row(self, node_data, level):

        title = node_data['title']
        variable = node_data.get('assign', None)
        position = node_data.get('position', 'before')
        show = node_data.get('show', False)
        
        self._logger.info('Node ' + title)
        row = SumRow(level, title, show, position, variable)
        
        if position == 'before':
            self._column.append_row(row)
        for child_data in node_data['childs']:
            sibling = self._process_node(child_data, level +1)
            if sibling is not None:
                row.add_sibling(sibling)
        if position == 'after':
            self._column.append_row(row)
        
        return row

    ##############################################

    def _process_empty_row(self, node_data, level):

        number_of_lines = int(node_data['padding'])
        for i in range(number_of_lines):
            self._column.append_empty_row()
        
        return EmptyRow(level, number_of_lines)

    ##############################################

    def _process_value_row(self, node_data, level):

        title = node_data['title']
        if 'computation' in node_data:
            computation = str(node_data['computation'])
            computation = hdl_parser.parse(computation)
        else:
            computation = None
        
        self._logger.info('Row ' + title)
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

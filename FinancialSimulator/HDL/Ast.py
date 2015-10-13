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

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class StatementList(object):

    ##############################################

    def __init__(self, *statements):

        self._statements = list(statements)

    ##############################################

    def __nonzero__(self):

        return bool(self._statements)

    ##############################################

    def __iter__(self):

        return iter(self._statements)

    ##############################################

    def append(self, statement):

        self._statements.append(statement)

    ##############################################

    def __str__(self):

        return '\n'.join([str(statement) for statement in self])

####################################################################################################

class Variable(object):
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name

####################################################################################################

class Account(Variable):
    pass

####################################################################################################

class Expression(object):

    __number_of_operands__ = None

    ##############################################

    def __init__(self, *args, **kwargs):

        if (self.__number_of_operands__ is not None
            and len(args) != self.__number_of_operands__):
            raise ValueError("Wrong number of operands")

        self._operands = args

    ##############################################

    def iter_on_operands(self):
        return iter(self._operands)

    ##############################################

    @property
    def operand(self):
        return self._operands[0]

    @property
    def operand1(self):
        return self._operands[0]

    @property
    def operand2(self):
        return self._operands[1]

class UnaryExpression(Expression):
    __number_of_operands__ = 1

class BinaryExpression(Expression):
    __number_of_operands__ = 2

####################################################################################################

class Assignation(UnaryExpression):

    ##############################################

    def __init__(self, destination, value):

        super(Assignation, self).__init__(value)
        self._destination = destination

    @property
    def destination(self):
        return self._destination

    @property
    def value(self):
        return self._operands[0]

    def __str__(self):
        # ←
        return ' '.join((str(self.destination), '<-', str(self.value)))

####################################################################################################

class Function(Expression):

    ##############################################

    def __init__(self, name, *args):

        super(Function, self).__init__(*args)
        self._name = name

    ##############################################

    @property
    def name(self):
        return self._name

    ##############################################

    def __str__(self):

        parameters = ', '.join([str(operand) for operand in self.iter_on_operands()])
        return self._name + ' (' + parameters  + ')'

####################################################################################################

class BinaryOperator(BinaryExpression):
    __operator__ = None

    def __str__(self):
        return '(' + ' '.join((str(self.operand1), self.__operator__, str(self.operand2))) + ')'

####################################################################################################

class Addition(BinaryOperator):
    __operator__ = '+'

class Subtraction(BinaryOperator):
    __operator__ = '-'

class Multiplication(BinaryOperator):
    __operator__ = '*' # ×

class Division(BinaryOperator):
    __operator__ = '/'

####################################################################################################
#
# End
#
####################################################################################################

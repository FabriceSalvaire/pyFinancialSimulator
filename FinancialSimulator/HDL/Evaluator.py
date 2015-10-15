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

class Evaluator(object):

    _logger = _module_logger.getChild('Evaluator')

    ##############################################

    def __init__(self):

        self._variables = {}

    ##############################################

    def eval_statement(self, level, statement):

        # self._logger.debug('')

        statement_class = statement.__class__.__name__
        # if statement_class == 'Function':
        #     statement_class = statement.name
        evaluator = getattr(self, 'eval_' + statement_class)
        if hasattr(statement, 'iter_on_operands'):
            # Compute the operand values: traverse recursively the AST
            args = [self.eval_statement(level+1, operand)
                    for operand in statement.iter_on_operands()]
            value = evaluator(level, statement, *args)
        else:
            value = evaluator(level, statement)
        
        return value

    ##############################################

    def run_ast_program(self, program):

        for statement in program:
            result = self.eval_statement(0, statement)
        return result

    ##############################################

    def eval_Variable(self, level, statement):

        return self._variables[str(statement)]

    ##############################################

    def eval_Assignation(self, level, statement, value):

        value = float(value)
        self._variables[str(statement.destination)] = value
        return value

    ##############################################

    def eval_Addition(self, level, statement, operand1, operand2):

        return float(operand1) + float(operand2)

    ##############################################

    def eval_Subtraction(self, level, statement, operand1, operand2):

        return float(operand1) - float(operand2)

    ##############################################

    def eval_Multiplication(self, level, statement, operand1, operand2):

        return float(operand1) * float(operand2)

    ##############################################

    def eval_Division(self, level, statement, operand1, operand2):

        return float(operand1) / float(operand2)

####################################################################################################

class NumericalEvaluator(Evaluator):

    ##############################################

    def eval_Constant(self, level, statement):

        return float(statement)

####################################################################################################

class AccountEvaluator(Evaluator):

    ##############################################

    def __init__(self, account_chart):

        super(AccountEvaluator, self).__init__()
        
        self._account_chart = account_chart

    ##############################################

    def eval_Account(self, level, statement):

        # Fixme: signed etc.
        try:
            account = self._account_chart[str(statement)]
            if account.balance:
                return account.debit
            else:
                return account.credit
        except KeyError:
            self._logger.warning("Account {} doesn't exist".format(str(statement)))
            return 0

    ##############################################

    def eval_AccountInterval(self, level, statement):

        # Fixme: check
        value = 0
        for code in statement:
            value += self.eval_Account(level, code)
        return value

####################################################################################################
#
# End
#
####################################################################################################

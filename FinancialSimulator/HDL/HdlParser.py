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

import ply.lex as lex
import ply.yacc as yacc

####################################################################################################

from .Ast import *

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class HdlParser(object):

    _logger = _module_logger.getChild('HdlParser')

    ##############################################

    _operator_to_class = {operator_class.__operator__:operator_class
                          for operator_class in (
                                  Addition,
                                  Division,
                                  Multiplication,
                                  Subtraction,
                          )
    }

    ##############################################

    reserved = {
    }

    tokens = [
        'DECIMAL_NUMBER',
        'NAME',
        'LEFT_PARENTHESIS', 'RIGHT_PARENTHESIS',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'SET',
    ] + list(reserved.values())

    ##############################################

    def t_error(self, token):
        self._logger.error("Illegal character '%s' at line %u and position %u" %
                           (token.value[0],
                            token.lexer.lineno,
                            token.lexer.lexpos - self._previous_newline_position))
        # token.lexer.skip(1)
        raise NameError('Lexer error')

    ##############################################

    t_ignore  = ' \t'

    def t_newline(self, t):
        r'\n+'
        # Track newline
        t.lexer.lineno += len(t.value)
        self._previous_newline_position = t.lexer.lexpos
        # t.type = 'SEMICOLON'
        # return t

    t_ignore_COMMENT = r'\#[^\n]*'

    ##############################################

    t_LEFT_PARENTHESIS = r'\('
    t_RIGHT_PARENTHESIS = r'\)'

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'

    t_SET = r'='

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # Check for reserved words
        t.type = self.reserved.get(t.value, 'NAME')
        return t

    def t_DECIMAL_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    ##############################################
    #
    # Grammar
    #

    # from lowest
    precedence = (
        # ('left', 'EQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        # ('right', 'UMINUS'),
    )

    def p_error(self, p):
        self._logger.error("Syntax error at '%s'", p.value)
        raise NameError('Parser error')

    start = 'statement'

    def p_statement_expr(self, p):
        'statement : expression'
        self._statements.append(p[1])

    def p_assignation(self, p):
        'statement : NAME SET expression'
        statement = Assignation(Variable(p[1]), p[3])
        self._statements.append(statement)

    def p_expression_name(self, p):
        'expression : NAME'
        p[0] = Variable(p[1])

    def p_expression_group(self, p):
        'expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS'
        p[0] = p[2]

    def p_binary_operation(self, p):
        # ... OP ...
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
        '''
        p[0] = self._operator_to_class[p[2]](p[1], p[3])

    ##############################################

    def __init__(self):

        self._build()

    ##############################################

    def _build(self, **kwargs):

        self._lexer = lex.lex(module=self, **kwargs)
        self._parser = yacc.yacc(module=self, **kwargs)

    ##############################################

    def _reset(self):

        self._previous_newline_position = 0
        self._statements = StatementList()

    ##############################################

    def parse(self, text):

        self._reset() # Fixme: after ?
        self._parser.parse(text, lexer=self._lexer)
        return self._statements

    ##############################################

    def test_lexer(self, text):

        self._reset()
        self._lexer.input(text)
        while True:
            token = self._lexer.token()
            if not token:
                break
            print(token)

####################################################################################################

class HdlNumericalParser(object):

    ##############################################

    def p_constant(self, p):
        '''expression : DECIMAL_NUMBER
        '''
        p[0] = Constant(p[1])

####################################################################################################

class HdlAccountParser(object):

    ##############################################

    def p_account(self, p):
        '''expression : DECIMAL_NUMBER
        '''
        p[0] = Account(str(p[1]))

####################################################################################################
#
# End
#
####################################################################################################
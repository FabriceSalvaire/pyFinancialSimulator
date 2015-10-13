####################################################################################################

from FinancialSimulator.HDL.HdlParser import HdlParser
from FinancialSimulator.HDL.Evaluator import Evaluator

####################################################################################################

hdl_parser = HdlParser()

source = 'T = 1 + 2 - 3 * (4 + 5) / 2'
statements = hdl_parser.parse(source)
print(statements)

evaluator = Evaluator()
result = evaluator.run_ast_program(statements)
print(result)

####################################################################################################
#
# End
#
####################################################################################################

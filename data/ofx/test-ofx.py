####################################################################################################

from FinancialSimulator.Accounting.BankStatement.OfxImporter import OfxSgmlParser

ofx_path = '4342989F0331445589627532.ofx'
ofx_parser = OfxSgmlParser()
bank_statement = ofx_parser.parse(ofx_path)
for transaction in bank_statement:
    print(transaction)

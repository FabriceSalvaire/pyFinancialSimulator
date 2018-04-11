####################################################################################################

from FinancialSimulator.Accounting.AccountChart import load_account_chart

####################################################################################################

account_chart = load_account_chart('fr')

for account in account_chart:
    if account.system == 'abrégé':
        print("{} - {}".format(account.code, account.name))

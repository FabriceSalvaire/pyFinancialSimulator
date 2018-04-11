####################################################################################################

from FinancialSimulator.Accounting.AccountChartLoader import load_account_chart_for_country

####################################################################################################

account_chart = load_account_chart_for_country('fr')

for account in account_chart:
    if account.system == 'abrégé':
        print(account)
        # print('{} - {}'.format(account.code, account.name))

####################################################################################################

import datetime
import os

####################################################################################################

import FinancialSimulator.Logging.Logging as Logging

logger = Logging.setup_logging('financial-simulator')
_module_logger = logger

####################################################################################################

from FinancialSimulator.Accounting.FinancialPeriod import FinancialPeriod
from FinancialSimulator.Accounting.AccountChartLoader import load_account_chart_for_country
from FinancialSimulator.Tools.Hierarchy import NonExistingNodeError
from FinancialSimulator.Tools.Currency import format_currency

####################################################################################################

account_chart = load_account_chart_for_country('fr')

journal_definitions = (
    ('JSOC', "Journal d'ouverture"), # Journal de situation ouverture/clôture
    ('Liq', 'Liquidités'), # Liquidités
    ('Ban', 'Banque'), # Banques et chèques
    ('JAA', "Journal des avoirs d'achats"), # Avoir fournisseur
    ('JA', 'Journal des achats'), # Achat
    ('JOD', 'Journal des opérations diverses'), # Général
    ('JV', 'Journal des ventes'), # Vente
    ('JAV', 'Journal des avoirs de ventes'), # Avoir de vente
)

year = 2016
start_date = datetime.date(year, 1, 1)
stop_date = datetime.date(year, 12, 31)

financial_period = FinancialPeriod(account_chart, None, journal_definitions, start_date, stop_date)
account_chart = financial_period.account_chart
journals = financial_period.journals

def to_float(x):
    if '+' in x:
        return float(eval(x))
    elif x:
        return float(x)
    else:
        return 0

data_path = 'data/exercice-p353.csv'
with open(data_path, 'r') as f:
    for line in f:
        account_number, debit, credit = line.strip().split(',')
        account_number = int(account_number)
        debit = to_float(debit)
        credit = to_float(credit)
        try:
            account = account_chart[account_number]
            account.force_balance(debit, credit)
        except NonExistingNodeError:
            _module_logger.warning("Account {} doesn't exist".format(account_number))

if False:
    for account in account_chart:
        if account.has_imputations():
            print('{}-{} : Solde Débiteur: {} € Créditeur: {} €'.format(account.number,
                                                                        account.description,
                                                                        account.debit,
                                                                        account.credit))
if False:
    from FinancialSimulator.Accounting import Results

    # yaml_file = 'systeme-abrege-resultat-tableau.yml'
    yaml_file = 'systeme-base-bilan-tableau.yml'
    # yaml_file = 'systeme-base-resultat-tableau.yml'
    yaml_loader = Results.YamlLoader(yaml_file)
    table = yaml_loader.table

    computation_visitor = table.compute(account_chart)
    for column in table:
        print('\n' + column.title)
        for row in column:
            if not isinstance(row, Results.EmptyRow):
                title_width = 80
                title = '  '*row.level + row.title[:title_width - 2*row.level]
                value = computation_visitor[row]
                if row.show and value:
                    string_format = '{:' + str(title_width) + '} {}'
                    print(string_format.format(title, format_currency(value)))
                else:
                    string_format = '{:' + str(title_width) + '}'
                    print(string_format.format(title))

if False:
    from FinancialSimulator.Accounting import Results

    # yaml_file = 'systeme-abrege-resultat-tableau.yml'
    # yaml_file = 'systeme-base-bilan-tableau.yml'
    yaml_file = 'systeme-base-resultat-tableau.yml'
    yaml_loader = Results.YamlLoader(yaml_file)
    table = yaml_loader.table

    computation_visitor = table.compute(account_chart, set_evaluator=True)
    evaluator = computation_visitor.evaluator
    used = evaluator['Tactif'] | evaluator['Tpassif']
    pcg_set = set(account for account in account_chart if account.system == 'base')
    delta = pcg_set - used
    for account in list(delta):
        if account in delta:
            account_set = set(account.depth_first_search()) - set(account)
            if account_set <= delta:
                delta -= account_set
    print('Delta:', sorted(delta))

if True:
    from FinancialSimulator.WebApplication.Application import create_application

    # Fixme: if DEBUG = True then reload ...
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    application = create_application(config_path, account_chart, None, journals)
    application.run()

####################################################################################################

import datetime
import glob
import os

####################################################################################################

import FinancialSimulator.Logging.Logging as Logging

logger = Logging.setup_logging('financial-simulator')
_module_logger = logger

####################################################################################################

from FinancialSimulator.Accounting.FinancialPeriod import (FinancialPeriod,
                                                           AccountChartBalance, AccountBalance,
                                                           AccountBalanceSnapshot)
from FinancialSimulator.Accounting.AccountChartLoader import (load_account_chart,
                                                              load_account_chart_for_country)
from FinancialSimulator.Scheduler import Scheduler
from FinancialSimulator.Simulator.Factory import JournalEntryActionFactory
from FinancialSimulator.Simulator.YamlLoader import YamlLoader

####################################################################################################

account_chart = load_account_chart_for_country('fr')
analytic_account_chart = load_account_chart('plan-analytique.yml')

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

financial_period_class = FinancialPeriod
financial_period = financial_period_class(account_chart,
                                          analytic_account_chart,
                                          journal_definitions,
                                          start_date, stop_date)
account_chart = financial_period.account_chart
analytic_account_chart = financial_period.analytic_account_chart
journals = financial_period.journals

####################################################################################################

if True:
    from FinancialSimulator.Accounting.BackendStore.MongoDB import AccountingStore
    accounting_store = AccountingStore(drop=True)

####################################################################################################

class JournalListener:

    _logger = _module_logger.getChild('JournalListener')

    ##############################################

    def slot(self, signal, sender, **kwargs):

        journal_entry = kwargs['journal_entry']
        self._logger.info(journal_entry.to_json())
        accounting_store.write_journal_entry(journal_entry)

####################################################################################################

class ImputationListener:

    _logger = _module_logger.getChild('ImputationListener')

    ##############################################

    def slot(self, signal, sender, **kwargs):

        # self._logger.info("{} {} {}".format(str(signal), str(sender), str(kwargs)))

        imputation = sender
        account = imputation.account
        account_snapshot = AccountBalanceSnapshot(imputation, account)
        self._logger.info(account_snapshot.to_json())
        accounting_store.write_account_snapshot(imputation)

####################################################################################################

from FinancialSimulator.Accounting.Journal import Imputation, Journal

journal_listener = JournalListener()
# global
Journal.logged_entry.connect(journal_listener.slot)

imputation_listener = ImputationListener()
# global
Imputation.imputed.connect(imputation_listener.slot)

####################################################################################################

yaml_loader = YamlLoader()
yaml_files = glob.glob(os.path.join(os.path.dirname(__file__), 'transactions', '*.yml'))
for yaml_file in yaml_files:
    yaml_loader.load(yaml_file)

scheduler = Scheduler()
factory = JournalEntryActionFactory(journals)
factory.make_transaction_actions(yaml_loader, scheduler)

###################################################################################################

start_day = datetime.date(year, 1, 1)
stop_day = datetime.date(year +1, 1, 1)

# print("\nActions:")
# for planned_action in scheduler.iter(start_day, stop_day):
#     print(planned_action)

if True:
    scheduler.run(start_day, stop_day)

if False:
    from FinancialSimulator.Accounting.BackendStore.File import AccountingStore
    AccountingStore.load(financial_period, 'financial_period.json')

####################################################################################################

# journal = journals['JOD']
# print('\n' + journal.name + ':\n')
# for transaction in journal._transactions:
#     print(transaction)

####################################################################################################

if False:
    # for journal_entry in journals['JOD']:
    #     print(journal_entry.to_json())
    #     accounting_store.write_journal_entry(journal_entry)

    for journal_entry_json in accounting_store.find_journal_entry('JOD'):
        # print(journal_entry_json)
        journals['JOD'].journal_entry_from_json(journal_entry_json)

####################################################################################################

if False:
    from FinancialSimulator.Accounting.BackendStore.File import AccountingStore
    AccountingStore.save(financial_period, 'financial_period.json')

####################################################################################################

if False:
    from FinancialSimulator.Accounting.fr.FEC import FecWriter
    FecWriter().write(financial_period, 'fec.xml', encoding='utf-8')
    print(FecWriter().validate('fec.xml', 'BIC'))

####################################################################################################

if False:
    for account in account_chart:
        if account.has_imputations():
            print('{}-{} : Solde Débiteur: {} € Créditeur: {} €'.format(account.number,
                                                                        account.description,
                                                                        account.debit,
                                                                        account.credit))

####################################################################################################

if False:
    from FinancialSimulator.Accounting import Results

    # yaml_file = 'systeme-abrege-resultat-tableau.yml'
    yaml_file = 'systeme-base-bilan-tableau.yml'
    yaml_loader = Results.YamlLoader(yaml_file)
    table = yaml_loader.table

    computation_visitor = Results.ComputationVisitor(account_chart)
    for column in table:
        print('\n' + column.title)
        # computation_visitor.compute(column.node)
        for row in column:
            if not isinstance(row, Results.EmptyRow):
                title_width = 60
                title = '  '*row.level + row.title[:title_width - 2*row.level]
                value = computation_visitor[row]
                if row.show and value:
                    string_format = '{:' + str(title_width) + '} {:10.2f} €'
                    print(string_format.format(title, float(value)))
                else:
                    string_format = '{:' + str(title_width) + '}'
                    print(string_format.format(title))

####################################################################################################

if False:
    from FinancialSimulator.WebApplication.Application import create_application

    # Fixme: if DEBUG = True then reload ...
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    application = create_application(config_path, account_chart, analytic_account_chart, journals)
    application.run()

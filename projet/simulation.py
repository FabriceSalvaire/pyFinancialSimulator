####################################################################################################

import datetime
import glob
import os

####################################################################################################

import FinancialSimulator.Logging.Logging as Logging

logger = Logging.setup_logging('financial-simulator')
_module_logger = logger

####################################################################################################

from FinancialSimulator.Accounting.AccountBalanceHistory import AccountBalanceWithHistory
from FinancialSimulator.Accounting.AccountChartLoader import (load_account_chart,
                                                              load_account_chart_for_country)
from FinancialSimulator.Accounting.FinancialPeriod import (FinancialPeriod,
                                                           AccountChartBalance,
                                                           Journals)
from FinancialSimulator.Accounting.Journal import DebitImputation, CreditImputation
from FinancialSimulator.Accounting.JournalInMemory import JournalInMemory
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

class MyAccountChartBalance(AccountChartBalance):
    __account_balance_factory__ = AccountBalanceWithHistory

# class MyDebitImputation(DebitImputation):
#     def apply(self):
#         super().apply()
#         print('MyDebitImputation apply')

# class MyJournalInMemory(JournalInMemory):
#     __debit_imputation_factory__ = MyDebitImputation
#     __credit_imputation_factory__ = CreditImputation

class MyJournals(Journals):
    __journal_factory__ = JournalInMemory

class MyFinancialPeriod(FinancialPeriod):
    __account_chart_factory__ = MyAccountChartBalance
    __analytic_account_chart_factory__ = MyAccountChartBalance
    __journals_factory__ = MyJournals

financial_period_class = MyFinancialPeriod
financial_period = financial_period_class(account_chart,
                                          analytic_account_chart,
                                          journal_definitions,
                                          start_date, stop_date)
account_chart = financial_period.account_chart
analytic_account_chart = financial_period.analytic_account_chart
journals = financial_period.journals

####################################################################################################

class ImputationListener:
    def slot(self, signal, sender, **kwargs):
        imputation = sender
        imputation.account.history.save(imputation)
        if imputation.analytic_account is not None:
            imputation.analytic_account.history.save(imputation)

from FinancialSimulator.Accounting.Journal import Imputation

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

scheduler.run(start_day, stop_day)

####################################################################################################

if True:
    from FinancialSimulator.WebApplication.Application import create_application

    # Fixme: if DEBUG = True then reload ...
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    application = create_application(config_path, account_chart, analytic_account_chart, journals)
    application.run()

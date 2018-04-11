class MyAccountChartBalance(AccountChartBalance):
    __account_balance_factory__ = AccountBalanceWithHistory

class MyImputation(Imputation):
    def apply(self):
        super().apply()
        self._account.history.save(self)
        if self._analytic_account is not None:
            self._analytic_account.history.save(self)

class MyJournals(Journals):
    __journal_factory__ = Journal

class MyFinancialPeriod(FinancialPeriod):
    __account_chart_factory__ = MyAccountChartBalance
    __analytic_account_chart_factory__ = MyAccountChartBalance
    __journal_factory__ = MyJournals

financial_period_class = MyFinancialPeriod

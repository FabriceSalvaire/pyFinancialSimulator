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

from flask import current_app, Blueprint, render_template

####################################################################################################

from ..Model import model

####################################################################################################

main = Blueprint('main', __name__, url_prefix='/main')

@main.route('/')
def index():
    journals = [journal for journal in model.journals]
    journals.sort(key=lambda journal: journal.label)
    return render_template('main.html', journals=journals)

@main.route('/account_chart')
def account_chart():
    accounts = [account for account in model.account_chart if account.has_imputations()]
    return render_template('account_chart.html',
                           account_chart=model.account_chart,
                           accounts=accounts)

@main.route('/analytic_account_chart')
def analytic_account_chart():
    accounts = [account for account in model.analytic_account_chart if account.has_imputations()]
    return render_template('account_chart.html',
                           account_chart=model.analytic_account_chart,
                           accounts=accounts)

@main.route('/journal/<label>')
def journal(label):
    journal = model.journals[label]
    return render_template('journal.html', journal=journal)

####################################################################################################

from FinancialSimulator.Accounting import Results

# yaml_file = 'systeme-abrege-resultat-tableau.yml'
# yaml_file = 'systeme-base-bilan-tableau.yml'
yaml_file = 'systeme-base-resultat-tableau.yml'
yaml_loader = Results.YamlLoader(yaml_file)

@main.route('/tableau/bilan')
def result():
    account_chart = model.account_chart
    table = yaml_loader.table
    computation_visitor = table.compute(account_chart)
    return render_template('result.html', table=table, computation_visitor=computation_visitor)

####################################################################################################
#
# End
#
####################################################################################################

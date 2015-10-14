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
    accounts = [account for account in model.account_chart if account.debit or account.credit]
    return render_template(current_app.config['INDEX_TEMPLATE'], accounts=accounts)

####################################################################################################
#
# End
#
####################################################################################################
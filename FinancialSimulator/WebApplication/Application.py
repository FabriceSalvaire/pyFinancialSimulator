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

from flask import Flask

####################################################################################################

def create_application(config_path, account_chart, analytic_account_chart, journals):

    application = Flask(__name__)

    application.config.from_pyfile(config_path)
    # Fixme: right way?
    application.config['account_chart'] = account_chart
    application.config['analytic_account_chart'] = analytic_account_chart
    application.config['journals'] = journals

    from .Model import model
    model.init_app(application)

    from .Views.Main import main
    application.register_blueprint(main)

    return application

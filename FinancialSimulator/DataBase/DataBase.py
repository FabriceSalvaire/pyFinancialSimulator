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

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

####################################################################################################

from .SqlAlchemyBase import autoload_table

####################################################################################################

class DataBase:

    _logger = logging.getLogger(__name__)

    ##############################################

    def __init__(self, connection_string, echo=False):

        self._engine = create_engine(connection_string, echo=echo)
        self.session = sessionmaker(bind=self._engine)()
        self._declarative_base_class = None

    ###############################################

    def has_table(self, table_name):

        # Fixme: give acces to engine ?

        return self._engine.has_table(table_name)

    ###############################################

    def table_columns(self, table_name):

        table = autoload_table(self._engine, table_name)
        return [column.name for column in table.columns]

    ###############################################

    def table_has_columns(self, table_name, columns):

        table_columns = self.table_columns(table_name)
        for column in columns:
            if column not in table_columns:
                return False
        return True

    ###############################################

    def close_session(self):

        self.session.close()

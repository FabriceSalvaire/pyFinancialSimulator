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

from sqlalchemy import Column, Date, DateTime, Integer, BIGINT, Float, String, VARCHAR, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref

####################################################################################################

from FinancialSimulator.DataBase.MysqlDataBase import MysqlDataBase
from FinancialSimulator.DataBase.SqlAlchemyBase import SqlRow
from FinancialSimulator.DataBase.SqlAlchemyBase import SqlTable

####################################################################################################

class AccountsRowMixin(SqlRow):

    # CREATE TABLE `accounts` (
    #   `guid` varchar(32) NOT NULL,
    #   `name` varchar(2048) CHARACTER SET utf8 NOT NULL,
    #   `account_type` varchar(2048) CHARACTER SET utf8 NOT NULL,
    #   `commodity_guid` varchar(32) DEFAULT NULL,
    #   `commodity_scu` int(11) NOT NULL,
    #   `non_std_scu` int(11) NOT NULL,
    #   `parent_guid` varchar(32) DEFAULT NULL,
    #   `code` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
    #   `description` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
    #   `hidden` int(11) DEFAULT NULL,
    #   `placeholder` int(11) DEFAULT NULL
    # ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

    __tablename__ = 'accounts'

    guid = Column(VARCHAR(length=32), nullable=False, primary_key=True)
    name = Column(VARCHAR(length=2048), nullable=False)
    account_type = Column(VARCHAR(length=2048), nullable=False)
    commodity_guid = Column(VARCHAR(length=32), default='')
    commodity_scu = Column(Integer, nullable=False)
    non_std_scu = Column(Integer, nullable=False)
    parent_guid = Column(VARCHAR(length=32), default='')
    code = Column(VARCHAR(length=2048), default='')
    description = Column(VARCHAR(length=2048), default='')
    hidden = Column(Integer, default=0)
    placeholder = Column(Integer, default=0)

####################################################################################################

# CREATE TABLE `books` (
#   `guid` varchar(32) NOT NULL,
#   `root_account_guid` varchar(32) NOT NULL,
#   `root_template_guid` varchar(32) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

####################################################################################################

# CREATE TABLE `commodities` (
#   `guid` varchar(32) NOT NULL,
#   `namespace` varchar(2048) CHARACTER SET utf8 NOT NULL,
#   `mnemonic` varchar(2048) CHARACTER SET utf8 NOT NULL,
#   `fullname` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
#   `cusip` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
#   `fraction` int(11) NOT NULL,
#   `quote_flag` int(11) NOT NULL,
#   `quote_source` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
#   `quote_tz` varchar(2048) CHARACTER SET utf8 DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

# CREATE TABLE `prices` (
#   `guid` varchar(32) NOT NULL,
#   `commodity_guid` varchar(32) NOT NULL,
#   `currency_guid` varchar(32) NOT NULL,
#   `date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
#   `source` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
#   `type` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
#   `value_num` bigint(20) NOT NULL,
#   `value_denom` bigint(20) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

####################################################################################################

class SlotsRowMixin(SqlRow):

    # CREATE TABLE `slots` (
    #   `id` int(11) NOT NULL,
    #   `obj_guid` varchar(32) NOT NULL,
    #   `name` varchar(4096) CHARACTER SET utf8 NOT NULL,
    #   `slot_type` int(11) NOT NULL,
    #   `int64_val` bigint(20) DEFAULT NULL,
    #   `string_val` varchar(4096) CHARACTER SET utf8 DEFAULT NULL,
    #   `double_val` double DEFAULT NULL,
    #   `timespec_val` timestamp NULL DEFAULT '0000-00-00 00:00:00',
    #   `guid_val` varchar(32) DEFAULT NULL,
    #   `numeric_val_num` bigint(20) DEFAULT NULL,
    #   `numeric_val_denom` bigint(20) DEFAULT NULL,
    #   `gdate_val` date DEFAULT NULL
    # ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

    # obj_guid -> transactions

    __tablename__ = 'slots'

    # Fixme
    id = Column(Integer, nullable=False, primary_key=True)
    obj_guid = Column(VARCHAR(length=32), nullable=False)
    name = Column(VARCHAR(length=32), nullable=False)
    slot_type = Column(Integer, nullable=False)
    int64_val = Column(BIGINT, default=0)
    string_val = Column(VARCHAR(length=4096), default='')
    double_val = Column(Float, default=.0) # double
    timespec_val = Column(TIMESTAMP)
    guid_val = Column(VARCHAR(length=32), default='')
    numeric_val_num = Column(BIGINT, default=0)
    numeric_val_denom = Column(BIGINT, default=0)
    gdate_val = Column(Date)

####################################################################################################

class SplitsRowMixin(SqlRow):

    # CREATE TABLE `splits` (
    #   `guid` varchar(32) NOT NULL,
    #   `tx_guid` varchar(32) NOT NULL,
    #   `account_guid` varchar(32) NOT NULL,
    #   `memo` varchar(2048) CHARACTER SET utf8 NOT NULL,
    #   `action` varchar(2048) CHARACTER SET utf8 NOT NULL,
    #   `reconcile_state` varchar(1) CHARACTER SET utf8 NOT NULL,
    #   `reconcile_date` timestamp NULL DEFAULT '0000-00-00 00:00:00',
    #   `value_num` bigint(20) NOT NULL,
    #   `value_denom` bigint(20) NOT NULL,
    #   `quantity_num` bigint(20) NOT NULL,
    #   `quantity_denom` bigint(20) NOT NULL,
    #   `lot_guid` varchar(32) DEFAULT NULL
    # ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

     # 2 splits per transaction

    __tablename__ = 'splits'

    guid = Column(VARCHAR(length=32), nullable=False, primary_key=True)
    account_guid = Column(VARCHAR(length=32), nullable=False)
    memo = Column(VARCHAR(length=2048), nullable=False)
    action = Column(VARCHAR(length=2048), nullable=False)
    reconcile_state = Column(VARCHAR(length=1), nullable=False)
    reconcile_date = Column(TIMESTAMP)
    value_num = Column(BIGINT, nullable=False)
    value_denom = Column(BIGINT, nullable=False)
    quantity_num = Column(BIGINT, nullable=False)
    quantity_denom = Column(BIGINT, nullable=False)
    lot_guid = Column(VARCHAR(length=32), default='')

    ##############################################

    @declared_attr
    def tx_guid(cls):
        return Column(VARCHAR(length=32), ForeignKey('transactions.guid'))

    ##############################################

    @declared_attr
    def transactions(cls):
        return relationship('TransactionsRow',
                            primaryjoin='TransactionsRow.guid==%s.tx_guid' % cls.__name__)

    ##############################################

    @property
    def value(self):
        return self.value_num / self.value_denom

    ##############################################

    @property
    def quantity(self):
        return self.quantity_num / self.quantity_denom

####################################################################################################

class TransactionsRowMixin(SqlRow):

    # CREATE TABLE `transactions` (
    #   `guid` varchar(32) NOT NULL,
    #   `currency_guid` varchar(32) NOT NULL,
    #   `num` varchar(2048) CHARACTER SET utf8 NOT NULL,
    #   `post_date` timestamp NULL DEFAULT '0000-00-00 00:00:00',
    #   `enter_date` timestamp NULL DEFAULT '0000-00-00 00:00:00',
    #   `description` varchar(2048) CHARACTER SET utf8 DEFAULT NULL
    # ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

    __tablename__ = 'transactions'

    guid = Column(VARCHAR(length=32), nullable=False, primary_key=True)
    currency_guid = Column(VARCHAR(length=32), nullable=False)
    num = Column(VARCHAR(length=2048), nullable=False)
    post_date = Column(TIMESTAMP) # default=None
    enter_date = Column(TIMESTAMP) # default=None
    description = Column(VARCHAR(length=2048), default='')

    ##############################################

    @declared_attr
    def splits(cls):
        return relationship('SplitsRow',
                            primaryjoin="SplitsRow.tx_guid==%s.guid" % cls.__name__)

####################################################################################################

class GnucashDataBase(MysqlDataBase):

    ##############################################

    def __init__(self, database_config, echo=False):

        super().__init__(database_config, echo)

        self._declarative_base_class = declarative_base()

        self._accounts_row_class = type('AccountsRow', (AccountsRowMixin, self._declarative_base_class), {})
        self._accounts_table_class = type('AccountsTable', (SqlTable,), {'ROW_CLASS':self._accounts_row_class})
        self.accounts_table = self._accounts_table_class(self)

        self._slots_row_class = type('SlotsRow', (SlotsRowMixin, self._declarative_base_class), {})
        self._slots_table_class = type('SlotsTable', (SqlTable,), {'ROW_CLASS':self._slots_row_class})
        self.slots_table = self._slots_table_class(self)

        self._splits_row_class = type('SplitsRow', (SplitsRowMixin, self._declarative_base_class), {})
        self._splits_table_class = type('SplitsTable', (SqlTable,), {'ROW_CLASS':self._splits_row_class})
        self.splits_table = self._splits_table_class(self)

        self._transactions_row_class = type('TransactionsRow', (TransactionsRowMixin, self._declarative_base_class), {})
        self._transactions_table_class = type('TransactionsTable', (SqlTable,), {'ROW_CLASS':self._transactions_row_class})
        self.transactions_table = self._transactions_table_class(self)

        # if self.create():
        #     pass

####################################################################################################
#
# End
#
####################################################################################################

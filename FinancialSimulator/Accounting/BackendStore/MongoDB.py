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

import pymongo
from pymongo import MongoClient

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class DatabaseConfig:

    host = 'localhost'
    port = 27017
    database = 'financial_simulator'

####################################################################################################

class DocumentExistsError(Exception):
    pass

class DocumentDontExistsError(Exception):
    pass

####################################################################################################

class AccountingStore:

    ##############################################

    def __init__(self, database_config=DatabaseConfig):

        self._client = MongoClient(database_config.host, database_config.port)
        self._db = self._client[database_config.database]

    ##############################################

    def collection_for_journal_entry(self, journal_entry):

        journal = journal_entry.journal.label
        return self._db.journals[journal]

    ##############################################

    def key_document_for_journal_entry(self, journal_entry):

        document = journal_entry.to_json()
        key = {'sequence_number': document['sequence_number']}
        
        return key, document

    ##############################################

    def write_journal_entry(self, journal_entry):

        collection = self.collection_for_journal_entry(journal_entry)
        key, document = self.key_document_for_journal_entry(journal_entry)
        if not collection.find_one(key):
            result = collection.insert_one(document)
            # insert_many
            # result.inserted_id
        else:
            raise DocumentExistsError

   ##############################################

    def update_journal_entry(self, journal_entry):

        collection = self.collection_for_journal_entry(journal_entry)
        key, document = self.key_document_for_journal_entry(journal_entry)
        result = collection.update(key, document)
        # .modified_count
        if result.matched_count != 1:
            raise DocumentDontExistsError

   ##############################################

    def find_journal_entry(self, journal, **kwargs):

        # find by sequence_number, etc.
        # <= date <=, amount etc.

        collection = self._db.journals[journal]

        cursor = collection.find(**kwargs)
        cursor = cursor.sort([
            ('sequence_number', pymongo.ASCENDING),
        ])
        
        for journal_entry in cursor:
            yield journal_entry

####################################################################################################
#
# End
#
####################################################################################################

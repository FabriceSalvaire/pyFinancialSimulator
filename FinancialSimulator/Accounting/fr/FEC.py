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
import os

from lxml import etree

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class FecWriter(object):

    ##############################################

    def validate(self, path, schema):

        document = etree.parse(path)
        schema_path = os.path.join(os.path.dirname(__file__), 'fec', schema + '.xsd')
        xmlschema_document = etree.parse(schema_path)
        xmlschema = etree.XMLSchema(xmlschema_document)
        return xmlschema.validate(document)

    ##############################################

    def write(self, financial_period, path, encoding='iso-8859-1'):

        with etree.xmlfile(path,
                           encoding=encoding,
                           compression=None,
                           close=True,
                           buffered=True) as xf:
            xf.write_declaration() # standalone=True
            with xf.element('comptabilite'):
                with xf.element('exercice'):
                    with xf.element('DateCloture'):
                        xf.write(financial_period.start_date.isoformat())
                    for journal in financial_period.journals:
                        self._write_journal(xf, journal)

    ##############################################

    def _write_journal(self, xf, journal):

        with xf.element('journal'):
            with xf.element('JournalCode'):
                xf.write(journal.label)
            with xf.element('JournalLib'):
                xf.write(journal.description)
            for entry in journal:
                self._write_entry(xf, entry)

    ##############################################

    def _write_entry(self, xf, entry):

        with xf.element('ecriture'):
            with xf.element('EcritureNum'):
                xf.write(str(entry.sequence_number))
            with xf.element('EcritureDate'):
                xf.write(entry.date.isoformat())
            with xf.element('EcritureLib'):
                xf.write(entry.description)
            with xf.element('PieceRef'):
                xf.write('FA-1') # entry.document.number
            with xf.element('PieceDate'):
                xf.write('2016-01-01') # entry.document.date.isoformat()
            with xf.element('EcritureLet'):
                xf.write('L1') # entry.reconciliation_id)
            with xf.element('DateLet'):
                xf.write('2016-01-01') # entry.reconciliation_date.isoformat()
            with xf.element('ValidDate'):
                xf.write(entry.validation_date.isoformat())
            
            for iterator, name in ((entry.debits, 'Debit'),
                                   (entry.credits, 'Credit'),
            ):
                for imputation in iterator:
                    with xf.element('ligne'):
                        with xf.element('CompteNum'):
                            number = str(imputation.account.number)
                            l = 3 - len(number)
                            if l:
                                number += '0' * l
                            xf.write(number)
                        with xf.element('CompteLib'):
                            xf.write(imputation.account.description)
                        with xf.element(name):
                            xf.write(str(imputation.amount))
            xf.flush()

    ##############################################

    # writer = self._writer(path, encoding)
    # next(w)
    # for i in range(10):
    #     el = etree.Element("item")
    #     el.text = 'foobar'
    #     w.send(el)
    # w.close()

    ##############################################

    # def _writer(self, path, encoding):

    # try:
    #     while True:
    #         el = (yield)
    #         xf.write(el, pretty_print=True)
    #         xf.flush()
    # except GeneratorExit:
    #     pass

####################################################################################################
#
# End
#
####################################################################################################

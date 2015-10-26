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

import datetime
import logging

from lxml import etree

####################################################################################################

from FinancialSimulator.IdentificationNumber.Bank import BankAccountNumber
from .BankStatement import BankStatement

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# CREDIT      | Generic credit
# DEBIT       | Generic debit
# INT         | Interest earned or paid / Note: Depends on signage of amount
# DIV         | Dividend
# FEE         | FI fee
# SRVCHG      | Service charge
# DEP         | Deposit
# ATM         | ATM debit or credit / Note: Depends on signage of amount
# POS         | Point of sale debit or credit / Note: Depends on signage of amount
# XFER        | Transfer
# CHECK       | Check
# PAYMENT     | Electronic payment
# CASH        | Cash withdrawal
# DIRECTDEP   | Direct deposit
# DIRECTDEBIT | Merchant initiated debit
# REPEATPMT   | Repeating payment/standing order
# OTHER       | Other

# DIRECTDEP: + virement
# PAYMENT: - prélévement
# DEBIT: - cotisation
# POS: - achat
# CREDIT: + CREDIT CARTE BANCAIRE
# CHECK: +/- chèque
# DEP: + remise de chèques

_transaction_type_translator = {
    'CREDIT': 'generic credit',
    'DEBIT': 'generic debit',
    'INT': 'interest',
    'DIV': 'dividend',
    'FEE': 'fee',
    'SRVCHG': 'Service charge',
    'DEP': 'deposit',
    'ATM': 'atm',
    'POS': 'bank card',
    'XFER': 'transfer',
    'CHECK': 'check',
    'PAYMENT': 'electronic payment',
    'CASH': 'cash withdrawal',
    'DIRECTDEP': 'direct deposit',
    'DIRECTDEBIT': 'direct debit',
    'REPEATPMT': 'repeating payment',
    'OTHER': 'other',
}

####################################################################################################

class OfxSgmlParserError(Exception):
    pass

####################################################################################################

class OfxSgmlParser(object):

    ##############################################

    def parse(self, ofx_path):

        with open(ofx_path) as f:
            source = f.read()

        header_data, location = self._parse_header(source)
        if header_data['DATA'] != 'OFXSGML':
            raise NameError("Unsupported OFX")

        xml_source = self._to_xml(source[location:])
        tree = etree.fromstring(xml_source)
        statement_ressource = self._get_xpath_element(tree, '/OFX/BANKMSGSRSV1/STMTTRNRS/STMTRS')

        bank_account = self._get_xpath_element(statement_ressource, 'BANKACCTFROM')
        bank_id = self._get_xpath_int(bank_account, 'BANKID')
        branch_id = self._get_xpath_int(bank_account, 'BRANCHID')
        account_id = self._get_xpath_text(bank_account, 'ACCTID')
        key = self._get_xpath_int(bank_account, 'ACCTKEY')
        bank_account_number = BankAccountNumber(bank_id, branch_id, account_id, key)
        
        # or AVAILBAL
        balance_element = self._get_xpath_element(statement_ressource, 'LEDGERBAL')
        balance = self._get_xpath_float(balance_element, 'BALAMT')
        balance_date = self._get_xpath_date(balance_element, 'DTASOF')
        
        bank_statement = BankStatement(bank_account_number, balance_date, balance)
        
        transaction_list = self._get_xpath_element(statement_ressource, 'BANKTRANLIST')
        transactions = transaction_list.xpath('STMTTRN')
        for transaction in transactions:
            type_ = ''
            date = None
            amount = None
            description = ''
            for element in transaction:
                tag = element.tag
                text = element.text
                if tag == 'TRNTYPE':
                    type_ = _transaction_type_translator[text]
                elif tag == 'DTPOSTED':
                    date = self._parse_date(text)
                elif tag == 'TRNAMT':
                    amount = float(text) # signed
                elif tag == 'NAME':
                    description = text
            bank_statement.add_transaction(date, description, amount, type_)
        
        return bank_statement

    ##############################################

    def _parse_header(self, source):

        location = source.find('<')
        if not location:
            raise OfxSgmlParserError
        header_source = source[:location]
        
        header_data = {}
        for line in header_source.split():
            line = line.strip()
            if line.startswith('<'):
                break
            else:
                key, value = line.split(':')
                header_data[key] = value
        
        return header_data, location

    ##############################################

    def _to_xml(self, source):

        """Convert SGML to a valid XML document (add close tags)"""

        xml_source = '<?xml version="1.0"?>\n'
        location = 0
        element_stack = []
        while location < len(source):
            start = source.find('<', location)
            stop = source.find('>', start)
            element = source[start+1:stop]
            if element.startswith('/'):
                close = True
                element = element[1:]
            else:
                close = False
            has_data = location < start
            if element_stack:
                current_element = element_stack[-1]
            else:
                current_element = None
            if has_data:
                xml_source += source[location:start]
                if current_element is not None and current_element != element: # and close
                    xml_source += '</' + current_element + '>\n'
                    element_stack.pop()
            if close:
                xml_source += '</' + element + '>\n'
                element_stack.pop()
            else:
                if xml_source and xml_source[-1] != '\n':
                    xml_source += '\n'
                xml_source += '<' + element + '>'
                element_stack.append(element)
            location = stop +1

        return xml_source

    ##############################################

    def _parse_date(self, text):

        return datetime.date(int(text[:4]), int(text[4:6]), int(text[6:8]))

    ##############################################

    def _get_xpath_element(self, root, path):

        return root.xpath(path)[0]

    ##############################################

    def _get_xpath_text(self, root, path):

        return self._get_xpath_element(root, path).text

    ##############################################

    def _get_xpath_int(self, root, path):

        return int(self._get_xpath_text(root, path))

    ##############################################

    def _get_xpath_float(self, root, path):

        return float(self._get_xpath_text(root, path))

    ##############################################

    def _get_xpath_date(self, root, path):

        return self._parse_date(self._get_xpath_text(root, path))

####################################################################################################
#
# End
#
####################################################################################################

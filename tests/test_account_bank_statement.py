# This file is part of the account_bank_statement module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountBankStatementTestCase(ModuleTestCase):
    'Test Account Bank Statement module'
    module = 'account_bank_statement'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountBankStatementTestCase))
    return suite
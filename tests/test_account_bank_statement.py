# This file is part of the account_bank_statement module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import doctest_setup, doctest_teardown


class AccountBankStatementTestCase(ModuleTestCase):
    'Test Account Bank Statement module'
    module = 'account_bank_statement'


def suite():
    suite = trytond.tests.test_tryton.suite()
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
#        AccountBankStatementTestCase))
    suite.addTests(doctest.DocFileSuite('scenario_bank_statement.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    suite.addTests(doctest.DocFileSuite(
            'scenario_bank_statement_different_currency.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite

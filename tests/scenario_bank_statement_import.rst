========================================
Account Bank Statement ES CSB43 Scenario
========================================

Imports::

    >>> import datetime
    >>> import os
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard, Report
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> today = datetime.date.today()
    >>> now = datetime.datetime.now()

Activate account_bank_statement_es_csb43 module::

    >>> config = activate_modules('account_bank_statement')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = create_fiscalyear(company)
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> payable = accounts['payable']
    >>> cash = accounts['cash']
    >>> cash.bank_reconcile = True
    >>> cash.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create Journal::

    >>> Sequence = Model.get('ir.sequence')
    >>> sequence = Sequence(name='Bank', code='account.journal',
    ...     company=company)
    >>> sequence.save()
    >>> AccountJournal = Model.get('account.journal')
    >>> account_journal = AccountJournal(name='Statement',
    ...     type='cash',
    ...     sequence=sequence)
    >>> account_journal.save()

Create Statement Journal::

    >>> StatementJournal = Model.get('account.bank.statement.journal')
    >>> statement_journal = StatementJournal(name='Test',
    ...     journal=account_journal, currency=company.currency, account=cash)
    >>> statement_journal.save()

Create Bank Statement::

    >>> BankStatement = Model.get('account.bank.statement')
    >>> StatementLine = Model.get('account.bank.statement.line')

    >>> statement = BankStatement(journal=statement_journal, date=now)
    >>> statement.save()
    >>> statement.reload()

Import CSB43 file::

    >>> csv_file = os.path.join(os.path.dirname(__file__), 'file.csv')
    >>> wizard = Wizard('account.bank.statement.import', [statement])
    >>> wizard.form.import_file = open(csv_file, 'rb').read()
    >>> wizard.form.type = 'csv'
    >>> wizard.form.confirm = True
    >>> wizard.execute('import_file')
    >>> statement.reload()
    >>> len(statement.lines)
    2

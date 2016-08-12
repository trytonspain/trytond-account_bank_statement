===============================
Account Bank Statement Scenario
===============================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()
    >>> now = datetime.datetime.now()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_bank_statement and account_invoice::

    >>> Module = Model.get('ir.module')
    >>> modules = Module.find([
    ...         ('name', 'in', ('account_bank_statement',
    ...             'account_invoice')),
    ...     ])
    >>> for module in modules:
    ...     module.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']
    >>> cash.bank_reconcile = True
    >>> cash.save()

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

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
    ...     credit_account=cash,
    ...     debit_account=cash,
    ...     sequence=sequence)
    >>> account_journal.save()

Create Statement Journal::

    >>> StatementJournal = Model.get('account.bank.statement.journal')
    >>> statement_journal = StatementJournal(name='Test',
    ...     journal=account_journal, currency=company.currency)
    >>> statement_journal.save()

Create Bank Move::

    >>> period = fiscalyear.periods[0]
    >>> Move = Model.get('account.move')
    >>> move = Move()
    >>> move.period = period
    >>> move.journal = account_journal
    >>> move.date = period.start_date
    >>> line = move.lines.new()
    >>> line.account = cash
    >>> line.credit = Decimal('80.0')
    >>> line2 = move.lines.new()
    >>> line2.account = receivable
    >>> line2.debit = Decimal('80.0')
    >>> line2.party = party
    >>> move.click('post')
    >>> move.state
    u'posted'

Create Bank Statement With Different Curreny::

    >>> BankStatement = Model.get('account.bank.statement')
    >>> statement = BankStatement(journal=statement_journal, date=now)

Create Bank Statement Lines::

    >>> StatementLine = Model.get('account.bank.statement.line')
    >>> statement_line = StatementLine()
    >>> statement.lines.append(statement_line)
    >>> statement_line.date = now
    >>> statement_line.description = 'Statement Line'
    >>> statement_line.amount = Decimal('80.0')
    >>> statement_line.party = party
    >>> statement.click('confirm')
    >>> statement.state
    u'confirmed'
    >>> statement_line = StatementLine(1)
    >>> statement_line.state
    u'confirmed'

Select statement move to reconcile statement line::

    >>> MoveLine = Model.get('account.move.line')
    >>> line = MoveLine(1)
    >>> BankLine = Model.get('account.bank.reconciliation')
    >>> bank_line, = BankLine.find([])
    >>> bank_line.amount = Decimal('80.0')
    >>> bank_line.bank_statement_line = statement_line
    >>> bank_line.save()
    >>> bank_line.reload()
    >>> statement_line.save()
    >>> statement_line.reload()
    >>> statement_line.moves_amount
    Decimal('80.00')
    >>> statement_line.company_amount
    Decimal('80.00')

Post line::

    >>> statement_line.click('post')
    >>> statement_line.state
    u'posted'

Cancel line::

    >>> statement_line.click('cancel')
    >>> statement_line.state
    u'canceled'
    >>> statement_line.bank_lines
    []

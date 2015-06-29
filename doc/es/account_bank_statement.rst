*********************
Conciliación bancaria
*********************

La conciliación bancaria consiste en el cuadre de la información que nos
facilita nuestra entidad bancaria con la información indicada por nuestra
cuenta 572x correspondiente a la cuenta bancaria a conciliar. Esta
funcionalidad nos permiten que el cuadre de los bancos, que es una de las
tareas más frecuentes en las empresas, sea un trabajo realmente sencillo y
rápido, minimizando errores. Vale la pena, pues, aprender en profundidad esta
sección.

En primer lugar veremos cómo configurar el sistema para poder realizar
correctamente la conciliación bancaria; seguidamente veremos cómo gestionar,
crear o importar extractos bancarios y por último trataremos la contabilización
y conciliación bancaria en sí. Para ello tendremos que tener presente los
conceptos del sistema *Extractos bancarios* (el extracto propiamente dicho) y
*Líneas de extracto bancario* (que representarán cada uno de los movimientos
del extracto bancario).

Configuración
=============

Como hemos comentado, el primer paso será ajustar el sistema a nuestras
necesidades, para ello deberemos crear un *Diario de extractos bancarios*
(tendremos que crear uno para cada cuenta bancaria que tengamos). Esto lo
haremos accediendo al menú |menu_st_jornal| y tras clicar en *Nuevo* nos
aparecerá el formulario que deberemos rellenar para crear el *Diario de
extracto bancario*. Los campos que rellenaremos son:

* |name_journal|: Nombre por el que identificaremos el diario de extracto.
  Debemos poner un texto que nos permita identificar fácilmente la cuenta
  bancaria a la que se refiere el extracto.

* |currency_journal|: Moneda en la que se reflejan los importes de nuestra
  cuenta bancaria.

* |journal_journal|: Diario contable en el que se pondrán los apuntes creados a
  partir del diario de extracto bancario. Este diario debe ser de tipo efectivo
  y se utilizaran sus cuentas *haber* y *debe* por defecto para las
  contrapartidas de las conciliaciones en apuntes existentes.

* |company_journal|: Indicaremos en cual de nuestras empresas realizaremos los
  apuntes contables del extracto.

Gestión de extractos
====================

Una vez creado el *Diario de extractos bancarios* ya podremos proceder a la
gestión de los extractos accediendo al menú |menu_statements|. Desde allí
podemos crear nuevos extractos bancarios e introducir todas sus líneas, una
por cada movimiento del extracto. Los campos |start_date_statement|,
|end_date_statement|, |start_balance_statement| y |end_balance_statement| no se
tienen en cuenta en el proceso, aunque es recomendable rellenar estos campos a
nivel informativo. Cuando generemos una nueva línea de extracto, los campos que
deberemos rellenar serán:

.. inheritref:: account_bank_statement/account_bank_statement:bullet_list:campos

* |description_line|: Aquí deberemos introducir la información sobre el origen
  o el motivo del movimiento bancario.

* |company_amount_line|: El importe del movimiento con la divisa con la que
  trabaja la empresa, este campo nos será útil cuando la cuenta bancaria
  corresponda a una cuenta extranjera que trabaje con una divisa diferente.

* |amount_line|: Importe de la línea de extracto en la moneda propia (en caso
  de que sea diferente al de la empresa).

* |company_moves_amount|: En este campo se indicará el importe de las
  contrapartidas que se asocien con la línea de extracto. Solo podremos
  conciliar y contabilizar las líneas del extracto cuando el
  |company_moves_amount| sea igual al importe de la línea.

Un extracto bancario puede estar en tres estados diferentes: *Borrador*,
*Confirmado* y *Cancelado*. Cuando estemos introduciendo manualmente un
extracto y sus correspondientes líneas, tanto el extracto como las líneas
quedarán en estado *Borrador*, una vez tengamos toda la información introducida
tendremos que clicar en el botón *Confirmar* del extracto y, tanto el extracto
como las líneas que lo componen, quedarán en estado confirmado.

.. inheritref:: account_bank_statement/account_bank_statement:paragraph:importacion_csb43

Si queremos borrar un extracto bancario ya introducido, primero de todo
deberemos borrar todas las líneas que lo componen, y para ello deberemos
cambiar el estado de cada línea a *Cancelado* y una vez esté la línea en estado
*Cancelado* ya podremos borrar la línea. Cuando tengamos todas las líneas del
extracto borradas, podremos borrar el extracto en sí.

.. inheritref:: account_bank_statement/account_bank_statement:section:buscar

Conciliación bancaria y contabilización de las líneas
=====================================================

Para conciliar o contabilizar líneas de extracto bancario deberemos acceder a
|menu_line_statememt|, donde nos aparecerán todas las líneas de todos los
extractos que hayamos introducido divididas en pestañas según el estado de cada
línea. Para contabilizar cada línea, deberemos entrar en cada una de las líneas
de la pestaña *Confirmado* y rellenar el campo que corresponda según cómo
queramos contabilizar la línea en concreto. Después deberemos clicar en en
*Contabilizar* y el estado de la línea cambiará a *Contabilizado*. Las opciones
que tenemos para contabilizar una línea son:

.. inheritref:: account_bank_statement/account_bank_statement:bullet_list:concile

* |bank_lines|: Si previamente a la introducción del extracto, hemos realizado
  manualmente el pago o cobro de un importe, en este campo deberemos seleccionar
  el apunte correspondiente a dicho pago o cobro de la cuenta 572x, esto lo
  haremos clicando en el icono "+" y seleccionando el apunte en cuestión entre
  los que se nos ofrecerán.

.. inheritref:: account_bank_statement/account_bank_statement:section:ejemplos

Ejemplos prácticos de conciliación
==================================

Conciliación bancaria con extractos en divisa extrajera
*******************************************************

**Tryton** nos permite contabilizar extractos bancarios con una moneda distinta
a la que utilizamos para realizar nuestra contabilidad. Para ello, previamente,
tendremos que haber creado un diario de extracto y un diario de extracto
bancario configurados con la moneda extranjera. En estos diarios los importes
se reflejarán en la moneda extrajera, pero en el diario contable asociado,
los importes ya se reflejarán en la moneda de la empresa.

.. note:: Si creamos una cuenta contable en el grupo 572 para la cuenta
   extranjera, en el campo |second_currency| podemos indicar la moneda
   extranjera con la que trabajará el banco. Con ello cada vez que accedamos
   a un extracto de la cuenta se nos habilitará una columna nueva donde se
   indicará a modo informativo el valor en la divisa secundaria para cada
   apunte.

Cuando se realiza una venta en moneda extrajera, durante todo el proceso los
importes se indican en la moneda extranjera. En el momento en el que la venta
se procesa (y se genera la factura) se realiza el primer cambio según la tasa
de ese momento y a partir de este punto, a parte de los importes en moneda
extranjera, que siempre vienen indicados, aparecen también el precio en euros.

Una vez se realiza el pago, y este se procesa en el sistema, se hace un apunte
en el diario de extracto en la moneda extranjera y otro con el importe con
la moneda de la empresa en el diario contable que tiene asociado el diario de
extracto, así como en la cuenta contable que tenga asociada. Para realizar esto
el sistema realiza de nuevo el cambio de divisas con la tasa en el momento del
pago. (Para ver como contabilizar las diferencias de cambio entre el  momento
de la venta y el pago podemos ver :ref:`diferencias de cambio`.

En el momento de hacer la conciliación bancaria, a la hora de introducir las
líneas en el campo |amount_line| tendremos que hacerlo con la moneda extranjera.
Una vez introducidas las líneas y guardado el extracto, si volvemos a acceder
de nuevo a cualquier línea (o si accedemos por medio de |menu_line_statememt|)
podremos ver que de forma automática se ha rellenado el campo
|company_moves_amount| indicando la equivalencia en la moneda de la empresa,
por lo que en la vista de edición de cada línea nos vendrá indicado el importe
en las dos divisas.

.. |menu_st_jornal| tryref:: account_bank_statement.menu_bank_statement_journal_form/complete_name
.. |name_journal| field:: account.bank.statement.journal/name
.. |currency_journal| field:: account.bank.statement.journal/currency
.. |journal_journal| field:: account.bank.statement.journal/journal
.. |company_journal| field:: account.bank.statement.journal/company
.. |menu_statements| tryref:: account_bank_statement.menu_bank_statements/complete_name
.. |start_date_statement| field:: account.bank.statement/start_date
.. |end_date_statement| field:: account.bank.statement/end_date
.. |start_balance_statement| field:: account.bank.statement/start_balance
.. |end_balance_statement| field:: account.bank.statement/end_balance
.. |description_line| field:: account.bank.statement.line/description
.. |company_amount_line| field:: account.bank.statement.line/company_amount
.. |amount_line| field:: account.bank.statement.line/amount
.. |company_moves_amount| field:: account.bank.statement.line/company_moves_amount
.. |bank_lines| field:: account.bank.statement.line/bank_lines
.. |menu_line_statememt| tryref:: account_bank_statement.menu_account_bank_statement_line/complete_name
.. |second_currency| field:: account.account/second_currency
.. |menu_statement| tryref:: account_bank_statement.menu_open_reconcile_bank_lines/complete_name
.. |menu_line_statememt| tryref:: account_bank_statement.menu_account_bank_statement_line/complete_name
.. |company_moves_amount| field:: account.bank.statement.line/company_moves_amount
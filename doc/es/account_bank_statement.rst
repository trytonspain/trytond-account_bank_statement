
En **Tryton** hablaremos de dos tipos de conciliación:

 · La *conciliación bancaria* consistente en el cuadre de la información que nos
 facilita nuestra entidad bancaria con la información indicada por nuestra
 cuenta 572x correspondiente a la cuenta bancaria a conciliar. Esta 
 funcionalidad nos permite que el cuadre de los bancos, que es una de las  
 tareas  más frecuentes en las empresas, sea un trabajo realmente sencillo y  
 rápido,  minimizando errores. Vale la pena, pues, aprender en profundidad esta
 sección.
 . La *contable* consistente en punteo o correspondencia entre las deudas 
 emitidas normalmente por facturas con los pagos o cobros de las mismas.

En primer lugar veremos cómo configurar el sistema para poder realizar
correctamente la conciliación bancaria; seguidamente veremos cómo gestionar,
crear o importar extractos bancarios y por último trataremos la contabilización
y conciliación bancaria en sí. Para ello tendremos que tener presente los
conceptos del sistema *Extractos bancarios* (el extracto propiamente dicho) y
*Líneas de extracto bancario* (que representarán cada uno de los movimientos
del extracto bancario).

Los extractos bancarios nos permiten importar los ficheros de movimientos de 
nuestras cuentas bancarias y completar nuestra contabilidad con la información 
obtenida de los bancos. Las opciones que podemos realizar son las siguientes:

 1. **Conciliar el banco con apuntes existentes en la cuenta572x**.Por ejemplo 
    porque hemos ya contabilizado manualmente el movimiento del banco en la 
    cuenta 572.

 2. **Crear nuevos apuntes contables**. Por ejemplo, para entrar las comisiones 
    que nuestro banco nos cobra por su magnifica gestión
 
 3. **Conciliar efectos existentes**. Por ejemplo, cuando el cliente nos 
    realiza una  transferencia para realizar el pago de una factura.
 
 4. **Conciliar remesas (Grupos de pago)**. Útil para conciliar todos los 
    apuntes  relacionados con un grupo de pago que hemos generado nosotros 
    mismos desde el  sistema.

Cuando realizamos la importación de un fichero desde nuestro banco, el sistema 
se encargarà de buscar apuntes existentes y grupos de pago que tengan el mismo 
importe que la línea que se está importando. Así, después de importar el 
fichero el sistema nos propondrá aquellos movimientos que cuadren con las líneas 
que estamos importando y nosotros sólo tendremos que repasarlas y confirmarlas.

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

* |currency_journal|: Moneda en la que se hacen referencia los importes del 
  extracto. Normalmente serà la misma moneda en la que tenemos nuestra cuenta 
  bancaria.

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

Aunque es posible introducir las líneas del banco manualmente, recomendamos 
utilizar la importación de ficheros para agilizar este proceso. Para importar 
un 
fichero debemos crear un nuevo extracto y utilizar la acción **Importación** 
**CSB 43**.
.. Al realizar esta acción se nos abrà la siguiente ventana: (imagen del 
   fichero CSB 43)

En esta pantalla debemos introducir el fichero que nos proporcione nuestro 
banco 
y seleccionar la opción *importar archivo*. Una vez finalizado el proceso el 
extracto nos aparecerà como confirmado. Las líneas que tienen el campo 
*Conciliado* como marcado se corresponden con aquellas que el sistema ha 
encontrado una contrapartida. Podemos utilizar el botón contabilizar para que 
se nos creen los movimientos contables correspondientes con esta línea.
.. (Imagen de extracto bancario y las líneas)

.. inheritref:: account_bank_statement/account_bank_statement:paragraph:borrar

Si queremos borrar un extracto bancario ya introducido, primero de todo
deberemos borrar todas las líneas que lo componen, y para ello deberemos
cambiar el estado de cada línea a *Cancelado* y una vez esté la línea en estado
*Cancelado* ya podremos borrar la línea. Cuando tengamos todas las líneas del
extracto borradas, podremos borrar el extracto en sí.

.. inheritref:: account_bank_statement/account_bank_statement:section:buscar

Botón Buscar 
============

El botón buscar se encargará de buscar apuntes y/o remesas que se correspondan 
con la línea actual. Para esta búsqueda se utiliza el importe pendiente de 
conciliar, que se trata de la diferència entre el importe de la línea i el 
importe de los movimientos. La búsqueda se realiza en los siguientes pasos:

 1. Efectos: Si se encuentra un efecto pendiente de conciliar del mismo importe 
    que el importe pendiente se añadirá a los efectos pendientes y se parará la 
    búsqueda. 

 2. Remesas: Se buscarán remesas del mismo importe que la línea de movimientos. 
    En caso de encontrar una remesa se añadirán los siguientes objectos: 
  
  a. Un efecto para cada línea de la remesa que esté totalmente pagado (el 
     importe del pago sea el mismo que el importe de la línea de remesa)
  
  b. Una transacción para cada línea de remesa que se corresponda con el pago 
     parcial de un efecto. Se utilizarà como importe de la transacción el 
     importe del pago y como cuenta la misma cuenta del efecto.
  
  c. Una transacción para cada línea de remesa que no se corresponda con un 
     efecto, utilizando la cuenta a cobrar/pagar del tercero como cuenta y el 
     importe del pago como importe.

Podemos utilizar el botón buscar tantas veces como creamos conveniente. 

.. Note:: Durante la importación de ficheros de banco, el proceso se encarga de 
llamar el botón buscar para cada una de las líneas que se importen, utilizando 
el mismo procedimiento comentado anteriormente para proporcionar-nos las 
sugerencias.

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

.. inheritref:: account_bank_statement/account_bank_statement:section:commission

Movimientos con comisiones
--------------------------

Algunos bancos no desglosan las comisiones aplicadas en un movimiento 
adicional, sino que simplemente se encargan de cargar las comisiones en la misma 
línea. Esto va a producir que el botón buscar no encuentre los movimientos 
correspondientes. De todos modos, podemos solucionar esto introduciendo, en el 
apartado transacciones, el importe correspondiente a la comisión (junto con la 
cuenta a la que debemos contabilizar) y luego, pulsar el botón buscar de nuevo. 

Cómo el botón buscar busca por el importe pendiente de contabilizar y ya hemos 
introducido la línea con la comisión, estaremos buscando por el importe del 
pago y luego nos encontrarà los movimientos correctos.

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

¿Cómo conciliar dos movimientos de un mismo extracto?
*****************************************************

Si los movimientos son de gastos, se ponen los dos a la cuenta 6XX a través de 
las Transacciones, no será necesario conciliar ya que las cuentas de gastos 
no son conciliables.

Si los movimientos son de cliente, lo mejor es ponerlos con la cuenta 43X que 
corresponda y luego conciliarlos manualmente.

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
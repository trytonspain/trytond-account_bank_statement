.. inheritref:: account_bank_statement/account_bank_statement:section:extractos_bancarios

-------------------
Extractos bancarios
-------------------

En |menu_bank_statements| podemos crear y conciliar extractos bancarios.
Utilizar esta funcionalidad permite añadir trazabilidad a la información dado
que podremos relacionar cada apunte llegado del banco con los apuntes contables
que se han utilizado para contabilizarlos.

.. inheritref:: account_bank_statement/account_bank_statement:paragraph:introduccion

Las líneas de extracto bancario
-------------------------------

Al crear un extracto, podemos añadir las líneas que contiene el extracto y por
cada línea podemos conciliar con uno o varios apuntes contables.

.. inheritref:: account_bank_statement/account_bank_statement:paragraph:conciliar


Podemos hacerlo manualmente o bien utilizar el botón *Buscar*, el cual
seleccionará automáticamente un apunte de la cuenta contable del banco si su
importe pendiente de asignar en líneas de extracto es exactamente igual al
importe que tenemos pendiente de asignar de la línea de extracto actual, y
además no hay ninguna otra línea que cumpla estas condiciones. De esta forma,
el sistema no sugerirá nunca una línea que no debería.

.. inheritref:: account_bank_statement/account_bank_statement:paragraph:buscar

Una vez el importe de la línea del extracto se ha repartido en su totalidad,
debemos utilizar el botón *Contabilizar* y dirigirnos a la siguiente línea.

.. inheritref:: account_bank_statement/account_bank_statement:paragraph:contabilizar

.. inheritref:: account_bank_statement/account_bank_statement:paragraph:final-lineas

.. |menu_bank_statements| tryref:: account_bank_statement.menu_bank_statements/complete_name

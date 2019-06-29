.. _Sleeping Barber:

Sleeping Barber
===============
This is a State Engine Crank implementation of
`The Sleeping Barber <https://en.wikipedia.org/wiki/Sleeping_barber_problem>`_
concurrent algorithm design problem.

There are multiple ways to solve the issue of concurrency and synchronization of
barbers, customers and access to a waiting room.
This implementation uses a lock on the waiting room to ensure that state changes
for the barber(s) and customers do not overlap due to simultaneous access of the
waiting room.

Sleeping Barber State Diagram
-----------------------------
.. figure:: Barber.png
    :alt: SleepingBarber state diagram (Barber)
    :name: SleepingBarberUmlPng

.. note::

    SleepingBarber simulation Barber state diagram.

    This image was created using PlantUML with the UML
    contained in the Barber.py docstring :ref:`SleepingBarberUml`.

Customer State Diagram
----------------------
.. figure:: Customer.png
    :alt: SleepingBarber state diagram (Customer)

.. note::

    SleepingBarber simulation Customer state diagram.

    This image was created using PlantUML with the UML contained in
    the Customer.py docstring :ref:`SleepingBarberCustomerUml`.

Barber Module
-------------
.. automodule:: SleepingBarber.Barber
    :members:
    :undoc-members:
    :show-inheritance:

Sleeping Barber Main Module
---------------------------
.. automodule:: SleepingBarber.main
    :members:
    :undoc-members:
    :show-inheritance:

Customer Module
---------------
.. automodule:: SleepingBarber.Customer
    :members:
    :undoc-members:
    :show-inheritance:

WaitingRoom Module
------------------
.. automodule:: SleepingBarber.WaitingRoom
    :members:
    :undoc-members:
    :show-inheritance:

Customer Generator Module
-------------------------
.. automodule:: SleepingBarber.CustomerGen
    :members:
    :undoc-members:
    :show-inheritance:

Common Code
-----------
.. automodule:: SleepingBarber.Common
    :members:
    :undoc-members:
    :show-inheritance:

Exceptions
----------
.. automodule:: SleepingBarber.exceptions
    :members:
    :undoc-members:
    :show-inheritance:

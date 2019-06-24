.. _Dining Philosophers:

Dining Philosophers
===================

This is a StateEngineCrank implementation of
`The Dining Philosophers <https://en.wikipedia.org/wiki/Dining_philosophers_problem>`_
concurrent algorithm design problem.

There are multiple ways to solve the issue of concurrency and synchronization between
philosophers and their access to the forks necessary to eat.
This implementation uses an arbitrator solution in the form of a **Waiter**.
Access to the Waiter is controlled via a lock.
A philosopher that is hungry and wishes to eat gains access to the necessary forks by
first acquiring the lock and then asking the Waiter for permission.

Dining Philosophers State Diagram
---------------------------------
.. figure:: DiningPhilosophers.png
	:alt: DiningPhilosophers state diagram
	:name: DiningPhilosophersUmlPng

.. note::

	DiningPhilosophers simulation state diagram.

	This image was created using PlantUML with the UML
	contained in the DiningPhilosophers.py docstring  :ref:`DiningPhilosophersUml`.

Dining Philosophers Source
--------------------------
.. automodule:: DiningPhilosophers.main
	:members:
	:undoc-members:
	:show-inheritance:

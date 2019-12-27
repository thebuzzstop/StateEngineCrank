.. State Engine Crank documentation master file, created by
   sphinx-quickstart on Sat Mar 16 00:31:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. codeauthor:: Mark Sawyer <mark@markbsawyer.com>

Welcome to State Engine Crank
=============================
This is the documentation for State Engine Crank, aka *"The Crank"*, a tool that converts a `PlantUML <http://www.plantuml.com>`_
state diagram into executable code.

Introduction
------------
State Engine Crank was so named because, given PlantUML as input, it *"cranks out a state engine executable."*

This documentation is divided into the following sections:

* State Engine Crank - our *raison d'etre*
* Dining Philosophers - a simulation demonstrating use of *"The Crank"* (see `WikiDiners <https://en.wikipedia.org/wiki/Dining_philosophers_problem>`_)
* Sleeping Barber(s) - a simulation demonstrating use of *"The Crank"* (see `WikiBarbers <https://en.wikipedia.org/wiki/Sleeping_barber_problem>`_)
* GUI Animation - an exercise in Tkinter to provide some life to the simulations
* Model-View-Controller - a package of routines used to bring together the various simulation components utilizing an MVC architecture.
* BookMarks - a package using *"The Crank"* to parse html

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   StateEngineCrank
   DiningPhilosophers
   SleepingBarber
   GuiAnimation
   ModelViewController
   BookMarks
   glossary

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

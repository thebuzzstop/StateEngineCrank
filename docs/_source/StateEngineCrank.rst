State Engine Crank
==================

Background
----------
The original State Engine Crank tool (SEC), written in C#, was conceived and developed by
`Nelson Ferragut <https://www.linkedin.com/in/ferragut/>`_,
a Lead Engineer in Controls & Electronics at Whirlpool Corporation in Benton Harber, MI.
Subsequent versions of SEC have been written in Ansi-C and Python by
`yours-truly <https://www.linkedin.com/in/markbsawyer/>`_.

*Crankin' them bits, boss.*

Goals
-----
* Automated code generation through translation of PlantUML state diagram definition
* Simplicity of use
* Colocation of code and its documentation

Benefits
--------
* PlantUML is simple to use and defining a state machine in PlantUML is straightforward with virtually instantaneous visual feedback.
* Transitioning from a graphic state diagram to code is automated.
* Colocation of code and its documentation means that the documentation and code will stay in sync.

The Process
-----------
Developing a State Engine Crank based solution involves the following steps:

#. Identify the elements that define the problem:

    * States
    * State transitions
    * State functions (i.e. *Enter, Do, Exit*)
    * State transition triggers (i.e. *Events*)
    * State transition guard functions
    * State transition functions.

#. Create state based design using PlantUML.
#. Run State Engine Crank on the PlantUML.
#. State Engine Crank:

    * Parses the source file containing the PlantUML for known markers indicating the presence of a previous run.
    * Creates the basic infrastructure for a state engine implementation if one does not already exist.
    * Creates basic state engine definitions (e.g. states and events)
    * Creates state transition and function tables used by the state engine execution functions.
    * Creates user specific functions as required by the state design.

#. Fill in the contents of the user specific functions required to implement the user specific logic. (e.g. *enter, do, exit* functions)
#. Repeat as necessary.

State Engine Crank Code
-----------------------
State Engine Crank code is structural and is created from scratch every time SEC is run.
State Engine Crank code is readily identified within the source file.

* Declarations for states and events.
* Basic infrastructure code (e.g. startup)
* State function tables (e.g. *enter, do, exit, transitions and guards*)
* State transition tables

User Defined Code
-----------------
User defined code is application specific and needs to be written by the designer.
User defined code is readily identified within the source file.

Modules
-------
.. toctree::

    StateEngineCrank.modules
    StateEngineCrank.modules.ansi_c
    StateEngineCrank.modules.python

Main module
-----------
.. automodule:: StateEngineCrank.main
    :members:
    :undoc-members:
    :show-inheritance:

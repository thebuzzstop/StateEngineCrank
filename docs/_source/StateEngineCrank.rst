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

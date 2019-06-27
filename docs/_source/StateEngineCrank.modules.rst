StateEngineCrank modules
========================

State Engine Crank (SEC) is capable of generating ANSI-C and Python source files.

It is comprised of the following language independent modules:

    * :ref:`Configuration`
    * :ref:`Defines`
    * :ref:`ErrorHandling`
    * :ref:`FileSupport`
    * :ref:`PyStateModule`
    * :ref:`UmlParsing`

Language specific support is provided by ANSI-C and Python modules:

    * Code Generation
    * Code Scanning
    * UML Signature Support

.. _Configuration:

Configuration
-------------
.. automodule:: StateEngineCrank.modules.Config
    :members:
    :undoc-members:
    :show-inheritance:

.. _Defines:

Defines
-------
.. automodule:: StateEngineCrank.modules.Defines
    :members:
    :undoc-members:
    :show-inheritance:

.. _ErrorHandling:

ErrorHandling
-------------
.. automodule:: StateEngineCrank.modules.ErrorHandling
    :members:
    :undoc-members:
    :show-inheritance:

.. _FileSupport:

FileSupport
-----------
.. automodule:: StateEngineCrank.modules.FileSupport
    :members:
    :undoc-members:
    :show-inheritance:

.. _PyStateModule:

PyState Module
--------------
.. automodule:: StateEngineCrank.modules.PyState
    :members:
    :undoc-members:
    :show-inheritance:

.. _UmlParsing:

UML Parsing
-----------
.. automodule:: StateEngineCrank.modules.UMLParse
    :members:
    :undoc-members:
    :show-inheritance:

UMLParse State Diagram
----------------------
.. figure:: UMLParse.png
    :alt: StateEngineCrank UML Parse State Diagram

.. note::

    StateEngineCrank state diagram for the UML Parse module.
    The purpose of the state diagram is to provide a representation
    of the various state diagram elements:

        * states
        * state enter functions
        * state do functions
        * state exit functions
        * state transitions
        * state transition guard functions
        * state transition functions

    This image was created using PlantUML with the UML
    contained in the UMLParse.py docstring.

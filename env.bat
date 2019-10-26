@echo off
: setup Python path for execution from the command line
set PYTHONPATH=%CD%
set PYTHONPATH=%PYTHONPATH%;%CD%\source
set PYTHONPATH=%PYTHONPATH%;%CD%\source\BookMarks
set PYTHONPATH=%PYTHONPATH%;%CD%\source\StateEngineCrank
set PYTHONPATH=%PYTHONPATH%;%CD%\source\DiningPhilosophers
set PYTHONPATH=%PYTHONPATH%;%CD%\source\SleepingBarber

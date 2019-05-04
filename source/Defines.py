""" StateEngineCrank Defines Module """

import enum

TITLE = 'StateEngineCrank'


class Times(float, enum.Enum):
    Starting = 0.1
    Running = 0.1
    Do = 0.0
    Pausing = 0.1
    Stopping = 5.0
    LoopTime = 1.0

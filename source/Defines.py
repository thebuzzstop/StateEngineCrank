""" StateEngineCrank.Defines """

import enum

TITLE = 'StateEngineCrank'


class Config(int, enum.Enum):
    JOIN_RETRIES = 10


class Times(float, enum.Enum):
    Starting = 0.1
    Running = 0.1
    Do = 0.0
    Pausing = 0.1
    Stopping = 5.0
    LoopTime = 1.0
    Joining = 1.0

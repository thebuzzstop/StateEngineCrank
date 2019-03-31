""" StateEngineCrank Defines Module """

import enum

TITLE = 'StateEngineCrank'


class Times(float, enum.Enum):
    Waiting = 0.5
    Running = 0.1
    Stopping = 5.0

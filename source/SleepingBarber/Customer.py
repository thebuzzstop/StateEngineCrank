"""
* State machine UML, tables and user state functions.
* Contains auto-generated and user created custom code.

**SleepingBarber Customer UML**::

    @startuml

    [*] --> StartUp

    StartUp --> HairCut : EvStart [BarberSleeping]
    StartUp --> Waiting : EvStart [BarberCutting && WaitingRoomChair] / GetChair()
    StartUp --> Finish : EvStart [BarberCutting && !WaitingRoomChair] / NoHairCut()
    StartUp --> Finish : EvStop
    StartUp : enter : CustomerStart

    HairCut --> Finish : EvFinishCutting
    HairCut : enter : StartHairCut
    HairCut : do    : GetHairCut
    HairCut : exit  : StopHairCut

    Waiting --> HairCut : EvBarberReady
    Waiting --> Finish : EvStop
    Waiting : enter : StartWaiting
    Waiting : do    : Wait
    Waiting : exit  : StopWaiting

    Finish : enter : CustomerDone

    @enduml
"""

# System imports
import time
from enum import Enum

# Project imports
import mvc
from mvc import Model
from StateEngineCrank.modules.PyState import StateMachine
from SleepingBarber.Common import ConfigData as ConfigData
from SleepingBarber.Common import Statistics as Statistics
import SleepingBarber.Barber
import SleepingBarber.WaitingRoom

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    HairCut = 2
    Waiting = 3
    Finish = 4


class Events(Enum):
    EvStart = 1
    EvStop = 2
    EvFinishCutting = 3
    EvBarberReady = 4


class StateTables(object):
    state_transition_table = {}
    state_function_table = {}

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = END = DO NOT MODIFY =========
# ==============================================================================

# ==============================================================================
# ===== USER STATE CODE = BEGIN ================================================
# ==============================================================================


class UserCode(StateMachine, Model):
    """ User code unique to the Customer state implementation of the SleepingBarber simulation """

    def cleanup(self):
        self.mvc_events.unregister_actor(self.name)
        StateMachine.cleanup(self)

    def __init__(self, id_=None, barbers=None):
        """ Customer class constructor

            :param id_: customer ID, unique to this customer
            :param barbers[]: list of barbers in the simulation
        """
        self.config = ConfigData()  #: simulation configuration data
        name_ = 'Customer%03d' % id_
        Model.__init__(self, name=name_)
        StateMachine.__init__(self, sm_id=id_, name=name_, running=False,
                              startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

        self.barbers = barbers  #: list of barbers in this simulation
        self.id = id_           #: our customer ID
        self.my_class_name = self.config.customer_class_name    #: our class name

        # clock time of simulation from start to finish
        self.start_time = time.time()   #: simulation clock start time
        self.finish_time = None         #: simulation clock stop time

        # simulation time spent getting a haircut
        self.cutting_time_start = None      #: cutting clock time - start
        self.cutting_time_finish = None     #: cutting clock time - finish
        self.cutting_time_elapsed = None    #: cutting clock time - elapsed
        self.cutting_time = 0               #: cutting time - simulation time (seconds)

        # simulation time spent in the waiting room
        self.waiting_room = SleepingBarber.WaitingRoom.WaitingRoom()   #: establish access to waitingroom
        self.waiting_time_start = None      #: waiting clock time - start
        self.waiting_time_finish = None     #: waiting clock time - finish
        self.waiting_time_elapsed = None    #: waiting clock time - elapsed
        self.waiting_time = 0               #: waiting time - simulation time (seconds)
        self.my_barber = None               #: this customers barber

        self.mvc_events = mvc.Event()       #: for event registration
        self.mvc_events.register_actor(class_name=self.config.customer_class_name, actor_name=self.name)

    def get_barber(self):
        return self.my_barber

    def set_barber(self, barber):
        self.my_barber = barber

    # ===========================================================================
    # noinspection PyPep8Naming
    def Finish_CustomerDone(self):
        """ State machine *enter* function processing for the *Finish* state.

            This function is called when the *Finish* state is entered.
        """
        self.finish_time = time.time()
        elapsed_time = self.finish_time - self.start_time
        simulation_time = self.waiting_time + self.cutting_time
        self.logger('Customer[%s] Done (%d/%d)' % (self.id, elapsed_time, simulation_time))
        # record customer statistics
        stats = Statistics()
        with stats.lock:
            stats.customers.append(self)
        self.running = False

    # ===========================================================================
    # noinspection PyPep8Naming
    def HairCut_GetHairCut(self):
        """ State machine *do* function processing for the *HairCut* state.

            This function is called once every state machine iteration to perform processing
            for the *HairCut* state.
        """
        time.sleep(1)
        self.cutting_time += 1

    # ===========================================================================
    # noinspection PyPep8Naming
    def HairCut_StartHairCut(self):
        """ State machine *enter* function processing for the *HairCut* state.

            This function is called when the *HairCut* state is entered.
        """
        self.logger('Customer[%s] StartHairCut [%s]' % (self.id, self.my_barber.id))
        self.cutting_time_start = time.time()

    # ===========================================================================
    # noinspection PyPep8Naming
    def HairCut_StopHairCut(self):
        """ State machine *exit* function processing for the *HairCut* state.

            This function is called when the *HairCut* state is exited.
        """
        self.logger('Customer[%s] StopHairCut (%s)' % (self.id, self.cutting_time))
        self.cutting_time_finish = time.time()
        self.cutting_time_elapsed = self.cutting_time_finish - self.cutting_time_start

    # =========================================================
    # noinspection PyPep8Naming
    def NoHairCut(self):
        """ State machine state *transition* processing for *NoHairCut* transition.

            This function is called whenever the state transition *NoHairCut* is taken.
        """
        self.logger('Customer[%s] NoHairCut.' % self.id)
        stats = Statistics()
        with stats.lock:
            stats.lost_customers += 1

    # ===========================================================================
    # noinspection PyPep8Naming
    def StartUp_CustomerStart(self):
        """ State machine *enter* function processing for the *StartUp* state.

            This function is called when the *StartUp* state is entered.
        """
        self.logger('Customer[%s] CustomerStart' % self.id)

        # tell barbers we are here
        for barber in self.barbers:
            # if we find one sleeping then issue our start and
            # send the barber a 'customer enter' event
            if barber.current_state == SleepingBarber.Barber.States.Sleeping:
                self.post_event(Events.EvStart)
                self.my_barber = barber
                barber.current_customer = self
                barber.post_event(SleepingBarber.Barber.Events.EvCustomerEnter)
                return
        # no sleeping barbers so issue our start and hopefully
        # we end up in the waiting room
        self.post_event(Events.EvStart)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Waiting_StartWaiting(self):
        """ State machine *enter* function processing for the *Waiting* state.

            This function is called when the *Waiting* state is entered.
        """
        self.logger('Customer[%s] StartWaiting' % self.id)
        self.waiting_time_start = time.time()
        # post event for view handling
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.waiting_time, self.current_state]))

    # ===========================================================================
    # noinspection PyPep8Naming
    def Waiting_StopWaiting(self):
        """ State machine *exit* function processing for the *Waiting* state.

            This function is called when the *Waiting* state is exited.
        """
        self.logger('Customer[%s] StopWaiting' % self.id)
        self.waiting_time_finish = time.time()
        self.waiting_time_elapsed = self.waiting_time_finish - self.waiting_time_start

    # ===========================================================================
    # noinspection PyPep8Naming
    def Waiting_Wait(self):
        """ State machine *do* function processing for the *Waiting* state.

            This function is called once every state machine iteration to perform
            processing for the *Waiting* state.
        """
        time.sleep(1)
        self.waiting_time += 1
        # post event for view handling
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.waiting_time, self.current_state]))

    # =========================================================
    # noinspection PyPep8Naming
    def BarberSleeping(self):
        """ State machine *guard* processing for *BarberSleeping*.

            This function is called whenever the *guard* *BarberSleeping* is
            tested.

            :returns: True : Guard is active/valid (Barber *is* sleeping)
            :returns: False : Guard is inactive/invalid (Barber *is not* sleeping)
        """
        with self.waiting_room.lock:
            for barber in self.barbers:
                if barber.current_state is SleepingBarber.Barber.States.Sleeping:
                    return True
            return False

    # =========================================================
    # noinspection PyPep8Naming
    def BarberCutting_AND_NOT_WaitingRoomChair(self):
        """ State machine guard processing for *BarberCutting_AND_NOT_WaitingRoomChair*.

            This function is called whenever the guard *BarberCutting_AND_NOT_WaitingRoomChair* is tested.

            :returns: True : Guard is active/valid. All barbers are cutting and there are no waiting room chairs free.
            :returns: False : Guard is inactive/invalid. Not all barbers are cutting, or,
                            there are no are no waiting room chairs free.
        """
        with self.waiting_room.lock:
            for barber in self.barbers:
                if barber.current_state is SleepingBarber.Barber.States.Sleeping:
                    return False
            return self.waiting_room.full()

    # =========================================================
    # noinspection PyPep8Naming
    def BarberCutting_AND_WaitingRoomChair(self):
        """ State machine guard processing for *BarberCutting_AND_WaitingRoomChair*.

            This function is called whenever the guard *BarberCutting_AND_WaitingRoomChair* is tested.

            :returns: True : Guard is active/valid. All barbers are cutting and
                             there are waiting room chairs free.
            :returns: False : Guard is inactive/invalid. Not all barbers are cutting, or,
                              there are no are no waiting room chairs free.
        """
        with self.waiting_room.lock:
            for barber in self.barbers:
                if barber.current_state is SleepingBarber.Barber.States.Sleeping:
                    return False
            return not self.waiting_room.full()

    # =========================================================
    # noinspection PyPep8Naming
    def GetChair(self):
        """ State machine state transition processing for *GetChair*.

            This function is called whenever the state transition *GetChair* is taken.
        """
        with self.waiting_room.lock:
            self.waiting_room.get_chair(self)

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================


StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: [
        {'state2': States.HairCut, 'guard': UserCode.BarberSleeping, 'transition': None},
        {'state2': States.Waiting, 'guard': UserCode.BarberCutting_AND_WaitingRoomChair,
         'transition': UserCode.GetChair},
        {'state2': States.Finish, 'guard': UserCode.BarberCutting_AND_NOT_WaitingRoomChair,
         'transition': UserCode.NoHairCut},
    ],
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.HairCut] = {
    Events.EvFinishCutting: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Waiting] = {
    Events.EvBarberReady: {'state2': States.HairCut, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Finish] = {
}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp_CustomerStart, 'do': None, 'exit': None}

StateTables.state_function_table[States.HairCut] = \
    {'enter': UserCode.HairCut_StartHairCut, 'do': UserCode.HairCut_GetHairCut, 'exit': UserCode.HairCut_StopHairCut}

StateTables.state_function_table[States.Waiting] = \
    {'enter': UserCode.Waiting_StartWaiting, 'do': UserCode.Waiting_Wait, 'exit': UserCode.Waiting_StopWaiting}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish_CustomerDone, 'do': None, 'exit': None}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================

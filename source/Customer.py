""" SleepingBarber.Customer

* State machine UML, tables and user state functions.
* Contains auto-generated and user created custom code.
"""

# System imports
import sys
import time
from enum import Enum
import logging

# Project imports
from modules.PyState import StateMachine    # noqa
from Common import Statistics as Statistics # noqa
import WaitingRoom                          # noqa
import Barber

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

"""
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


class UserCode(StateMachine):
    """ User code unique to the Customer state implementation of the SleepingBarber simulation """

    def __init__(self, id=None, barbers=None):
        """ Customer class constructor

            Parameters:
                id - customer ID, unique to this customer
                barbers[] - list of barbers in the simulation
        """
        StateMachine.__init__(self, sm_id=id, name='Customer%03d' % id,
                              startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)
        logging.debug('Customer[%d] INIT' % id)
        self.barbers = barbers  #: list of barbers in this simulation
        self.id = id            #: our customer ID

        # clock time of simulation from start to finish
        self.start_time = time.time()   #: simulation clock start time
        self.finish_time = None         #: simulation clock stop time

        # simulation time spent getting a haircut
        self.cutting_time_start = None      #: cutting clock time - start
        self.cutting_time_finish = None     #: cutting clock time - finish
        self.cutting_time_elapsed = None    #: cutting clock time - elapsed
        self.cutting_time = 0               #: cutting time - simulation time (seconds)

        # simulation time spent in the waiting room
        self.waiting_room = WaitingRoom.WaitingRoom()   #: establish access to waitingroom
        self.waiting_time_start = None      #: waiting clock time - start
        self.waiting_time_finish = None     #: waiting clock time - finish
        self.waiting_time_elapsed = None    #: waiting clock time - elapsed
        self.waiting_time = 0               #: waiting time - simulation time (seconds)

    # ===========================================================================
    def Finish_CustomerDone(self):
        """ *Enter* function processing for *Finish* state.

            State machine *enter* function processing for the *Finish* state.
            This function is called when the *Finish* state is entered.
        """
        self.finish_time = time.time()
        elapsed_time = self.finish_time - self.start_time
        simulation_time = self.waiting_time + self.cutting_time
        logging.debug('Customer[%s] Done (%d/%d)' %
                      (self.id, elapsed_time, simulation_time))
        # record customer statistics
        stats = Statistics()
        with stats.lock:
            stats.customers.append(self)
        self.running = False

    # ===========================================================================
    def HairCut_GetHairCut(self):
        """
            *Do* function processing for the *HairCut* state

            State machine *do* function processing for the *HairCut* state.
            This function is called once every state machine iteration to perform processing
            for the *HairCut* state.
        """
        time.sleep(1)
        self.cutting_time += 1

    # ===========================================================================
    def HairCut_StartHairCut(self):
        """
            *Enter* function processing for *HairCut* state.

            State machine enter function processing for the *HairCut* state.
            This function is called when the *HairCut* state is entered.
        """
        logging.debug('Customer[%s] StartHairCut' % self.id)
        self.cutting_time_start = time.time()

    # ===========================================================================
    def HairCut_StopHairCut(self):
        """
            *Exit* function processing for the *HairCut* state.

            State machine exit function processing for the *HairCut* state.
            This function is called when the *HairCut* state is exited.
        """
        logging.debug('Customer[%s] StopHairCut (%s)' % (self.id, self.cutting_time))
        self.cutting_time_finish = time.time()
        self.cutting_time_elapsed = self.cutting_time_finish - self.cutting_time_start

    # =========================================================
    def NoHairCut(self):
        """
            State transition processing for NoHairCut

            State machine state transition processing for NoHairCut.
            This function is called whenever the state transition NoHairCut is taken.
        """
        logging.debug('Customer[%s] NoHairCut.' % self.id)
        stats = Statistics()
        with stats.lock:
            stats.lost_customers += 1

    # ===========================================================================
    def StartUp_CustomerStart(self):
        """
            *Enter* function processing for *StartUp* state.

            State machine enter function processing for the *StartUp* state.
            This function is called when the *StartUp* state is entered.
        """
        logging.debug('Customer[%s] CustomerStart' % self.id)

        # tell barbers we are here
        for barber in self.barbers:
            # if we find one sleeping then issue our start and
            # send the barber a 'customer enter' event
            if barber.current_state == Barber.States.Sleeping:
                self.post_event(Events.EvStart)
                barber.current_customer = self
                barber.post_event(Barber.Events.EvCustomerEnter)
                return
        # no sleeping barbers so issue our start and hopefully
        # we end up in the waiting room
        self.post_event(Events.EvStart)

    # ===========================================================================
    def Waiting_StartWaiting(self):
        """
            *Enter* function processing for *Waiting* state.

            State machine enter function processing for the *Waiting* state.
            This function is called when the *Waiting* state is entered.
        """
        logging.info('Customer[%s] StartWaiting' % self.id)
        self.waiting_time_start = time.time()

    # ===========================================================================
    def Waiting_StopWaiting(self):
        """
            *Exit* function processing for the *Waiting* state.

            State machine exit function processing for the *Waiting* state.
            This function is called when the *Waiting* state is exited.
        """
        logging.info('Customer[%s] StopWaiting' % self.id)
        self.waiting_time_finish = time.time()
        self.waiting_time_elapsed = self.waiting_time_finish - self.waiting_time_start

    # ===========================================================================
    def Waiting_Wait(self):
        """
            *Do* function processing for the *Waiting* state

            State machine do function processing for the *Waiting* state.
            This function is called once every state machine iteration to perform processing
            for the *Waiting* state.
        """
        time.sleep(1)
        self.waiting_time += 1

    # =========================================================
    def BarberSleeping(self):
        """ Guard processing for BarberSleeping

            State machine guard processing for BarberSleeping.
            This function is called whenever the guard BarberSleeping is tested.

            Returns:
                True - Guard is active/valid
                False - Guard is inactive/invalid
        """
        with self.waiting_room.lock:
            for barber in self.barbers:
                if barber.current_state is Barber.States.Sleeping:
                    return True
            return False

    # =========================================================
    def BarberCutting_AND_NOT_WaitingRoomChair(self):
        """ Guard processing for BarberCutting_AND_NOT_WaitingRoomChair

            State machine guard processing for BarberCutting_AND_NOT_WaitingRoomChair.
            This function is called whenever the guard BarberCutting_AND_NOT_WaitingRoomChair is tested.

            Returns:
                True - Guard is active/valid. All barbers are cutting and there are no waiting room chairs free.
                False - Guard is inactive/invalid. Not all barbers are cutting, or, there are no are no waiting room chairs free.
        """
        with self.waiting_room.lock:
            for barber in self.barbers:
                if barber.current_state is Barber.States.Sleeping:
                    return False
            return self.waiting_room.full()

    # =========================================================
    def BarberCutting_AND_WaitingRoomChair(self):
        """ Guard processing for BarberCutting_AND_WaitingRoomChair

            State machine guard processing for BarberCutting_AND_WaitingRoomChair.
            This function is called whenever the guard BarberCutting_AND_WaitingRoomChair is tested.

            Returns:
                True - Guard is active/valid. All barbers are cutting and there are waiting room chairs free.
                False - Guard is inactive/invalid. Not all barbers are cutting, or, there are no are no waiting room chairs free.
        """
        with self.waiting_room.lock:
            for barber in self.barbers:
                if barber.current_state is Barber.States.Sleeping:
                    return False
            return not self.waiting_room.full()

    # =========================================================
    def GetChair(self):
        """ State transition processing for *GetChair*

            State machine state transition processing for *GetChair*.
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
        {'state2': States.Waiting, 'guard': UserCode.BarberCutting_AND_WaitingRoomChair, 'transition': UserCode.GetChair},
        {'state2': States.Finish, 'guard': UserCode.BarberCutting_AND_NOT_WaitingRoomChair, 'transition': UserCode.NoHairCut},
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

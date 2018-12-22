from enum import Enum
from modules.PyState import StateMachine

"""
    @startuml

       [*] --> State1
	State1 --> State1 : Event11 [Guard11]
	State1 --> State2 : Event12
	State1 --> State3 : Event13
	State1 --> State3 : Event13 [Guard13A] / Transition13A
	State1 --> State3 : Event13 [Guard13B] / Transition13B
	State1 --> [*]    : EvDone  [Guard1Done] / Transition1Done
	State1 --> State2 : EvNext
	State1 --> State3 : EvNext  [GuardNext]

	State1 : enter : EnterFunc()
	State1 : do    : DoFunc()
	State1 : exit  : ExitFunc()

	State2 --> State1 : Event21
	State2 --> [*]    : EvDone [Guard2DoneA] / Transition2DoneA
	State2 --> [*]    : EvDone [Guard2DoneB] / Transition2DoneB
	State2 --> State3 : Event23
	State2 --> State3 : EvNext
	State2 --> State1 : EvNext [GuardNext]

	State2 : enter : EnterFunc()
	State2 : do    : DoFunc()
	State2 : exit  : ExitFunc()

	State3 --> State1 : Event31 [Guard31] / Transition31
	State3 --> State1 : Event31 / Transition31b
	State3 --> State2 : Event32
	State3 --> State3 : Event33
	State3 --> State3 : Event33 [Guard33] / Transition33
	State3 --> [*]    : EvDone  [Guard3Done] / Transition3Done
	State3 --> State1 : EvNext
	State3 --> State2 : EvNext  [GuardNext]

	State3 : enter : EnterFunc()
	State3 : do    : DoFunc()
	State3 : exit  : ExitFunc()

    @enduml
"""

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    State1 = 1
    State2 = 2
    State3 = 3


class Events(Enum):
    Event11 = 1
    Event12 = 2
    Event13 = 3
    EvDone = 4
    EvNext = 5
    Event21 = 6
    Event23 = 7
    Event31 = 8
    Event32 = 9
    Event33 = 10


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

    def __init__(self, id=None):
        StateMachine.__init__(self, id=id, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

    # =========================================================
    def Guard11(self):
        """
        @brief Guard processing for <i>Guard11</i>

        @details State machine guard processing for <i>Guard11</i>.
        This function is called whenever the guard <i>Guard11</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard13A(self):
        """
        @brief Guard processing for <i>Guard13A</i>

        @details State machine guard processing for <i>Guard13A</i>.
        This function is called whenever the guard <i>Guard13A</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard13B(self):
        """
        @brief Guard processing for <i>Guard13B</i>

        @details State machine guard processing for <i>Guard13B</i>.
        This function is called whenever the guard <i>Guard13B</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard1Done(self):
        """
        @brief Guard processing for <i>Guard1Done</i>

        @details State machine guard processing for <i>Guard1Done</i>.
        This function is called whenever the guard <i>Guard1Done</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard2DoneA(self):
        """
        @brief Guard processing for <i>Guard2DoneA</i>

        @details State machine guard processing for <i>Guard2DoneA</i>.
        This function is called whenever the guard <i>Guard2DoneA</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard2DoneB(self):
        """
        @brief Guard processing for <i>Guard2DoneB</i>

        @details State machine guard processing for <i>Guard2DoneB</i>.
        This function is called whenever the guard <i>Guard2DoneB</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard31(self):
        """
        @brief Guard processing for <i>Guard31</i>

        @details State machine guard processing for <i>Guard31</i>.
        This function is called whenever the guard <i>Guard31</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard33(self):
        """
        @brief Guard processing for <i>Guard33</i>

        @details State machine guard processing for <i>Guard33</i>.
        This function is called whenever the guard <i>Guard33</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def Guard3Done(self):
        """
        @brief Guard processing for <i>Guard3Done</i>

        @details State machine guard processing for <i>Guard3Done</i>.
        This function is called whenever the guard <i>Guard3Done</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def GuardNext(self):
        """
        @brief Guard processing for <i>GuardNext</i>

        @details State machine guard processing for <i>GuardNext</i>.
        This function is called whenever the guard <i>GuardNext</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # ===========================================================================
    def State1_DoFunc(self):
        """
        @brief <i>Do</i> function processing for the <i>State1</i> state

        @details State machine <i>do</i> function processing for the <i>State1</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>State1</i> state.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State1_EnterFunc(self):
        """
        @brief Enter function processing for <i>State1</i> state.

        @details State machine enter function processing for the <i>State1</i> state.
        This function is called when the <i>State1</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State1_ExitFunc(self):
        """
        @brief <i>Exit</i> function processing for the <i>State1</i> state.

        @details State machine <i>exit</i> function processing for the <i>State1</i> state.
        This function is called when the <i>State1</i> state is exited.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State2_DoFunc(self):
        """
        @brief <i>Do</i> function processing for the <i>State2</i> state

        @details State machine <i>do</i> function processing for the <i>State2</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>State2</i> state.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State2_EnterFunc(self):
        """
        @brief Enter function processing for <i>State2</i> state.

        @details State machine enter function processing for the <i>State2</i> state.
        This function is called when the <i>State2</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State2_ExitFunc(self):
        """
        @brief <i>Exit</i> function processing for the <i>State2</i> state.

        @details State machine <i>exit</i> function processing for the <i>State2</i> state.
        This function is called when the <i>State2</i> state is exited.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State3_DoFunc(self):
        """
        @brief <i>Do</i> function processing for the <i>State3</i> state

        @details State machine <i>do</i> function processing for the <i>State3</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>State3</i> state.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State3_EnterFunc(self):
        """
        @brief Enter function processing for <i>State3</i> state.

        @details State machine enter function processing for the <i>State3</i> state.
        This function is called when the <i>State3</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def State3_ExitFunc(self):
        """
        @brief <i>Exit</i> function processing for the <i>State3</i> state.

        @details State machine <i>exit</i> function processing for the <i>State3</i> state.
        This function is called when the <i>State3</i> state is exited.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition13A(self):
        """
        @brief State transition processing for <i>Transition13A</i>

        @details State machine state transition processing for <i>Transition13A</i>.
        This function is called whenever the state transition <i>Transition13A</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition13B(self):
        """
        @brief State transition processing for <i>Transition13B</i>

        @details State machine state transition processing for <i>Transition13B</i>.
        This function is called whenever the state transition <i>Transition13B</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition1Done(self):
        """
        @brief State transition processing for <i>Transition1Done</i>

        @details State machine state transition processing for <i>Transition1Done</i>.
        This function is called whenever the state transition <i>Transition1Done</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition2DoneA(self):
        """
        @brief State transition processing for <i>Transition2DoneA</i>

        @details State machine state transition processing for <i>Transition2DoneA</i>.
        This function is called whenever the state transition <i>Transition2DoneA</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition2DoneB(self):
        """
        @brief State transition processing for <i>Transition2DoneB</i>

        @details State machine state transition processing for <i>Transition2DoneB</i>.
        This function is called whenever the state transition <i>Transition2DoneB</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition31(self):
        """
        @brief State transition processing for <i>Transition31</i>

        @details State machine state transition processing for <i>Transition31</i>.
        This function is called whenever the state transition <i>Transition31</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition31b(self):
        """
        @brief State transition processing for <i>Transition31b</i>

        @details State machine state transition processing for <i>Transition31b</i>.
        This function is called whenever the state transition <i>Transition31b</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition33(self):
        """
        @brief State transition processing for <i>Transition33</i>

        @details State machine state transition processing for <i>Transition33</i>.
        This function is called whenever the state transition <i>Transition33</i> is taken.

        @todo FIXME
        """
        return

    # =========================================================
    def Transition3Done(self):
        """
        @brief State transition processing for <i>Transition3Done</i>

        @details State machine state transition processing for <i>Transition3Done</i>.
        This function is called whenever the state transition <i>Transition3Done</i> is taken.

        @todo FIXME
        """
        return

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================


StateTables.state_transition_table[States.State1] = {
    Events.Event11: {'state2': States.State1, 'guard': UserCode.Guard11, 'transition': None},
    Events.Event12: {'state2': States.State2, 'guard': None, 'transition': None},
    Events.Event13: [
        {'state2': States.State3, 'guard': None, 'transition': None},
        {'state2': States.State3, 'guard': UserCode.Guard13A, 'transition': UserCode.Transition13A},
        {'state2': States.State3, 'guard': UserCode.Guard13B, 'transition': UserCode.Transition13B},
    ],
    Events.EvDone: {'state2': States.FinalState, 'guard': UserCode.Guard1Done, 'transition': UserCode.Transition1Done},
    Events.EvNext: [
        {'state2': States.State2, 'guard': None, 'transition': None},
        {'state2': States.State3, 'guard': UserCode.GuardNext, 'transition': None},
    ],
}

StateTables.state_transition_table[States.State2] = {
    Events.Event21: {'state2': States.State1, 'guard': None, 'transition': None},
    Events.EvDone: [
        {'state2': States.FinalState, 'guard': UserCode.Guard2DoneA, 'transition': UserCode.Transition2DoneA},
        {'state2': States.FinalState, 'guard': UserCode.Guard2DoneB, 'transition': UserCode.Transition2DoneB},
    ],
    Events.Event23: {'state2': States.State3, 'guard': None, 'transition': None},
    Events.EvNext: [
        {'state2': States.State3, 'guard': None, 'transition': None},
        {'state2': States.State1, 'guard': UserCode.GuardNext, 'transition': None},
    ],
}

StateTables.state_transition_table[States.State3] = {
    Events.Event31: [
        {'state2': States.State1, 'guard': UserCode.Guard31, 'transition': UserCode.Transition31},
        {'state2': States.State1, 'guard': None, 'transition': UserCode.Transition31b},
    ],
    Events.Event32: {'state2': States.State2, 'guard': None, 'transition': None},
    Events.Event33: [
        {'state2': States.State3, 'guard': None, 'transition': None},
        {'state2': States.State3, 'guard': UserCode.Guard33, 'transition': UserCode.Transition33},
    ],
    Events.EvDone: {'state2': States.FinalState, 'guard': UserCode.Guard3Done, 'transition': UserCode.Transition3Done},
    Events.EvNext: [
        {'state2': States.State1, 'guard': None, 'transition': None},
        {'state2': States.State2, 'guard': UserCode.GuardNext, 'transition': None},
    ],
}

StateTables.state_function_table[States.State1] = \
    {'enter': UserCode.State1_EnterFunc, 'do': UserCode.State1_DoFunc, 'exit': UserCode.State1_ExitFunc}

StateTables.state_function_table[States.State2] = \
    {'enter': UserCode.State2_EnterFunc, 'do': UserCode.State2_DoFunc, 'exit': UserCode.State2_ExitFunc}

StateTables.state_function_table[States.State3] = \
    {'enter': UserCode.State3_EnterFunc, 'do': UserCode.State3_DoFunc, 'exit': UserCode.State3_ExitFunc}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================

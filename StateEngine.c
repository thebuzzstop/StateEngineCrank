/**
 *
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
 *
 */


// =============================================================================
// ========== USER STATE CODE PROTOTYPES START =================================
// =============================================================================

static BOOL_TYPE Guard11(void);
static BOOL_TYPE Guard13A(void);
static BOOL_TYPE Guard13B(void);
static BOOL_TYPE Guard1Done(void);
static BOOL_TYPE Guard2DoneA(void);
static BOOL_TYPE Guard2DoneB(void);
static BOOL_TYPE Guard31(void);
static BOOL_TYPE Guard33(void);
static BOOL_TYPE Guard3Done(void);
static BOOL_TYPE GuardNext(void);
static void State1_DoFunc(void);
static void State1_EnterFunc(void);
static void State1_ExitFunc(void);
static void State2_DoFunc(void);
static void State2_EnterFunc(void);
static void State2_ExitFunc(void);
static void State3_DoFunc(void);
static void State3_EnterFunc(void);
static void State3_ExitFunc(void);
static void Transition13A(void);
static void Transition13B(void);
static void Transition1Done(void);
static void Transition2DoneA(void);
static void Transition2DoneB(void);
static void Transition31(void);
static void Transition31b(void);
static void Transition33(void);
static void Transition3Done(void);

// =============================================================================
// ========== USER STATE CODE PROTOTYPES END ===================================
// =============================================================================

// =============================================================================
// ========== USER STATE CODE START ============================================
// =============================================================================

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard11(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13A(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13B(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard1Done(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneA(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneB(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard31(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard33(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard3Done(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE GuardNext(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static void State1_DoFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_EnterFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_ExitFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_DoFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_EnterFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_ExitFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_DoFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_EnterFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_ExitFunc(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13A(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13B(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition1Done(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneA(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneB(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31b(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition33(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition3Done(void)
{
    return;
}

// =============================================================================
// ========== USER STATE CODE END ==============================================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE STATE DEFINES START - DO NOT MODIFY ==============
// =============================================================================

typedef enum STATES {
    InitialState = -1, //!< initial state is automatic
    State1,
    State2,
    State3,
    FinalState = -2 //!< final state is automatic
} State;

// =============================================================================
// ========== MAIN STATE CODE STATE DEFINES END - DO NOT MODIFY ================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE DEFINES START - DO NOT MODIFY ====================
// =============================================================================

#ifndef GET_CURRENT_STATE
#define GET_CURRENT_STATE (CurrentState)
#endif

#ifndef SET_CURRENT_STATE
#define SET_CURRENT_STATE(state) (CurrentState=(state))
#endif

#ifndef STATE_ENGINE_INITIALIZE_HOOK
#define STATE_ENGINE_INITIALIZE_HOOK 
#endif

#ifndef STATE_ENGINE_TERMINATE_HOOK
#define STATE_ENGINE_TERMINATE_HOOK 
#endif

#ifndef EVT_HANDLER_DEFAULT_HOOK
#define EVT_HANDLER_DEFAULT_HOOK 
#endif

#ifndef MAIN_LOOP_INITIAL_STATE_HOOK
#define MAIN_LOOP_INITIAL_STATE_HOOK 
#endif

#ifndef MAIN_LOOP_FINAL_STATE_HOOK
#define MAIN_LOOP_FINAL_STATE_HOOK 
#endif

#ifndef MAIN_LOOP_DEFAULT_HOOK
#define MAIN_LOOP_DEFAULT_HOOK 
#endif

// =============================================================================
// ========== MAIN STATE CODE DEFINES END - DO NOT MODIFY ======================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE PROTOTYPES START - DO NOT MODIFY =================
// =============================================================================

static void StateEngineCrank_Initialize(void);
static void StateEngineCrank_MainDoLoop(void);
static void StateEngineCrank_Terminate(void);

static void EvDone(void);
static void EvNext(void);
static void Event11(void);
static void Event12(void);
static void Event13(void);
static void Event21(void);
static void Event23(void);
static void Event31(void);
static void Event32(void);
static void Event33(void);

// =============================================================================
// ========== MAIN STATE CODE PROTOTYPES END - DO NOT MODIFY ===================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE VARIABLES START - DO NOT MODIFY ==================
// =============================================================================

static unsigned int CurrentState = -1; //!< holds state machine current state

// =============================================================================
// ========== MAIN STATE CODE VARIABLES END - DO NOT MODIFY ====================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE START - DO NOT MODIFY ============================
// =============================================================================

/**
 * ===========================================================================
 * @brief StateEngineCrank - Main Loop
 *
 * @details This is the main state machine processing loop. It needs to be
 *          called periodically at a rate sufficient to process incoming
 *          events and service any state "Do" functions.
 * ===========================================================================
 */
static void StateEngineCrank_MainDoLoop(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            State1_DoFunc();
            break;
        case State2:
            State2_DoFunc();
            break;
        case State3:
            State3_DoFunc();
            break;
        case InitialState:
            MAIN_LOOP_INITIAL_STATE_HOOK;
            break;
        case FinalState:
            MAIN_LOOP_FINAL_STATE_HOOK;
            break;
        default:
            MAIN_LOOP_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief StateEngineCrank - Initialize
 *
 * @details This is the main state machine initialization.
 *          There is a HOOK provided for user custom code.
 * ===========================================================================
 */
static void StateEngineCrank_Initialize(void)
{
    SET_CURRENT_STATE(InitialState);
    STATE_ENGINE_INITIALIZE_HOOK;
}

/**
 * ===========================================================================
 * @brief StateEngineCrank - Terminate
 *
 * @details This is the main state machine termination.
 *          There is a HOOK provided for user custom code.
 * ===========================================================================
 */
static void StateEngineCrank_Terminate(void)
{
    SET_CURRENT_STATE(FinalState);
    STATE_ENGINE_TERMINATE_HOOK;
}

/**
 * ===========================================================================
 * @brief Event processing EvDone
 *
 * @details State machine event processing for EvDone.
 *          This function needs to be called whenever the event
 *          EvDone is detected.
 * ===========================================================================
 */
static void EvDone(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            if (Guard1Done()) {
                State1_ExitFunc();
                Transition1Done();
                SET_CURRENT_STATE(FinalState);
            }
            break;
        case State2:
            if (Guard2DoneA()) {
                State2_ExitFunc();
                Transition2DoneA();
                SET_CURRENT_STATE(FinalState);
            } else
            if (Guard2DoneB()) {
                State2_ExitFunc();
                Transition2DoneB();
                SET_CURRENT_STATE(FinalState);
            }
            break;
        case State3:
            if (Guard3Done()) {
                State3_ExitFunc();
                Transition3Done();
                SET_CURRENT_STATE(FinalState);
            }
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing EvNext
 *
 * @details State machine event processing for EvNext.
 *          This function needs to be called whenever the event
 *          EvNext is detected.
 * ===========================================================================
 */
static void EvNext(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            if (GuardNext()) {
                State1_ExitFunc();
                SET_CURRENT_STATE(State3);
                State3_EnterFunc();
            } else {
                State1_ExitFunc();
                SET_CURRENT_STATE(State2);
                State2_EnterFunc();
            }
            break;
        case State2:
            if (GuardNext()) {
                State2_ExitFunc();
                SET_CURRENT_STATE(State1);
                State1_EnterFunc();
            } else {
                State2_ExitFunc();
                SET_CURRENT_STATE(State3);
                State3_EnterFunc();
            }
            break;
        case State3:
            if (GuardNext()) {
                State3_ExitFunc();
                SET_CURRENT_STATE(State2);
                State2_EnterFunc();
            } else {
                State3_ExitFunc();
                SET_CURRENT_STATE(State1);
                State1_EnterFunc();
            }
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event11
 *
 * @details State machine event processing for Event11.
 *          This function needs to be called whenever the event
 *          Event11 is detected.
 * ===========================================================================
 */
static void Event11(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            if (Guard11()) {
                State1_ExitFunc();
                SET_CURRENT_STATE(State1);
                State1_EnterFunc();
            }
            break;
        case State2:
            break;
        case State3:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event12
 *
 * @details State machine event processing for Event12.
 *          This function needs to be called whenever the event
 *          Event12 is detected.
 * ===========================================================================
 */
static void Event12(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            State1_ExitFunc();
            SET_CURRENT_STATE(State2);
            State2_EnterFunc();
            break;
        case State2:
            break;
        case State3:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event13
 *
 * @details State machine event processing for Event13.
 *          This function needs to be called whenever the event
 *          Event13 is detected.
 * ===========================================================================
 */
static void Event13(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            if (Guard13A()) {
                State1_ExitFunc();
                Transition13A();
                SET_CURRENT_STATE(State3);
                State3_EnterFunc();
            } else
            if (Guard13B()) {
                State1_ExitFunc();
                Transition13B();
                SET_CURRENT_STATE(State3);
                State3_EnterFunc();
            } else {
                State1_ExitFunc();
                SET_CURRENT_STATE(State3);
                State3_EnterFunc();
            }
            break;
        case State2:
            break;
        case State3:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event21
 *
 * @details State machine event processing for Event21.
 *          This function needs to be called whenever the event
 *          Event21 is detected.
 * ===========================================================================
 */
static void Event21(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            break;
        case State2:
            State2_ExitFunc();
            SET_CURRENT_STATE(State1);
            State1_EnterFunc();
            break;
        case State3:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event23
 *
 * @details State machine event processing for Event23.
 *          This function needs to be called whenever the event
 *          Event23 is detected.
 * ===========================================================================
 */
static void Event23(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            break;
        case State2:
            State2_ExitFunc();
            SET_CURRENT_STATE(State3);
            State3_EnterFunc();
            break;
        case State3:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event31
 *
 * @details State machine event processing for Event31.
 *          This function needs to be called whenever the event
 *          Event31 is detected.
 * ===========================================================================
 */
static void Event31(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            break;
        case State2:
            break;
        case State3:
            if (Guard31()) {
                State3_ExitFunc();
                Transition31();
                SET_CURRENT_STATE(State1);
                State1_EnterFunc();
            } else {
                State3_ExitFunc();
                Transition31b();
                SET_CURRENT_STATE(State1);
                State1_EnterFunc();
            }
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event32
 *
 * @details State machine event processing for Event32.
 *          This function needs to be called whenever the event
 *          Event32 is detected.
 * ===========================================================================
 */
static void Event32(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            break;
        case State2:
            break;
        case State3:
            State3_ExitFunc();
            SET_CURRENT_STATE(State2);
            State2_EnterFunc();
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing Event33
 *
 * @details State machine event processing for Event33.
 *          This function needs to be called whenever the event
 *          Event33 is detected.
 * ===========================================================================
 */
static void Event33(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case State1:
            break;
        case State2:
            break;
        case State3:
            if (Guard33()) {
                State3_ExitFunc();
                Transition33();
                SET_CURRENT_STATE(State3);
                State3_EnterFunc();
            } else {
                State3_ExitFunc();
                SET_CURRENT_STATE(State3);
                State3_EnterFunc();
            }
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

// =============================================================================
// ========== MAIN STATE CODE END - DO NOT MODIFY ==============================
// =============================================================================

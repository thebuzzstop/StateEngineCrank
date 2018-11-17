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

static BOOL_TYPE Guard11(int id);
static BOOL_TYPE Guard13A(int id);
static BOOL_TYPE Guard13B(int id);
static BOOL_TYPE Guard1Done(int id);
static BOOL_TYPE Guard2DoneA(int id);
static BOOL_TYPE Guard2DoneB(int id);
static BOOL_TYPE Guard31(int id);
static BOOL_TYPE Guard33(int id);
static BOOL_TYPE Guard3Done(int id);
static BOOL_TYPE GuardNext(int id);
static void State1_DoFunc(int id);
static void State1_EnterFunc(int id);
static void State1_ExitFunc(int id);
static void State2_DoFunc(int id);
static void State2_EnterFunc(int id);
static void State2_ExitFunc(int id);
static void State3_DoFunc(int id);
static void State3_EnterFunc(int id);
static void State3_ExitFunc(int id);
static void Transition13A(int id);
static void Transition13B(int id);
static void Transition1Done(int id);
static void Transition2DoneA(int id);
static void Transition2DoneB(int id);
static void Transition31(int id);
static void Transition31b(int id);
static void Transition33(int id);
static void Transition3Done(int id);

static BOOL_TYPE Guard11(int id);
static BOOL_TYPE Guard13A(int id);
static BOOL_TYPE Guard13B(int id);
static BOOL_TYPE Guard1Done(int id);
static BOOL_TYPE Guard2DoneA(int id);
static BOOL_TYPE Guard2DoneB(int id);
static BOOL_TYPE Guard31(int id);
static BOOL_TYPE Guard33(int id);
static BOOL_TYPE Guard3Done(int id);
static BOOL_TYPE GuardNext(int id);
static void State1_DoFunc(int id);
static void State1_EnterFunc(int id);
static void State1_ExitFunc(int id);
static void State2_DoFunc(int id);
static void State2_EnterFunc(int id);
static void State2_ExitFunc(int id);
static void State3_DoFunc(int id);
static void State3_EnterFunc(int id);
static void State3_ExitFunc(int id);
static void Transition13A(int id);
static void Transition13B(int id);
static void Transition1Done(int id);
static void Transition2DoneA(int id);
static void Transition2DoneB(int id);
static void Transition31(int id);
static void Transition31b(int id);
static void Transition33(int id);
static void Transition3Done(int id);

static BOOL_TYPE Guard11(int id);
static BOOL_TYPE Guard13A(int id);
static BOOL_TYPE Guard13B(int id);
static BOOL_TYPE Guard1Done(int id);
static BOOL_TYPE Guard2DoneA(int id);
static BOOL_TYPE Guard2DoneB(int id);
static BOOL_TYPE Guard31(int id);
static BOOL_TYPE Guard33(int id);
static BOOL_TYPE Guard3Done(int id);
static BOOL_TYPE GuardNext(int id);
static void State1_DoFunc(int id);
static void State1_EnterFunc(int id);
static void State1_ExitFunc(int id);
static void State2_DoFunc(int id);
static void State2_EnterFunc(int id);
static void State2_ExitFunc(int id);
static void State3_DoFunc(int id);
static void State3_EnterFunc(int id);
static void State3_ExitFunc(int id);
static void Transition13A(int id);
static void Transition13B(int id);
static void Transition1Done(int id);
static void Transition2DoneA(int id);
static void Transition2DoneB(int id);
static void Transition31(int id);
static void Transition31b(int id);
static void Transition33(int id);
static void Transition3Done(int id);

static BOOL_TYPE Guard11(int id);
static BOOL_TYPE Guard13A(int id);
static BOOL_TYPE Guard13B(int id);
static BOOL_TYPE Guard1Done(int id);
static BOOL_TYPE Guard2DoneA(int id);
static BOOL_TYPE Guard2DoneB(int id);
static BOOL_TYPE Guard31(int id);
static BOOL_TYPE Guard33(int id);
static BOOL_TYPE Guard3Done(int id);
static BOOL_TYPE GuardNext(int id);
static void State1_DoFunc(int id);
static void State1_EnterFunc(int id);
static void State1_ExitFunc(int id);
static void State2_DoFunc(int id);
static void State2_EnterFunc(int id);
static void State2_ExitFunc(int id);
static void State3_DoFunc(int id);
static void State3_EnterFunc(int id);
static void State3_ExitFunc(int id);
static void Transition13A(int id);
static void Transition13B(int id);
static void Transition1Done(int id);
static void Transition2DoneA(int id);
static void Transition2DoneB(int id);
static void Transition31(int id);
static void Transition31b(int id);
static void Transition33(int id);
static void Transition3Done(int id);

// =============================================================================
// ========== USER STATE CODE PROTOTYPES END ===================================
// =============================================================================

// =============================================================================
// ========== USER STATE CODE START ============================================
// =============================================================================

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard11(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13A(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13B(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard1Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneA(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneB(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard31(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard33(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard3Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE GuardNext(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static void State1_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13A(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13B(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition1Done(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneA(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneB(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31b(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition33(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition3Done(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard11(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13A(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13B(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard1Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneA(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneB(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard31(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard33(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard3Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE GuardNext(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static void State1_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13A(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13B(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition1Done(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneA(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneB(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31b(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition33(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition3Done(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard11(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13A(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13B(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard1Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneA(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneB(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard31(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard33(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard3Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE GuardNext(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static void State1_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13A(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13B(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition1Done(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneA(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneB(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31b(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition33(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition3Done(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard11(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13A(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard13B(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard1Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneA(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard2DoneB(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard31(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard33(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE Guard3Done(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE GuardNext(int id)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static void State1_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State1_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State2_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_DoFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_EnterFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void State3_ExitFunc(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13A(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition13B(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition1Done(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneA(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition2DoneB(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition31b(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition33(int id)
{
    return;
}

/**
 * @todo FIXME
 */
static void Transition3Done(int id)
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

#ifndef NUM_THREADS
#define NUM_THREADS 1
#endif

#ifndef GET_CURRENT_STATE(id)
#define GET_CURRENT_STATE(id) GetCurrentState(id)
#endif

#ifndef SET_CURRENT_STATE(id, state)
#define SET_CURRENT_STATE(id, state) SetCurrentState(id, state)
#endif

#ifndef STATE_ENGINE_INITIALIZE_HOOK(id)
#define STATE_ENGINE_INITIALIZE_HOOK(id) 
#endif

#ifndef STATE_ENGINE_TERMINATE_HOOK(id)
#define STATE_ENGINE_TERMINATE_HOOK(id) 
#endif

#ifndef EVT_HANDLER_DEFAULT_HOOK(id)
#define EVT_HANDLER_DEFAULT_HOOK(id) 
#endif

#ifndef MAIN_LOOP_INITIAL_STATE_HOOK(id)
#define MAIN_LOOP_INITIAL_STATE_HOOK(id) 
#endif

#ifndef MAIN_LOOP_FINAL_STATE_HOOK(id)
#define MAIN_LOOP_FINAL_STATE_HOOK(id) 
#endif

#ifndef MAIN_LOOP_DEFAULT_HOOK(id)
#define MAIN_LOOP_DEFAULT_HOOK(id) 
#endif

// =============================================================================
// ========== MAIN STATE CODE DEFINES END - DO NOT MODIFY ======================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE PROTOTYPES START - DO NOT MODIFY =================
// =============================================================================

static void StateEngineCrank_Initialize(int id);
static void StateEngineCrank_MainDoLoop(int id);
static void StateEngineCrank_Terminate(int id);


// =============================================================================
// ========== MAIN STATE CODE PROTOTYPES END - DO NOT MODIFY ===================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE VARIABLES START - DO NOT MODIFY ==================
// =============================================================================

static unsigned int CurrentState[NUM_THREADS]; //!< holds state machine current state

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
static void StateEngineCrank_MainDoLoop(int id)
{
    switch (GET_CURRENT_STATE(id)) // dispatch according to current state
    {
        case State1:
            State1_DoFunc(id);
            break;
        case State2:
            State2_DoFunc(id);
            break;
        case State3:
            State3_DoFunc(id);
            break;
        case InitialState:
            MAIN_LOOP_INITIAL_STATE_HOOK(id);
            break;
        case FinalState:
            MAIN_LOOP_FINAL_STATE_HOOK(id);
            break;
        default:
            MAIN_LOOP_DEFAULT_HOOK(id);
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
static void StateEngineCrank_Initialize(int id)
{
    SET_CURRENT_STATE(id, InitialState);
    STATE_ENGINE_INITIALIZE_HOOK(id);
}

/**
 * ===========================================================================
 * @brief StateEngineCrank - Terminate
 *
 * @details This is the main state machine termination.
 *          There is a HOOK provided for user custom code.
 * ===========================================================================
 */
static void StateEngineCrank_Terminate(int id)
{
    SET_CURRENT_STATE(id, FinalState);
    STATE_ENGINE_TERMINATE_HOOK(id);
}

// =============================================================================
// ========== MAIN STATE CODE END - DO NOT MODIFY ==============================
// =============================================================================

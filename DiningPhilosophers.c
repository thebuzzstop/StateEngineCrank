/**
 *
    @startuml

         [*] --> Thinking

    Thinking --> GetForks : EvHungry
    Thinking : enter : StartThinkingTimer()
    Thinking : do    : Think()

    GetForks --> Eating : [HavePermission]
    GetForks : do   : AskPermission()
    GetForks : exit : PickUpForks()

    Eating --> Thinking : EvFull
    Eating : enter : StartEatingTimer()
    Eating : do    : Eat()
    Eating : exit  : PutDownForks()

    @enduml
 *
 */


// =============================================================================
// ========== USER STATE CODE PROTOTYPES START =================================
// =============================================================================

static void Eating_Eat(void);
static void Eating_PutDownForks(void);
static void Eating_StartEatingTimer(void);
static void GetForks_AskPermission(void);
static void GetForks_PickUpForks(void);
static BOOL_TYPE RandomEvent(void);
static void Thinking_StartThinkingTimer(void);
static void Thinking_Think(void);

// =============================================================================
// ========== USER STATE CODE PROTOTYPES END ===================================
// =============================================================================

// =============================================================================
// ========== USER STATE CODE START ============================================
// =============================================================================

/**
 * @todo FIXME
 */
static void Eating_Eat(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Eating_PutDownForks(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Eating_StartEatingTimer(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void GetForks_AskPermission(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void GetForks_PickUpForks(void)
{
    return;
}

/**
 * @todo FIXME
 */
static BOOL_TYPE RandomEvent(void)
{
    return TRUE;
}

/**
 * @todo FIXME
 */
static void Thinking_StartThinkingTimer(void)
{
    return;
}

/**
 * @todo FIXME
 */
static void Thinking_Think(void)
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
    Thinking,
    GetForks,
    Eating,
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

static void EvFull(void);
static void EvHungry(void);

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
        case Thinking:
            Thinking_Think();
            break;
        case GetForks:
            GetForks_AskPermission();
            break;
        case Eating:
            Eating_Eat();
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
 * @brief Event processing EvFull
 *
 * @details State machine event processing for EvFull.
 *          This function needs to be called whenever the event
 *          EvFull is detected.
 * ===========================================================================
 */
static void EvFull(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case Thinking:
            break;
        case GetForks:
            break;
        case Eating:
            Eating_PutDownForks();
            SET_CURRENT_STATE(Thinking);
            Thinking_StartThinkingTimer();
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing EvHungry
 *
 * @details State machine event processing for EvHungry.
 *          This function needs to be called whenever the event
 *          EvHungry is detected.
 * ===========================================================================
 */
static void EvHungry(void)
{
    switch (GET_CURRENT_STATE) // dispatch according to current state
    {
        case Thinking:
            SET_CURRENT_STATE(GetForks);
            break;
        case GetForks:
            break;
        case Eating:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK;
            break;
    }
}

// =============================================================================
// ========== MAIN STATE CODE END - DO NOT MODIFY ==============================
// =============================================================================

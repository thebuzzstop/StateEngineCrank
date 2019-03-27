/**
 *
    @startuml

         [*] --> StartUp

	StartUp --> Thinking : EvStart
	StartUp --> Finish : EvStop
	StartUp : enter : StartUp()

    Thinking --> Hungry : EvHungry
    Thinking --> Finish : EvStop
    Thinking : enter : StartThinkingTimer()
    Thinking : do    : Think()

    Hungry --> Eating : EvHaveForks
    Hungry --> Finish : EvStop
    Hungry : do   : AskPermission()
    Hungry : exit : PickUpForks()

    Eating --> Thinking : EvFull
    Eating --> Finish : EvStop
    Eating : enter : StartEatingTimer()
    Eating : do    : Eat()
    Eating : exit  : PutDownForks()

	Finish : do : Finish()

    @enduml
 *
 */

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <pthread.h>

#include <errno.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#ifndef TRUE
#define TRUE (1==1)
#endif
#ifndef FALSE
#define FALSE !TRUE
#endif

#include <sys/time.h>

typedef unsigned char BOOL_TYPE;	//!< 1/0 = True/False
typedef unsigned char FORK_TYPE;	//!< a fork for eating
typedef BOOL_TYPE FORK_FREE;		//!< 1/0 = Free/Busy = Fork Status

#define PHILOSOPHERS 25				//!< number of philosophers dining
#define NUM_THREADS PHILOSOPHERS	//!< each philosopher is a thread

#define EAT_MIN 10			//!< minimum number of seconds to eat
#define EAT_MAX 20			//!< maximum number of seconds to eat
#define THINK_MIN 10		//!< minimum number of seconds to think
#define	THINK_MAX 20		//!< maximum number of seconds to think
#define DINING_LOOPS 500	//!< maximum number of main loops for dining

//! Return a random number of seconds to eat or think
#define SECONDS(min, max) ((rand() % ((max)-(min))) + (min))

// =============================================================================
// ========== MAIN STATE CODE STATE DEFINES START - DO NOT MODIFY ==============
// =============================================================================

typedef enum STATES {
    InitialState = -1, //!< initial state is automatic
    StartUp,
    Thinking,
    Finish,
    Hungry,
    Eating,
    FinalState = -2 //!< final state is automatic
} State;

// =============================================================================
// ========== MAIN STATE CODE STATE DEFINES END - DO NOT MODIFY ================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE PROTOTYPES START - DO NOT MODIFY =================
// =============================================================================

static void StateEngineCrank_MainDoLoop(int id);

static void EvFull(int id);
static void EvHaveForks(int id);
static void EvHungry(int id);
static void EvStart(int id);
static void EvStop(int id);

// =============================================================================
// ========== MAIN STATE CODE PROTOTYPES END - DO NOT MODIFY ===================
// =============================================================================

/**
 * Philosopher control structure
 */
typedef struct _PHILOSOPHER_T {
	int	id;						//!< philosopher ID associated with this structure
	pthread_t thread;			//!< this philosopher thread variable
	int current_state;			//!< current state
	int events;					//!< counter used for tracking event activity
	int eating_seconds;			//!< number of seconds spent eating
	int thinking_seconds;		//!< number of seconds spent thinking
	int hungry_seconds;			//!< number of seconds spent hungry
	int event_timer;			//!< timer used to time eating & thinking
	int exit_code;				//!< exit code returned by this philosopher
	int waiter_busy;			//!< number of times the waiter was busy

    BOOL_TYPE running;          //!< TRUE, simulation is running
	BOOL_TYPE has_forks;		//!< TRUE, philosopher has possession of both forks
	FORK_TYPE left_fork;		//!< philosophers left fork (index)
	FORK_TYPE right_fork;		//!< philosophers right fork (index)
} PHILOSOPHER_T, *PHILOSOPHER_PTR_T;

static PHILOSOPHER_T Philosophers[PHILOSOPHERS];	//!< Array of philosopher control structures
static int Forks[PHILOSOPHERS];		                //!< 1 fork for each philosopher
static pthread_mutex_t maitre_d;					//!< matre-d who grants access to forks
static pthread_mutex_t stdio_lock;					//!< mutex for locking stdio (for printing)

/**
 * @brief A fork is either Free or InUse
 */
typedef enum _Fork_t {
	Free,
	InUse
} Fork_t, *Fork_tp;

/**
 * @brief Philosopher exit codes
 */
typedef enum _ExitCode_t {
	Init = -1,
	Running = 1,
	Success = 2,
} ExitCode_t, *ExitCode_tp;

/**
 * @brief Macro to determine the index of a philosophers left fork.
 * @details A philosophers left fork is the same as the philosoper's index.
 */
#define LEFT_FORK(p) (p)

/**
 * @brief Macro to determine the index of a philosophers right fork.
 * @details A philosophers right fork is the philosophers index + 1 MOD the
 * number of philosophers at the table.
 */
#define RIGHT_FORK(p) ((p+1) % (PHILOSOPHERS))

/**
 * Private function prototypes
 */
//static void *start_thread(void *);
static void start_simulation_timer(void);
static int simulation_timer(void);

#define MAIN_LOOP_INITIAL_STATE_HOOK(id) (Philosophers[id].current_state = StartUp)
#define MAIN_LOOP_DEFAULT_HOOK(id) printf("MainLoop Default Hook: %d", id)

#define STATE_ENGINE_RUNNING(id) (Philosophers[id].running)

#define GET_CURRENT_STATE(id) Philosophers[id].current_state
#define SET_CURRENT_STATE(id, state) (Philosophers[id].current_state = state)

#define EVT_HANDLER_DEFAULT_HOOK(id) printf("EvtHandler Default Hook: %d", id)

// =============================================================================
// ========== MAIN STATE CODE DEFINES START - DO NOT MODIFY ====================
// =============================================================================

#ifndef NUM_THREADS
#define NUM_THREADS 1
#endif

#ifndef GET_CURRENT_STATE
#define GET_CURRENT_STATE(id) 
#endif

#ifndef SET_CURRENT_STATE
#define SET_CURRENT_STATE(id, state) 
#endif

#ifndef STATE_ENGINE_RUNNING
#define STATE_ENGINE_RUNNING(id) 
#endif

#ifndef STATE_ENGINE_INITIALIZE_HOOK
#define STATE_ENGINE_INITIALIZE_HOOK(id) 
#endif

#ifndef STATE_ENGINE_TERMINATE_HOOK
#define STATE_ENGINE_TERMINATE_HOOK(id) 
#endif

#ifndef EVT_HANDLER_DEFAULT_HOOK
#define EVT_HANDLER_DEFAULT_HOOK(id) 
#endif

#ifndef MAIN_LOOP_INITIAL_STATE_HOOK
#define MAIN_LOOP_INITIAL_STATE_HOOK(id) 
#endif

#ifndef MAIN_LOOP_FINAL_STATE_HOOK
#define MAIN_LOOP_FINAL_STATE_HOOK(id) 
#endif

#ifndef MAIN_LOOP_DEFAULT_HOOK
#define MAIN_LOOP_DEFAULT_HOOK(id) 
#endif

// =============================================================================
// ========== MAIN STATE CODE DEFINES END - DO NOT MODIFY ======================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE VARIABLES START - DO NOT MODIFY ==================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE VARIABLES END - DO NOT MODIFY ====================
// =============================================================================

// =============================================================================
// ========== USER STATE CODE PROTOTYPES START =================================
// =============================================================================

static void Eating_Eat(int id);
static void Eating_PutDownForks(int id);
static void Eating_StartEatingTimer(int id);
static void Finish_Finish(int id);
static void Hungry_AskPermission(int id);
static void Hungry_PickUpForks(int id);
static void StartUp_StartUp(int id);
static void Thinking_StartThinkingTimer(int id);
static void Thinking_Think(int id);

// =============================================================================
// ========== USER STATE CODE PROTOTYPES END ===================================
// =============================================================================

/**
 * logger - print to standard output
 */
void logger(const char *format, ...)
{
	int lock_rtn = pthread_mutex_lock(&stdio_lock);
	if (0 == lock_rtn)
	{
		va_list args;
		va_start (args, format);
		printf("\n");
		vprintf (format, args);
		va_end (args);
	} else {
		printf("Error locking STDIO: %d", lock_rtn);
		exit(lock_rtn);
	}
	pthread_mutex_unlock(&stdio_lock);
}

/**
 * StartThread - start a philosopher thread
 */
void *StartThread(void *argp)
{
	int id = *(int *)argp;
	StartUp_StartUp(id);
	StateEngineCrank_MainDoLoop(id);
	return NULL;
}

/**
 * Main_Event_Loop
 */
int main(void)
{
	setbuf(stdout, NULL);
	setbuf(stderr, NULL);

	// Initialize the random number generator
	srand(time(NULL));

	// Start the simulation timer
	start_simulation_timer();

	// Initialize all philosophers
	for (int i=0; i<PHILOSOPHERS; i++) {
		Philosophers[i].id = i;							//!< philosopher id (index)
        Philosophers[i].running = FALSE;                //!< means of starting and stopping the simulation
		Philosophers[i].event_timer = 0;				//!< event timer in reset
		Philosophers[i].events = 0;						//!< counter for monitoring event activity
		Philosophers[i].thinking_seconds = 0;			//!< number of seconds thinking
		Philosophers[i].eating_seconds = 0;				//!< number of seconds eating
		Philosophers[i].hungry_seconds = 0;				//!< number of seconds being hungry
		Philosophers[i].exit_code = Init;				//!< exit code returned
		Philosophers[i].waiter_busy = 0;				//!< number of times waiter was busy

		// Allocate forks for this philosopher
		Philosophers[i].left_fork = LEFT_FORK(i);		//!< philosopher fork index - left
		Philosophers[i].right_fork = RIGHT_FORK(i);		//!< philosopher fork index - right
		Philosophers[i].has_forks = FALSE;				//!< not in possession of forks

		// Initialize all forks to Free
		Forks[i] = Free;
	}

	// Initialize the Maitre'd mutex
	pthread_mutex_init(&maitre_d, NULL);
	pthread_mutex_init(&stdio_lock, NULL);

	// Create the philosopher threads
	logger("[%04d] Creating threads.", simulation_timer());
	for (int i=0; i<PHILOSOPHERS; i++) {
		pthread_create(&Philosophers[i].thread, NULL, StartThread, &Philosophers[i].id);
		// Custom hook for state engine initialization
	}

	// Start main processing loop
	logger("[%04d] Philosophers dining [START].", simulation_timer());

	// Tell all philosophers to start
	for (int i=0; i<PHILOSOPHERS; i++) {
		Philosophers[i].events++;
		EvStart(i);
	}

	// Main dining loop
	for (int loops=0; loops<=DINING_LOOPS; loops++) {
		// Let 1 tick of the system clock elapse
		sleep(1);
	}

	// Tell all philosophers to finish up
	logger("[%04d] Stopping simulation", simulation_timer());
	for (int i=0; i<PHILOSOPHERS; i++) {
		Philosophers[i].events++;
    	EvStop(i);
	}

	// Wait for all philosophers to finish dining
    for (int i=0; i<PHILOSOPHERS; i++) {
        pthread_join(Philosophers[i].thread, NULL);
    }

	logger("[%04d] Philosophers dining [FINISH].", simulation_timer());

	 // Display philosopher statistics
	for (int i=0; i<PHILOSOPHERS; i++) {
		int total =	Philosophers[i].id +
					Philosophers[i].events +
					Philosophers[i].thinking_seconds +
					Philosophers[i].eating_seconds +
					Philosophers[i].hungry_seconds +
					Philosophers[i].waiter_busy;
		logger("Philosopher %2d: events: %3d  thinking: %3d  eating: %3d  hungry: %3d  waiter: %3d  total: %3d",
				Philosophers[i].id+1,
				Philosophers[i].events,
				Philosophers[i].thinking_seconds,
				Philosophers[i].eating_seconds,
				Philosophers[i].hungry_seconds,
				Philosophers[i].waiter_busy,
				total);
	}
	exit (EXIT_SUCCESS);
}

/**
 * @brief Start a simulation thread
 * @param start_void_argp pointer to philosopher structure
 */
//static void *start_thread(void *start_void_argp)
//{
//    PHILOSOPHER_PTR_T philosopher = (PHILOSOPHER_PTR_T)start_void_argp;
//}

static struct timeval StartTime;
static struct timeval CurrentTime;
//{
//    time_t      tv_sec;     /* seconds */
//    suseconds_t tv_usec;    /* microseconds */
//};
/**
 * @brief Start the simulation timer
 */
static void start_simulation_timer(void)
{
	gettimeofday(&StartTime, NULL);
}

/**
 * @brief Return elapsed simulation time
 * @return elapsed time in seconds
 */
int simulation_timer(void)
{
	gettimeofday(&CurrentTime, NULL);
	return CurrentTime.tv_sec - StartTime.tv_sec;
}

// =============================================================================
// ========== USER STATE CODE START ============================================
// =============================================================================

/**
 * @brief State: Eating, philosopher eats for a time slot
 */
static void Eating_Eat(int id)
{
	logger("[%04d][%02d] Eating (%d)", simulation_timer(), id, Philosophers[id].event_timer);
	if (Philosophers[id].event_timer) {
		Philosophers[id].event_timer--;
	}
	if (Philosophers[id].event_timer) {
		sleep(1);
		Philosophers[id].eating_seconds++;
	} else {
		logger("[%04d][%02d] EvFull", simulation_timer(), id);
		EvFull(id);
		Philosophers[id].events++;
	}
}

/**
 * @brief State: Eating, philosopher done eating, put down the forks
 */
static void Eating_PutDownForks(int id)
{
    Forks[Philosophers[id].left_fork] = Free;
    Forks[Philosophers[id].right_fork] = Free;
}

/**
 * @brief State: Eating, start the eating timer for this philosopher
 */
static void Eating_StartEatingTimer(int id)
{
	Philosophers[id].event_timer = rand() % ((EAT_MAX-EAT_MIN)+1);
}

/**
 * @brief State: Finish, perform exit processing for this philosopher
 */
static void Finish_Finish(int id)
{
	Philosophers[id].exit_code = Success;
    pthread_exit(&Philosophers[id].exit_code);
}

/**
 * @brief State: Hungry, philosopher is hungry, ask permission to eat
 */
static void Hungry_AskPermission(int id)
{
	BOOL_TYPE have_forks = FALSE;

	// try to get the maitre d's attention
	if (0 == pthread_mutex_trylock(&maitre_d)) {
		if ((Forks[Philosophers[id].left_fork] == Free) &&
			(Forks[Philosophers[id].right_fork] == Free)) {
			Forks[Philosophers[id].left_fork] = InUse;
			Forks[Philosophers[id].right_fork] = InUse;
			logger("[%04d][%02d] EvHaveForks", simulation_timer(), id);
			EvHaveForks(id);
			Philosophers[id].events++;
			have_forks = TRUE;
		}
		pthread_mutex_unlock(&maitre_d);
	} else {
		Philosophers[id].waiter_busy++;
	}

	// if we didn't get forks then sleep for a bit
	if (!have_forks) {
		sleep(1);
		Philosophers[id].hungry_seconds++;
	}
}

/**
 * @brief State: Hungry, philosopher has been granted permission to eat, so pickup the forks
 */
static void Hungry_PickUpForks(int id)
{
    Forks[Philosophers[id].left_fork] = InUse;
    Forks[Philosophers[id].right_fork] = InUse;
}

/**
 * @brief State: Startup, philosopher startup processing
 */
static void StartUp_StartUp(int id)
{
	logger("[%04d][%02d] Startup", simulation_timer(), id);

	Philosophers[id].exit_code = Running;
	Philosophers[id].running = TRUE;
}

/**
 * @brief State: Thinking, start the thinking timer for this philosopher
 */
static void Thinking_StartThinkingTimer(int id)
{
	Philosophers[id].event_timer = rand() % ((THINK_MAX-THINK_MIN)+1);
}

/**
 * @brief State: Thinking, this philosopher thinks for a time slot
 */
static void Thinking_Think(int id)
{
	logger("[%04d][%02d] Thinking (%d)", simulation_timer(), id, Philosophers[id].event_timer);
	if (Philosophers[id].event_timer) {
		Philosophers[id].event_timer--;
	}
	if (Philosophers[id].event_timer) {
	    sleep(1);
	    Philosophers[id].thinking_seconds++;
	} else {
		logger("[%04d][%02d] EvHungry", simulation_timer(), id);
		EvHungry(id);
		Philosophers[id].events++;
	}
}

// =============================================================================
// ========== USER STATE CODE END ==============================================
// =============================================================================

// =============================================================================
// ========== MAIN STATE CODE START - DO NOT MODIFY ============================
// =============================================================================

/**
 * ===========================================================================
 * @brief StateEngineCrank - Main Loop
 *
 * @details This is the main state machine processing loop.
 * ===========================================================================
 */
static void StateEngineCrank_MainDoLoop(int id)
{
    STATE_ENGINE_INITIALIZE_HOOK(id);
loop:
    switch (GET_CURRENT_STATE(id)) // dispatch according to current state
    {
        case StartUp:
            break;
        case Thinking:
            Thinking_Think(id);
            break;
        case Finish:
            Finish_Finish(id);
            break;
        case Hungry:
            Hungry_AskPermission(id);
            break;
        case Eating:
            Eating_Eat(id);
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
goto loop;
    STATE_ENGINE_TERMINATE_HOOK(id);
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
static void EvFull(int id)
{
    switch (GET_CURRENT_STATE(id)) // dispatch according to current state
    {
        case StartUp:
            break;
        case Thinking:
            break;
        case Finish:
            break;
        case Hungry:
            break;
        case Eating:
            Eating_PutDownForks(id);
            SET_CURRENT_STATE(id, Thinking);
            Thinking_StartThinkingTimer(id);
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK(id);
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing EvHaveForks
 *
 * @details State machine event processing for EvHaveForks.
 *          This function needs to be called whenever the event
 *          EvHaveForks is detected.
 * ===========================================================================
 */
static void EvHaveForks(int id)
{
    switch (GET_CURRENT_STATE(id)) // dispatch according to current state
    {
        case StartUp:
            break;
        case Thinking:
            break;
        case Finish:
            break;
        case Hungry:
            Hungry_PickUpForks(id);
            SET_CURRENT_STATE(id, Eating);
            Eating_StartEatingTimer(id);
            break;
        case Eating:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK(id);
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
static void EvHungry(int id)
{
    switch (GET_CURRENT_STATE(id)) // dispatch according to current state
    {
        case StartUp:
            break;
        case Thinking:
            SET_CURRENT_STATE(id, Hungry);
            break;
        case Finish:
            break;
        case Hungry:
            break;
        case Eating:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK(id);
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing EvStart
 *
 * @details State machine event processing for EvStart.
 *          This function needs to be called whenever the event
 *          EvStart is detected.
 * ===========================================================================
 */
static void EvStart(int id)
{
    switch (GET_CURRENT_STATE(id)) // dispatch according to current state
    {
        case StartUp:
            SET_CURRENT_STATE(id, Thinking);
            Thinking_StartThinkingTimer(id);
            break;
        case Thinking:
            break;
        case Finish:
            break;
        case Hungry:
            break;
        case Eating:
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK(id);
            break;
    }
}

/**
 * ===========================================================================
 * @brief Event processing EvStop
 *
 * @details State machine event processing for EvStop.
 *          This function needs to be called whenever the event
 *          EvStop is detected.
 * ===========================================================================
 */
static void EvStop(int id)
{
    switch (GET_CURRENT_STATE(id)) // dispatch according to current state
    {
        case StartUp:
            SET_CURRENT_STATE(id, Finish);
            break;
        case Thinking:
            SET_CURRENT_STATE(id, Finish);
            break;
        case Finish:
            break;
        case Hungry:
            Hungry_PickUpForks(id);
            SET_CURRENT_STATE(id, Finish);
            break;
        case Eating:
            Eating_PutDownForks(id);
            SET_CURRENT_STATE(id, Finish);
            break;
        default:
            EVT_HANDLER_DEFAULT_HOOK(id);
            break;
    }
}

// =============================================================================
// ========== MAIN STATE CODE END - DO NOT MODIFY ==============================
// =============================================================================

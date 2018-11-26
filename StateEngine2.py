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

""" SleepingBarber.main

The Sleeping Barber main module pulls together the various pieces of the Sleeping Barber
simulation.

The main module contains:

* Top level code for SleepingBarber(s) simulation.
* Main driver, instantiates Barber(s) and Customer(s) and drives the state machines
"""

# System imports
import time
import threading

# Project imports
import mvc
import exceptions
# from exceptions import JoinFailure

import Defines

from SleepingBarber.Common import ConfigData as ConfigData
from SleepingBarber.Common import Statistics as Statistics
from SleepingBarber.Barber import UserCode as UserCode
from SleepingBarber.Barber import Events as BarberEvents
from SleepingBarber.Customer import Events as CustomerEvents
from SleepingBarber.CustomerGen import CustomerGenerator
from SleepingBarber.WaitingRoom import WaitingRoom


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Barber(UserCode):
    """ Extends the UserCode base class """

    def cleanup(self):
        UserCode.cleanup(self)

    def __init__(self, barber_id=None):
        UserCode.__init__(self, user_id=barber_id, target=self.run)


class SleepingBarber(mvc.Model):
    """ Main SleepingBarber(s) Class """

    def __init__(self, exit_when_done=None):
        super().__init__('barbers', thread=threading.Thread(name='barbers', target=self.run))

        #: simulation configuration data
        self.config = ConfigData()

        # determine our exit criteria
        if exit_when_done is not None:
            self.exit_when_done = exit_when_done
        else:
            self.exit_when_done = True

        #: event processing
        self.mvc_events = mvc.Event()
        self.mvc_events.register_class(self.name)

        #: register mvc model events
        self.mvc_model_events = [
            mvc.Event.Events.LOOPS,
            mvc.Event.Events.STATISTICS,
            mvc.Event.Events.ALLSTOPPED,
            mvc.Event.Events.JOINING,
            mvc.Event.Events.LOGGER
        ]
        for event_ in self.mvc_model_events:
            self.mvc_events.register_event(self.name, event=event_, event_type='model', text=event_.name)

        #: register philosopher statemachine events
        for e in BarberEvents:
            self.mvc_events.register_event(class_name=self.name, event=e, event_type='model',
                                           text='%s[%s][%s]' % (self.name, e.name, e.value), data=e.value)

        #: The sleeping barbers
        self.barbers = []

        #: The customer generator
        self.cg = None

        #: The waiting room
        self.waiting_room = None

        #: Instantiate the statistics module
        self.statistics = Statistics()

    def create_barbers(self, first_time):
        if not first_time:
            # unregister barber actors so that they can be recreated
            for b in self.barbers:
                self.mvc_events.unregister_actor(b.name)
            # now delete our instantiations
            del self.barbers
            self.barbers = []
            self.running = False

        for id_ in range(self.config.barbers):
            barber = Barber(id_)
            self.barbers.append(barber)
            for vk in self.views.keys():
                barber.register(self.views[vk])

    def register(self, view):
        self.views[view.name] = view
        for b in self.barbers:
            b.register(view)
        if self.cg is not None:
            self.cg.register(view)

    def update(self, event):
        """ Called by Views and/or Controller to alert us to an event """
        if event['class'] is not self.name:
            raise Exception('Dining: Unknown event type')
        # process event received
        if event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.START]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_running()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STEP]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_step()
            for p in self.barbers:
                p.set_step()
                self.cg.set_step()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STOP]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_stopping()
            self.cg.set_stopping()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.PAUSE]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_pause()
            for p in self.barbers:
                p.set_pause()
                self.cg.set_pause()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.RESUME]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_resume()
            for p in self.barbers:
                p.set_resume()
            self.cg.set_resume()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.ALLSTOPPED]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.LOOPS]['event']:
            if (event['data'] % 10) == 0:
                self.logger('[{}]: Iteration: {}'.format(event['class'], event['data']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.TIMER]['event']:
            pass
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.LOGGER]['event']:
            self.logger('Event: %s / %s' % (event['text'], event['data']))
        else:
            raise Exception('Unhandled event')

    def run(self):
        """ SleepingBarber Main Program

            Implemented as a function so as to be callable from an outside
            entity when running in concert with other applications.

            Also runnable as a standalone application.
        """
        done = False
        first_time = True
        while not done:

            # Instantiate the waiting room
            # nb: barbers and customers require a newly instantiated waiting room
            if self.waiting_room is None:
                self.waiting_room = WaitingRoom()
            else:
                self.waiting_room.reset()

            # Instantiate and initialize all barbers
            self.create_barbers(first_time=first_time)
            first_time = False

            # Instantiate the customer generator
            if self.cg is not None:
                self.cg.cleanup()
                del self.cg
            self.cg = CustomerGenerator(self.config.customer_rate, self.config.customer_variance, self.barbers)
            for v in self.views.keys():
                self.cg.register(self.views[v])

            # Reset simulation components
            self.statistics.reset()

            # Wait for simulation to start running
            while not self.running:
                time.sleep(Defines.Times.Starting)

            # Start the simulation, i.e. start all barbers and the customer generator
            for b in self.barbers:
                b.running = True
                b.event(BarberEvents.EvStart)

            # Start the customer generator
            self.cg.thread.start()
            self.cg.running = True

            # Wait for the simulation to complete
            for loop in range(self.config.simulation_loops):
                # Sleep for 1 loop iteration time slot
                time.sleep(Defines.Times.LoopTime)
                # Bump loop count and notify
                loop += 1
                self.notify(self.mvc_events.events[self.name][mvc.Event.Events.LOOPS], data=loop)
                # Pause if requested, keep monitoring the running flag
                while self.pause and self.running:
                    time.sleep(Defines.Times.Pausing)
                # Break simulation if not running
                if self.running is False:
                    break

            # Stop the customer generator
            self.cg.running = False

            # Tell the barber(s) to stop
            for barber in self.barbers:
                barber.event(BarberEvents.EvStop)

            # Tell any waiting customers to stop
            for c in self.cg.customer_list:
                c.post_event(CustomerEvents.EvStop)

            # Joining threads
            join_list_b = []
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.JOINING])
            for b in self.barbers:
                try:
                    self.join_thread(b.thread)
                    del b
                except exceptions.JoinFailure:
                    self.logger(f'JoinFailure: Barber={b}')
                    join_list_b.append(b)
            if len(join_list_b) == 0:
                self.notify(self.mvc_events.events[self.name][mvc.Event.Events.ALLSTOPPED])

            # Cleanup and Join customer generator
            self.join_thread(self.cg.thread)
            del self.cg
            self.cg = None

            # Generate some statistics of the simulation
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS],
                        text=self.statistics.barber_stats())
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS],
                        text=self.statistics.customer_stats())
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS],
                        text=self.statistics.summary_stats())

            # shutdown behavior
            if self.exit_when_done:
                self.set_stopping()
                done = True


if __name__ == '__main__':
    """ Execute main code if run from the command line """

    sleeping_barbers = SleepingBarber()
    sleeping_barbers.thread.start()
    sleeping_barbers.set_running()
    while sleeping_barbers.running:
        time.sleep(1)
    sleeping_barbers.thread.join()

    print('Sleeping Barber(s) Simulation Done')
    with sleeping_barbers.statistics as s:
        print(s.customer_stats())
        print(s.barber_stats())
        print(s.summary_stats())

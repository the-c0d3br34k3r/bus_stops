##########################
#  actors.py
#
#  This file defines classes that make up the main actors in a simulation of a
#  bus picking up passengers from bus stops.
##########################

import random

from busstop.objects import BusStop, Bus, BusPassenger, BusNetwork


class LinearBusRouteModel(BusNetwork):
    """Linear bus route with stops and buses

    Parameters
    ==========

    start: int, coordinate of start of the route
    end: int, coordinate of end of the route
    stops: list[BusStop], list of bus stops
    buses: list[Bus], list of the buses on the route
    rates: dict[str,float] (optional) rates of passengers arriving

    A LinearBusRoute instances holds a complete model of the state of all
    buses, bus stops and passengers along its route.

    Examples
    ========

    First create passengers, buses and bus stops:

        >>> dave = BusPassenger('Dave', 'West St', 'East St')
        >>> joan = BusPassenger('Joan', 'West St', 'East St')
        >>> bus = Bus('Number 47', (20, 0), 1, [dave])
        >>> busstops = [BusStop('West St', (0, 100), [joan]),
        ...             BusStop('East St', (100, 100), [])]

    Finally we are ready to create a complete linear bus route model with two
    stops and one bus:

        >>> model = LinearBusRouteModel(0, 100, busstops, [bus])

    This model has a route going from coordinate 0 to 100 with a bus stop at
    each end. There are two passengers Dave and Joan both wanting to go from
    East St to West St. Joan is waiting at the West St bus stop. Dave is on
    the bus which is already heading to East St and is currently at
    coordinate 20.
    """

    def init(self):
        """Initialise the model and return initial events.

        Computes and returns the initial events of the simulation e.g.

            >>> sally = BusPassenger('Sally', 'West St', 'East St')
            >>> bus = Bus('56', (0, 0), 1, [sally])
            >>> model = LinearBusRouteModel(0, 100, [], [bus])
            >>> events = model.init()
            >>> events
            [('boards', 'Sally', '56')]

        This shows that at the start of the simulation Sally boards the number
        56 bus.
        """
        self.passenger_num = 0

        events = []
        for stop in self.stops:
            for passenger in stop.passengers:
                events.append(('waits', passenger.name, stop.name))

        for bus in self.buses:
            for passenger in bus.passengers:
                events.append(('boards', passenger.name, bus.name))

        return events

    def update(self):
        """Update the state of the model by one time step.

        Returns any events that take place during that step:

            >>> sally = BusPassenger('Sally', 'East St', 'West St')
            >>> stop = BusStop('East St', (0, 0), [sally])
            >>> bus = Bus('56', (-1, 0), 1, [])
            >>> model = LinearBusRouteModel(0, 100, [stop], [bus])
            >>> model.init()
            [('waits', 'Sally', 'East St')]
            >>> model.update()
            [('stops', '56', 'East St'), ('boards', 'Sally', 'East St')]
            >>> model.update()
            []

        This shows that at the start of the simulation Sally boards the number
        56 bus. In the first time step Sally gets on the bus. In the second
        timestep there are no events.
        """
        events = []

        for bus in self.buses:
            events += self.update_bus(bus)

        for stop in self.stops:
            events += self.update_stop(stop)

        return events

    def update_bus(self, bus):
        """Update simulation state of bus."""

        # If bus speed is set to any value <= 0, randomize it instead.
        speed = bus.speed if bus.speed > 0 else random.randint(1, bus.max_speed)
        old_x, old_y = bus.position
        new_x = old_x + speed * bus.direction
        new_y = old_y  # Buses move horizontally
        bus.position = (new_x, old_y)

        events = []

        # Does the bus stop at any stops?
        if bus.direction == 1:
            # The bus is travelling left to right
            for stop in self.stops:
                stop_x, stop_y = stop.position
                if old_x < stop_x <= new_x:
                    events += self.stop_at(bus, stop)
        else:
            # The bus is traveling right to left - we assume it doesn't
            # stop or pick up passengers as all our passengers travel left
            # to right.
            pass

        # Update stop passengers patience value
        self.update_stop_passengers_patience()

        # Does the bus turn around?
        if not (self.start <= new_x <= self.end):
            bus.direction = - bus.direction
            events.append(('turns', bus.name))

        return events

    def update_stop_passengers_patience(self):
        for stop in self.stops:
            for passenger in stop.passengers:
                # 0 represents the peak of the grumpy scale i.e. passenger has lost all patience.
                passenger.patience = max(passenger.patience - 1, 0)


    def stop_at(self, bus, stop):
        """Handle bus stopping at stop."""

        # Passengers get off if this is their stop
        staying_passengers = []
        leaving_passengers = []
        for passenger in bus.passengers:
            if passenger.destination == stop.name:
                leaving_passengers.append(passenger)
            else:
                staying_passengers.append(passenger)

        # All passengers waiting at the bus stop get on
        boarding_passengers_count = bus.capacity - len(staying_passengers)
        boarding_passengers = stop.passengers[:boarding_passengers_count] if bus.capacity >= 0 \
            else stop.passengers

        # Actually update passengers at bus and stop
        bus.passengers = staying_passengers + boarding_passengers
        stop.passengers = stop.passengers[boarding_passengers_count:] if bus.capacity >= 0 \
            else stop.passengers

        # Record events for everyone getting on and off
        events = [('stops', bus.name, stop.name)]
        for passenger in leaving_passengers:
            events.append(('alights', passenger.name, stop.name))
        for passenger in boarding_passengers:
            events.append(('boards', passenger.name, stop.name))
        return events

    def update_stop(self, stop):
        """Update bus stop"""

        # New passengers arrive randomly at each bus stop. The probability of
        # a passenger arriving at particular stop is given by
        #     1 - self.rates[self.name].
        if stop.name in self.rates:
            rate = self.rates[stop.name]
            if rate > random.random():
                # A new passenger randomly arrives. They go to a randomly chosen destination.
                print(random.randint(0, len(self.stops)))
                destination = self.stops[random.randint(0, len(self.stops) - 1)].name
                name = 'random' + str(self.passenger_num)
                self.passenger_num += 1
                passenger = BusPassenger(name, stop.name, destination)
                stop.passengers.append(passenger)
                return [('waits', passenger.name, stop.name)]

        return []


if __name__ == "__main__":
    import doctest
    doctest.testmod()

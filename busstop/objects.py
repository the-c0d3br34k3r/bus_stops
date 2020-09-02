##########################
#  actors.py
#
#  This file defines classes that make up the main actors in a simulation of a
#  bus picking up passengers from bus stops.
##########################


class Printable:
    """Mixin to add printing functionality to subclasses.

    Examples
    ========

    A subclass just needs to define parameters and will print nicely::

        >>> class Thing(Printable):
        ...     parameters = 'foo', 'bar'
        ...     def __init__(self, foo, bar):
        ...         self.foo = foo
        ...         self.bar = bar
        >>> t = Thing(3, 'qwe')
        >>> t
        Thing(3, 'qwe')
    """
    def __repr__(self):
        classname = type(self).__name__
        args = [getattr(self, p) for p in self.parameters]
        return '%s(%s)' % (classname, ', '.join(map(repr, args)))


class BusPassenger(Printable):
    """Bus passenger going from A to B

    Parameters
    ==========

    name: str, the name of the passenger
    source: str, the name of the starting bus stop
    destination: str, the name of the ending bus stop

    Examples
    ========

    Create a passenger:

        >>> dave = BusPassenger('Dave', 'A', 'B')
        >>> dave
        BusPassenger('Dave', 'A', 'B')

    All attributes are public:

        >>> dave.name
        'Dave'
    """
    parameters = 'name', 'source', 'destination'

    def __init__(self, name, source, destination):

        if not all(isinstance(p, str) for p in (name, source, destination)):
            raise TypeError('name, source and destination should be strings')

        self.name = name
        self.source = source
        self.destination = destination


class BusStop(Printable):
    """Bus stop along a bus route with a position and passengers

    Parameters
    ==========

    name: str, name of the bus stop
    position: tuple(int,int), coordinates of the bus stop
    passengers: list[Passenger], list of the passengers at the stop

    Examples
    ========

    Create a pasenger and add to the bus stop:

        >>> dave = BusPassenger('Dave', 'West St', 'East St')
        >>> busstop = BusStop('West St', (20, 0), [dave])
        >>> busstop
        BusStop('West St', (20, 0), [BusPassenger('Dave', 'West St', 'East St')])

    """
    parameters = 'name', 'position', 'passengers'

    def __init__(self, name, position, passengers):

        if not isinstance(name, str):
            raise TypeError('name should be a string')
        if not (isinstance(position, tuple) and len(position) == 2 and
                all(isinstance(c, int) for c in position)):
            raise TypeError('position should be a pair of ints')
        if not all(isinstance(p, BusPassenger) for p in passengers):
            raise TypeError('passengers should be a list of BusPassenger')
        if not all(p.source == name for p in passengers):
            raise ValueError('passenger at the wrong stop')

        self.name = name
        self.position = position
        self.passengers = list(passengers)

    def init_animation(self, ax):
        """Initialise matplotlib animation for axes ax"""
        self.stop_line, = ax.plot([], [], 'ro', markersize=10)
        self.queue_line, = ax.plot([], [], 'bo')
        x, y = self.position
        self.text = ax.text(x, y-3, self.name, rotation=90,
                verticalalignment='top', horizontalalignment='center')
        return [self.stop_line, self.queue_line, self.text]

    def update_animation(self):
        """Update matplotlib animation for axes ax"""
        x, y = self.position
        # Redraw the bus stop
        self.stop_line.set_data([x], [y])
        # Redraw the queueing passingers
        qspace = 2
        num_passengers = len(self.passengers)
        xdata = [x] * num_passengers
        ydata = [y + qspace*(n+1) for n in range(num_passengers)]
        self.queue_line.set_data(xdata, ydata)
        # Return the patches for matplotlib to update
        return [self.stop_line, self.queue_line, self.text]


class Bus(Printable):
    """Bus traversing a linear bus route

    Parameters
    ==========

    name: str, name of the bus
    position: tuple(int,int), position of the bus
    direction: int, 1 if moving right and -1 if moving left
    passengers: list[Passenger], list of passengers

    Examples
    ========

    Create passengers and add them to a bus:

        >>> dave = BusPassenger('Dave', 'West St', 'East St')
        >>> bus = Bus('Number 47', (20,0), 1, [dave])
        >>> bus
        Bus('Number 47', (20, 0), 1, [BusPassenger('Dave', 'West St', 'East St')])

    """
    parameters = 'name', 'position', 'direction', 'passengers'

    def __init__(self, name, position, direction, passengers):

        if not isinstance(name, str):
            raise TypeError('name should be a string')
        if not (isinstance(position, tuple) and len(position) == 2 and
                all(isinstance(c, int) for c in position)):
            raise TypeError('position should be a pair of ints')
        if direction not in {1, -1}:
            raise TypeError('direction should be 1 or -1')
        if not all(isinstance(p, BusPassenger) for p in passengers):
            raise TypeError('passengers should be a list of BusPassenger')

        self.name = name
        self.position = position
        self.direction = direction
        self.passengers = list(passengers)

    def init_animation(self, ax):
        """Initialise matplotlib animation for axes ax"""
        self.bus_line, = ax.plot([], [], 'gs', markersize=10)
        self.passenger_line, = ax.plot([], [], 'bo')
        x, y = self.position
        self.text = ax.text(x, y+3, self.name,
                verticalalignment='bottom', horizontalalignment='center')
        return [self.bus_line, self.passenger_line, self.text]

    def update_animation(self):
        """Update matplotlib animation for axes ax"""
        # Redraw the bus
        x, y = self.position
        self.bus_line.set_data([x], [y])
        # Redraw the passengers
        pspace = 2
        num_passengers = len(self.passengers)
        xdata = [x] * num_passengers
        ydata = [y - pspace*(n+1) for n in range(num_passengers)]
        self.passenger_line.set_data(xdata, ydata)
        # Update text position
        self.text.set_x(x)
        self.text.set_y(y+3)
        # Return the patches for matplotlib to update
        return [self.bus_line, self.passenger_line, self.text]


class BusNetwork(Printable):
    """Network of bus stops and buses.

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
        >>> busstops = [BusStop('West St', (0, 0), [joan]),
        ...             BusStop('East St', (100, 0), [])]

    Finally we are ready to create a complete linear bus route model with two
    stops and one bus:

        >>> model = BusNetwork(0, 100, busstops, [bus])

    This model has a route going from coordinate 0 to 100 with a bus stop at
    each end. There are two passengers Dave and Joan both wanting to go from
    East St to West St. Joan is waiting at the West St bus stop. Dave is on
    the bus which is already heading to East St and is currently at
    coordinate 20.

    """

    def __init__(self, start, end, stops, buses, rates=None):
        self.start = start
        self.end = end
        self.stops = list(stops)
        self.buses = list(buses)

        if rates is None:
            rates = {}
        else:
            rates = dict(rates)
        self.rates = rates

    def init(self):
        """Initialise the model after creating nand return events"""
        raise NotImplementedError("Subclasses should override this method")

    def update(self):
        """Updates the model through one timestep"""
        raise NotImplementedError("Subclasses should override this method")

    def init_animation(self, ax):
        """Initialise matplotlib animation for axes ax"""

        # Initialise self before child objects
        patches = self._init_animation(ax)

        # Initialise all buses
        for bus in self.buses:
            patches += bus.init_animation(ax)

        # Initialise all bus stops
        for stop in self.stops:
            patches += stop.init_animation(ax)

        # List of patches for matplotlib to update
        return patches

    def update_animation(self):
        """Update matplotlib animation for axes ax"""

        # Redraw self before child objects
        patches = self._update_animation()

        # Redraw bus stops
        for stop in self.stops:
            patches += stop.update_animation()

        # Redraw buses
        for bus in self.buses:
            patches += bus.update_animation()

        # List of patches for matplotlib to update
        return patches

    def _init_animation(self, ax):
        """Initialise self for animation in axes ax"""
        size = self.end - self.start
        delta = size // 10
        ax.set_xlim([self.start-delta, self.end+delta])
        ax.set_ylim([-size//2, size//2])
        self.route_line, = ax.plot([], [], 'k-', linewidth=3)
        return [self.route_line]

    def _update_animation(self):
        """Redraw self for animation in axes ax"""
        xdata = [self.start, self.end]
        ydata = [0, 0]
        self.route_line.set_data(xdata, ydata)
        return [self.route_line]


if __name__ == "__main__":
    import doctest
    doctest.testmod()

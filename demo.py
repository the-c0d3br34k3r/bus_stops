#!/usr/bin/env python3

from busstop.objects import BusPassenger, Bus, BusStop
from busstop.linear import LinearBusRouteModel
from busstop.animation import animate_model


dave = BusPassenger('Dave', 'East St', 'West St')
joan = BusPassenger('Joan', 'East St', 'West St')

stops = [
    BusStop('East St', (0, 0), [dave]),
    BusStop('North St', (25, 0), []),
    BusStop('South St', (75, 0), []),
    BusStop('West St', (100, 0), []),
]

buses = [
    Bus('47', (20,0), 1, [joan]),
    Bus('48', (40,0), -1, []),
]

rates = {'East St': 0.03, 'North St': 0.05, 'South St': 0.03}

model = LinearBusRouteModel(0, 100, stops, buses, rates)

animate_model(model)

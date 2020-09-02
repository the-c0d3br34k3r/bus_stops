import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from busstop.objects import Bus, BusStop, BusPassenger
from busstop.linear import LinearBusRouteModel

def animate_model(model):
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])

    time = -1  # time
    events = model.init()
    for event in events:
        print((time,) + event)

    def init():
        # Initialise the graphics
        return model.init_animation(ax)

    def update(frame_number):
        # Update the simulation
        time = frame_number
        events = model.update()
        for event in events:
            print((time,) + event)
        # Update the graphics
        return model.update_animation()

    animation = FuncAnimation(fig, update, init_func=init, blit=True)
    plt.show()

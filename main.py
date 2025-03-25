import heapq
import numpy as np
import random
from scipy.stats import truncnorm # type: ignore

# Adrian Dalena, Ian Wilson, Marlon Branham

##################################### Constants (change per scenario)

# SCENARIO ONE: Default configuration from slides

NUM_WINDOWS = 10
WINDOW_EFFICIENCY = 10
NUM_CUSTOMERS = 160
NUM_WORKDAY_HOURS = 8

#####################################

class EventQueue:
    def __init__(self):
        self.queue = []

    def push(self, event):
        heapq.heappush(self.queue, event)

    def pop(self):
        return heapq.heappop(self.queue)
    
    def is_empty(self):
        return len(self.queue) == 0

class State:
    def __init__(self):
        self.windows = [0 for i in range(0,NUM_WINDOWS)]       # 10 windows; 0 == idle, 1 == busy

class Event:
    def __init__(self, event, time, args):
        self.event = event
        self.time = time
        self.args = args # to hold extra info such as work units needed, or which window to open

    # Overload for priority queue insertion based on time
    def __lt__(self, other):
        return self.time < other.time

if __name__ == "__main__":

    customerQueue = [] # Holds pairs (a,b) where a is customer ID and b is their arrival time
    custServed = 0
    waitTimeSum = 0

    # Generate the 160 customers
    customers = [
        {
            "id" : i,
            "workUnits" : truncnorm.rvs(0, 20, loc=5, scale=0.5),
            "arrivalTime" : np.random.uniform(0, 8)
        }
        for i in range(0, NUM_CUSTOMERS)
    ]

    currTime = 0
    state = State()
    eventQueue = EventQueue()

    # Populate queue with exogeneous customer arrivals
    for customer in customers:
        newEvent = Event("customerArrival", customer["arrivalTime"], [customer["workUnits"], customer["id"]])
        eventQueue.push(newEvent)
    
    # Run through events
    while currTime <= 8 and eventQueue.is_empty() == False:
        print(f"Time: {currTime}")
        currEvent = eventQueue.pop()

        if currEvent.event == "customerArrival":
            try:
                openWindow = state.windows.index(0) # Look for open windows
            except ValueError:
                openWindow = -1

            if openWindow != -1:
                state.windows[openWindow] = 1
                                                                            ## FIXME
            else:
                customerQueue.append((currEvent.args[1], currEvent.time))   ## FIXME

        elif currEvent.event == "windowOpen":
            pass                                                            ## FIXME

        currTime = currEvent.time
import heapq
import numpy as np
from queue import Queue
from scipy.stats import truncnorm # type: ignore

# Adrian Dalena, Ian Wilson, Marlon Branham

## ASSUMPTIONS:
# "Wait time" means the amount of time waiting in queue, not the time between their arrival and job finishing
# Customers that arrive or are still in queue after hour 8 will be ignored.
# Jobs in process will still be completed even if the job finishes after hour 8, so long as they were started before closing.

##################################### Constants (change per scenario)

NUM_WINDOWS = 2
WINDOW_EFFICIENCY = 10
NUM_CUSTOMERS = 10
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

    customerQueue = Queue()
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

    state = State()
    eventQueue = EventQueue()

    # Populate queue with exogeneous customer arrivals
    for customer in customers:
        newEvent = Event("customerArrival", customer["arrivalTime"], {"workUnits" : customer["workUnits"], "customerId" : customer["id"]})
        eventQueue.push(newEvent)


    currTime = 0

    # Run through events
    while currTime <= NUM_WORKDAY_HOURS and eventQueue.is_empty() == False:
        currEvent = eventQueue.pop()
        print()
        # print(f"\nTime: {currEvent.time}")
        # print(f"Event: {currEvent.event}")
        # print(f"Arguments: {currEvent.args}")

        # Ignore new customers coming after closing (but allow jobs in progress to complete)
        if currTime > NUM_WORKDAY_HOURS and currEvent.event == "customerArrival":
            continue

        if currEvent.event == "customerArrival":
            print(f"- Customer ID {currEvent.args["customerId"]} has arrived at the bank at time = {currEvent.time}")
            try:
                openWindow = state.windows.index(0) # Look for an open window
            except ValueError:                      # No open windows found (index just throws an error when the element isn't in list)
                openWindow = -1

            # Found an open window
            if openWindow != -1:
                state.windows[openWindow] = 1
                jobCompletionTime = currEvent.time + currEvent.args["workUnits"] / WINDOW_EFFICIENCY
                print(f"    - Customer ID {currEvent.args["customerId"]} is immediately getting served at window {openWindow}")
                print(f"    - Job will be complete at {jobCompletionTime}")
                newEvent = Event("jobFinish", jobCompletionTime, {"startTime" : currEvent.time, "jobWindow" : openWindow, "customerId" : currEvent.args["customerId"]})
                eventQueue.push(newEvent)
            else:
                print(f"    - No open windows, customer ID {currEvent.args["customerId"]} put into queue.")
                customerQueue.put({"customerId" : currEvent.args["customerId"], "arrivalTime" : currEvent.time})

        elif currEvent.event == "jobFinish":
            print(f"- Job for customer ID {currEvent.args["customerId"]} finished at time = {currEvent.time}")
            jobWindow = currEvent.args["jobWindow"]
            jobStart = currEvent.args["startTime"]

            custServed += 1

            # Check if customers are waiting to be served
            if not customerQueue.empty():
                if currEvent.time <= NUM_WORKDAY_HOURS:
                    customer = customerQueue.get()
                    customerId = customer["customerId"]

                    waitTime = currEvent.time - customer["arrivalTime"]
                    waitTimeSum += waitTime

                    print(f"    - Now serving customer ID {customerId} at window {jobWindow}")
                    print(f"    - Customer waited {waitTime} hours in queue")

                    state.windows[jobWindow] = 1
                    jobCompletionTime = currEvent.time + customers[customerId]["workUnits"] / WINDOW_EFFICIENCY
                    newEvent = Event("jobFinish", jobCompletionTime, {"startTime" : customer["arrivalTime"], "jobWindow" : jobWindow, "customerId" : customerId})
                    eventQueue.push(newEvent)

                    print(f"    - Job will be complete at {jobCompletionTime}")
                else:
                    print("    - Past working hours, not adding any more customers from queue.")
            else:
                state.windows[jobWindow] = 0
                print("    - No customers in queue, waiting for next customer to arrive at the bank.")

        #print(f"Queue after event:\n {[(event.event, event.time) for event in eventQueue.queue]}")
        currTime = currEvent.time

    averageWaitTime = waitTimeSum / custServed

    print("\n")
    print(f"Customers served: {custServed}/{NUM_CUSTOMERS}")
    print(f"Average Wait Time: {averageWaitTime} hours")
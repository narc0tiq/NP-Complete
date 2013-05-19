import Queue
from itertools import count
from collections import namedtuple

counter = count()
id = lambda: counter.next()

# Events are handled by PriorityQueue, so the event type ID defines the order of
# processing. This may turn out to be a bad thing.
QUIT = id()
MOUSE = id()
KEY = id()

queue = Queue.PriorityQueue()
Event = namedtuple("Event", ["type", "data"])

def post(type, data=None):
    queue.put(Event(type, data))

def generator():
    try:
        yield queue.get(False)
    except Queue.Empty:
        raise StopIteration()

import Queue
from itertools import count
from collections import namedtuple

id = count()

# Events are handled by PriorityQueue, so the event type ID defines the order of
# processing. This may turn out to be a bad thing.
QUIT = id.next()
MOUSE = id.next()
KEY = id.next()
LAUNCH = id.next()
# Dialog events:
OK = id.next()
CANCEL = id.next()
APPLY = id.next()
# Widget events:
RESIZE = id.next()

queue = Queue.PriorityQueue()
Event = namedtuple("Event", ["type", "data"])

def post(type, data=None):
    queue.put(Event(type, data))

def generator():
    try:
        while True:
            yield queue.get(False)
    except Queue.Empty:
        raise StopIteration()

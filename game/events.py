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
ACTIVATE = id.next()

queue = Queue.PriorityQueue()
Event = namedtuple("Event", ["type", "data", "widget"])

def post(type, data=None, widget=None):
    queue.put(Event(type, data, widget))

def generator():
    try:
        while True:
            yield queue.get(False)
    except Queue.Empty:
        raise StopIteration()

def handler(event_type):
    """
    A decorator that tags event handlers. Widgets use their __init__ to check for tagged handlers
    and add them to their .handlers dict.
    """
    def decorator(function):
        function.handles_event = event_type
        return function
    return decorator


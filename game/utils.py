from collections import namedtuple, MutableSet
import sys, time, string

import tcod

Point = namedtuple('Point', ['x', 'y'])
origin = Point(0, 0)

class Rect(object):
    """
    Stores a rectangle and provides easy access to its top, left, right, and
    bottom coordinates, as well as its width and height.
    """
    def __init__(self, x=0, y=0, width=0, height=0):
        """ Note: Actually uses move_to and resize. """
        self.left = self.top = self.width = self.height = 0

        self.move_to(x, y)
        self.resize(width, height)

    def move_to(self, x=None, y=None):
        if x is None:
            x = self.left
        if y is None:
            y = self.top

        self.left = x
        self.top = y

    def move_to_point(self, point):
        """ Same as move_to, but using a Point """
        self.move_to(point.x, point.y)

    def resize(self, width=None, height=None):
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        self.width = width
        self.height = height

    @property
    def origin(self):
        return self.left, self.top

    @origin.setter
    def origin(self, value):
        self.left, self.top = value

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, value):
        self.width, self.height = value

    @property
    def right(self):
        return self.left + self.width

    @right.setter
    def right(self, value):
        diff = value - self.right
        self.left += diff

    @property
    def bottom(self):
        return self.top + self.height

    @bottom.setter
    def bottom(self, value):
        diff = value - self.bottom
        self.top += diff

    @property
    def center(self):
        x = self.left + (self.width / 2)
        y = self.top + (self.height / 2)
        return (x, y)

    def is_intersecting(self, other):
        return (self.left <= other.right and self.right >= other.left and
                self.top <= other.bottom and self.bottom >= other.top)

    def contains(self, point):
        return (self.left <= point.x < self.right and
                self.top <= point.y < self.bottom)

    def __str__(self):
        return "Rect: (%d, %d)->(%d, %d)" % (self.left, self.top, self.right, self.bottom)

    def __repr__(self):
        return "Rect(x=%d, y=%d, width=%d, height=%d)" % (self.left, self.top, self.width, self.height)

    def __len__(self):
        return 4

    def __getitem__(self, key):
        if key == 0:
            return self.left
        elif key == 1:
            return self.top
        elif key == 2:
            return self.width
        elif key == 3:
            return self.height
        else:
            raise IndexError()


class OrderedSet(MutableSet):
    """ Lovingly taken from http://code.activestate.com/recipes/576694/ """
    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


vkeys = {}
chars = {}

def key_vk(vk):
    return lambda k: not k.shift and k.vk == vk

def key_vk_shift(vk):
    return lambda k: k.shift and k.vk == vk

def key_c(c):
    return lambda k: k.c == ord(c)

for name, vk in tcod.key.__dict__.items():
    if name.startswith('_') or name == "CHAR":
        continue
    elif name == "CAPSLOCK":
        name = "CLock"
    elif name == "ESCAPE":
        name = "Esc"
    elif len(name) == 2 and name.startswith("K"):
        continue
    elif name.startswith("KP"):
        name = "Num" + name[2:].capitalize()
    elif name == "LWIN":
        name = "LWin"
    elif name == "NUMLOCK":
        name = "NLock"
    elif name == "PAGEDOWN":
        name = "PageDn"
    elif name == "PAGEUP":
        name = "PageUp"
    elif name == "PRINTSCREEN":
        name = "PrtScr"
    elif name == "RWIN":
        name = "RWin"
    elif name == "SCROLLLOCK":
        name = "SLock"
    elif name == "SHIFT":
        continue
    else:
        name = name.capitalize()
    vkeys[name] = key_vk(vk)
    vkeys["Shift+"+name] = key_vk_shift(vk)

for s in string.digits, string.letters, string.punctuation:
    for ch in s:
        chars[ch] = key_c(ch)

def key_check(name):
    if vkeys[name]:
        return vkeys[name]
    elif chars[name]:
        return chars[name]

def name_key(key):
    for name, check in vkeys.iteritems():
        if check(key):
            return name
    for name, check in chars.iteritems():
        if check(key):
            return name

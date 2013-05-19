from collections import namedtuple
import sys, time

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


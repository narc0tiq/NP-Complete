""" User Interface bits and widgets """
import collections

import tcod
from game import events, utils

COLOR_BASE = 0
COLOR_SHORTCUT = 1

active_colors = tcod.ColorSet()
active_colors.set_colors(COLOR_BASE,
                         fgcolor=tcod.color.LIGHT_GREY, bgcolor=tcod.color.BLACK)
active_colors.set_colors(COLOR_SHORTCUT,
                         fgcolor=tcod.color.LIME)

disabled_colors = tcod.ColorSet()
disabled_colors.set_colors(COLOR_BASE,
                           fgcolor=tcod.color.DARKER_GREY, bgcolor=tcod.color.BLACK)
disabled_colors.set_colors(COLOR_SHORTCUT,
                           fgcolor=tcod.color.LIGHT_GREY)


class Widget(object):
    def __init__(self, parent=None, x=0, y=0, width=0, height=0):
        """
        Initialize a new generic Widget.

         * parent: if provided, the parent will be called to register_child() this widget.
         * x, y, width, height: if provided, these define the on-console `placement` of the
         widget. Some widgets may use width and height as `bounds`, as well.
        """
        self.children = utils.OrderedSet()
        self.console = tcod.root_console
        self.handlers = {}
        self.colors = active_colors
        self.effect = tcod.background.SET
        self.bounds = utils.Rect(0,0, 0,0)
        self.placement = utils.Rect(x,y, width,height)

        if parent:
            parent.register_child(self)
            self.console = parent.console

    def register_child(self, child):
        """
        Register a widget to become a child of this widget. The child's parent (if any) will
        be asked to unregister it first, and then the child's parent attribute will be
        modified.
        """
        if child.parent:
            child.parent.abandon_child(child)
        child.parent = self
        self.children.add(child)

    def abandon_child(self, child):
        """
        Unregister a widget from this widget's children. The child's parent attribute will
        be set to None.
        """
        child.parent = None
        self.children.discard(child)

    def to_screen(self, point):
        """ Translates a `Point` inside this widget into screen coordinates. """
        x, y = point

        x += self.placement.left
        y += self.placement.top

        if self.parent:
            return self.parent.to_screen(utils.Point(x, y))
        else:
            return utils.Point(x, y)

    def to_local(self, point):
        """ Translates a `Point` from screen coordinates into the widget's coordinate system. """
        x, y = point

        x -= self.placement.left
        y -= self.placement.top

        if self.parent:
            return self.parent.to_local(utils.Point(x, y))
        else:
            return utils.Point(x, y)

    def center(self, horizontal=True, vertical=True):
        """ Centers the widget inside its parent (if present) or its console. """
        if self.parent:
            if horizontal:
                self.placement.left = (self.parent.placement.width - self.placement.width) / 2
            if vertical:
                self.placement.top = (self.parent.placement.height - self.placement.height) / 2
        else:
            if horizontal:
                self.placement.left = (self.console.width - self.placement.width) / 2
            if vertical:
                self.placement.top = (self.console.height - self.placement.height) / 2

    def render(self):
        """
        Render this widget and all its children, in that order. Note that the base Widget has
        nothing to render.
        """
        for child in self.children:
            child.render()

    def dispatch(self, event):
        """
        Dispatch an event to this widget and all its children, in that order. The first widget
        to return True for a dispatch call is considered to have handled the event, and it
        will not bubble further.
        """
        if event.type in self.handlers and self.handlers[event.type](self, event):
            return True

        for child in self.children:
            if child.dispatch(event):
                return True

        return False

class Dialog(Widget):
    """ A dialog renders a frame inside itself, on its outer edge. """
    def render(self):
        self.colors.apply(self.console)
        self.console.print_frame(self.placement.left, self.placement.top,
                                 self.placement.width, self.placement.height)
        super(Dialog, self).render()

class Image(Widget):
    """ Render an image from a file using libtcod's image handling. """
    def __init__(self, path, parent=None, x=0, y=0, width=0, height=0):
        super(Image, self).__init__(parent, x, y, width, height)
        self.image = tcod.ImageFile(path)
        self.bounds.size = self.image.size

    def render(self):
        self.image.blit_2x(self.console)
        super(Image, self).render()

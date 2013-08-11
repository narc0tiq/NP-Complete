""" User Interface bits and widgets """
import inspect
from itertools import imap

import tcod
from game import events, utils

COLOR_BASE = 0
COLOR_SHORTCUT = 1

active_colors = tcod.ColorSet()
active_colors.set_colors(COLOR_BASE, fgcolor=tcod.color.LIGHT_GREY, bgcolor=tcod.color.BLACK)
active_colors.set_colors(COLOR_SHORTCUT, fgcolor=tcod.color.LIME)

selected_colors = tcod.ColorSet()
selected_colors.set_colors(COLOR_BASE, fgcolor=tcod.color.WHITE, bgcolor=tcod.color.AZURE)
selected_colors.set_colors(COLOR_SHORTCUT, fgcolor=tcod.color.LIME)

disabled_colors = tcod.ColorSet()
disabled_colors.set_colors(COLOR_BASE, fgcolor=tcod.color.DARKER_GREY, bgcolor=tcod.color.BLACK)
disabled_colors.set_colors(COLOR_SHORTCUT, fgcolor=tcod.color.LIGHT_GREY)


class Widget(object):
    def __init__(self, parent=None, x=0, y=0, width=0, height=0):
        """
        Initialize a new generic Widget.

         * parent: if provided, the parent will be called to register_child() this widget.
         * x, y: if provided, these define the on-console `placement` of the
         widget.
         * width, height: if provided, these define the `bounds` of the widget.
        """
        self.parent = None
        self.children = utils.OrderedSet()
        self.console = tcod.root_console
        self.handlers = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            try: self.handlers[method.handles_event] = method
            except AttributeError: pass  # Not every method is a handler, and that's fine.
        self.colors = active_colors
        self.effect = tcod.background.SET
        self.bounds = utils.Rect(0,0, width,height)
        self.placement = utils.Rect(x,y, width,height)

        if parent:
            self.console = parent.console
            parent.register_child(self)

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
        if event.type in self.handlers:
            if event.widget is None or event.widget is self:
                if self.handlers[event.type](event):
                    return True
                # Short-circuit: event is directed at me and my handler
                # rejected it; nobody else will take it.
                elif event.widget is self:
                    return False

        for child in self.children:
            if child.dispatch(event):
                return True

        return False


class Dialog(Widget):
    """ A dialog renders a frame inside itself, on its outer edge. """
    def render(self):
        self.colors.apply(self.console)
        x, y = self.to_screen(utils.origin)
        self.console.print_frame(x, y, *self.placement.size)
        super(Dialog, self).render()


class Image(Widget):
    """ Render an image from a file using libtcod's image handling. """
    def __init__(self, path, parent=None, x=0, y=0, width=0, height=0):
        super(Image, self).__init__(parent, x, y, width, height)
        self.image = tcod.ImageFile(path)

    def render(self):
        x, y = self.to_screen(utils.origin)
        self.image.blit_2x(self.console, x, y, *self.bounds.origin,
                           width=2 * self.bounds.width, height=2 * self.bounds.height)
        super(Image, self).render()


class Label(Widget):
    """ Render text, with optional maximum width. """
    def __init__(self, text, parent=None, x=0, y=0, width=0):
        super(Label, self).__init__(parent, x, y, width, height=0)
        self._text = ''
        self.text = text
        self.align = tcod.align.LEFT

    @property
    def max_width(self):
        return self.bounds.width

    @max_width.setter
    def max_width(self, value):
        self.bounds.width = value
        self._recalc_size()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._recalc_size()

    def _recalc_size(self):
        text = self.colors.strip(self._text)
        width = self.bounds.width
        if self.bounds.width < 1:
            width = min(len(text), self.console.width - self.placement.left)
        height = self.console.get_height_rect(x=self.placement.left, y=self.placement.top,
                                              width=width, text=self._text)
        if (width, height) != self.placement.size:
            self.placement.size = width, height
            events.post(events.RESIZE, data=self)

    def render(self):
        self.colors.apply(self.console)
        x,y = self.to_screen(utils.origin)
        self.console.rect(x, y, *self.placement.size, clear=True)
        self.console.print_rect_ex(x, y, *self.placement.size,
                                   effect=self.effect, align=self.align,
                                   text=self._text)
        super(Label, self).render()


class Button(Label):
    """ A label that responds to keyboard shortcuts. """
    def __init__(self, key, label, parent=None, x=0, y=0, width=0, action=None):
        super(Button, self).__init__(label, parent, x, y, width)
        self.key = key
        self.action = action

    @events.handler(events.ACTIVATE)
    def on_activate(self, event):
        self.action(self)
        return True

    @events.handler(events.KEY)
    def on_key(self, event):
        if self.key_match(event.data):
            events.post(events.ACTIVATE, widget=self)
            return True

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key):
        if new_key is None:
            self._key = None
            self.key_match = lambda unused: False
            return

        key_match = utils.key_check(new_key)
        if not key_match:
            raise ValueError("'key' must be a valid name for utils.key_check()")

        self._key = new_key
        self.key_match = key_match


class List(Widget):
    def __init__(self, parent=None, x=0, y=0, width=0, height=0):
        super(List, self).__init__(parent, x, y, width, height)
        self.sub_console = tcod.Console(*self.bounds.size)
        self._selected_child = None

    @events.handler(events.RESIZE)
    def on_resize(self, event):
        if event.data in self.children:
            self._recalc_size()
            return True

    @events.handler(events.KEY)
    def on_key(self, event):
        if utils.key_check('Up')(event.data) and self.selected_child is not self.children.first:
            self.selected_child = self.children.triple(self.selected_child).prev
            return True
        elif utils.key_check('Down')(event.data) and self.selected_child is not self.children.last:
            self.selected_child = self.children.triple(self.selected_child).next
            return True

    def register_child(self, child):
        super(List, self).register_child(child)
        child.console = self.sub_console
        if self.bounds.width > 0:
            child.bounds.width = self.bounds.width - 1
        self._recalc_size()

    @property
    def scroll_pos(self):
        return (self.bounds.top, self.bounds.top + self.placement.height)

    @property
    def selected_child(self):
        return self._selected_child

    @selected_child.setter
    def selected_child(self, child):
        if self._selected_child:
            self._selected_child.colors = active_colors
        child.colors = selected_colors
        self._selected_child = child

    def _recalc_size(self):
        self._recalc_itempos()
        width = max(imap(lambda child: child.placement.width, self.children))
        height = sum(imap(lambda child: child.placement.height, self.children))
        self.sub_console.grow(width, height)

        self.placement.width = self.bounds.width if self.bounds.width > 0 else width
        self.placement.height = self.bounds.height if self.bounds.height > 0 else height

        for child in self.children:
            child.placement.width = self.placement.width

    def _recalc_itempos(self):
        for curr, prev, next in self.children.itertriples():
            # We set up a new sub_console to print in, so our children must think they are at the
            # (0,0) position on-screen (since they are at that position in the sub_console)
            x, y = self.to_screen(utils.origin)
            curr.placement.left = -x
            curr.placement.top = prev.placement.bottom if prev else -y

    def scroll_by(self, amount):
        new_top = self.bounds.top + amount
        if new_top < 0 or new_top > self.bounds.height:
            raise ValueError('Cannot scroll off-list to %d!' % new_top)
        self.bounds.top = new_top

    def scroll_to(self, top, bottom=None):
        """
        Scroll to bring either top or bottom into view, whichever is furthest from the current
        visible location. Prefers bringing top into view when scrolling up, and bottom into view
        when scrolling down.
        """
        if self.bounds.height < 1:
            return  # variable-height list is, by definition, always fully visible.
        elif top < self.bounds.top:  # scroll up to reveal top
            self.scroll_by(top - self.bounds.top)
        elif bottom and bottom > self.bounds.bottom:  # scroll down to reveal bottom
            self.scroll_by(bottom - self.bounds.bottom)
        elif top > self.bounds.bottom:  # scroll down to reveal top
            self.scroll_by(top - self.bounds.bottom)

    def render(self):
        # Clear the sub_console and render all the children (onto it)
        self.colors.apply(self.sub_console)
        self.sub_console.clear()
        super(List, self).render()

        # Then just blit the right part of the sub_console onto our console
        x, y = self.to_screen(utils.origin)
        self.console.rect(x, y, *self.placement.size, clear=True)
        self.sub_console.blit(self.bounds.left, self.bounds.top,
                              self.placement.width, self.placement.height,
                              self.console, x, y)

""" User Interface bits and widgets """
import collections

import tcod
from game import utils

class event:
    KEY, MOUSE = range(2)

class Widget(object):
    """
    A widget is something that knows how to render itself. All things that know
    how to render themselves are widgets.

    Widgets may have child widgets; when a widget is told to render itself, it
    asks its children to render themselves. Widgets may receive events; if an
    event is handled by a widget, it should return True. Otherwise, the event
    should be pased along to children, returning True if one of the children
    handled it, or False otherwise.

    Widgets who are initialized knowing who their parent is will automatically
    register themselves with their parent.

    Widgets all exist in a console; on initialization, widgets not given a
    console will make a good-faith effort and assume their console is their
    parent's. At render time, a widget that still does not know what its
    console is will assume it is tcod.root_console.

    Coordinates (in self.rect) are parent-relative (unless there's no parent,
    in which case, they are console-relative).
    """

    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0):
        self.parent = parent
        self.children = set()
        self.console = console

        if self.parent is not None:
            self.parent.register_child(self)

            if self.console is None:
                self.console = self.parent.console

            x = x + self.parent.rect.left
            y = y + self.parent.rect.top

        if self.console is None: #, even after all that,
            self.console = tcod.root_console

        self.rect = utils.Rect(x, y, width, height)

    def register_child(self, child):
        child.parent = self
        self.children.add(child)

    def point_to_screen(self, point):
        """ Translates a Point(x,y) inside this widget into screen coordinates """
        x = point.x + self.rect.left
        y = point.y + self.rect.top

        if self.parent:
            return self.parent.point_to_screen(utils.Point(x,y))
        else:
            return utils.Point(x,y)

    def screen_to_point(self, point):
        """
        Translates a Point(x,y) in screen coordinates into a point inside this
        widget. Inverse of self.point_to_screen().
        """
        x = point.x - self.rect.left
        y = point.y - self.rect.top

        if self.parent:
            return self.parent.screen_to_point(utils.Point(x,y))
        else:
            return utils.Point(x,y)

    def render(self):
        """ The default implementation just asks children to render. """
        for child in self.children:
            child.render()

    def handle_event(self, ev, data):
        """
        The default implementation just asks children if they want it. If they
        return True, they did.
        """
        for child in self.children:
            if child.handle_event(ev, data):
                return True

        return False

    def hcenter_in_parent(self):
        if self.parent is None:
            raise ValueError("Widget trying to hcenter in non-existent parent")
        self.rect.left = (self.parent.rect.width - self.rect.width) / 2

    def vcenter_in_parent(self):
        if self.parent is None:
            raise ValueError("Widget trying to vcenter in non-existent parent")
        self.rect.top = (self. parent.rect.height - self.rect.height) / 2

class Label(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, text="", width=0):
        super(Label, self).__init__(parent, console, x, y, width, height=0)
        self.max_width = width
        self._text = text
        self.align = tcod.align.LEFT
        self.effect = tcod.background.SET

        self.calc_size()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.calc_size()

    def calc_size(self):
        width = self.rect.width
        if self.max_width < 1:
            width = min(len(self._text), self.console.width - self.rect.left)
        height = self.console.get_height_rect(self.rect.left, self.rect.top,
                                              width, text=self._text)
        self.rect.resize(width=width, height=height)

    def render(self):
        x,y = self.point_to_screen(utils.origin)

        self.console.print_rect_ex(x, y, self.rect.width, self.rect.height,
                                   self.effect, self.align, self._text)

ListItem = collections.namedtuple("ListItem", ["label", "disabled", "on_activate"])

class List(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0):
        super(List, self).__init__(parent, console, x, y, 0, 0)
        self.init_width = max(0, width-1) # leave 1 character of width for the scrollbar, if fixed-width
        self.init_height = height
        self.items = []
        self.selected_item = None
        self.sub_console = None
        self.scroll_y = 0
        self.render_item_override = None

    def add_item(self, label, disabled=False, on_activate=None):
        """
        Warning: Trying to add_item() after the list has been rendered is
        currently unsupported.
        """
        if self.sub_console is not None:
            raise AttributeError("Trying to add items to a list after offscreen surface created.")

        li = ListItem(label, disabled, on_activate)

        self.items.append(li)
        if self.selected_item is None and not li.disabled:
            self.selected_item = li

        self._calc_size(li)
        return li

    def _calc_size(self, item):
        """
        Recalculates the size of the offscreen surface to include the size of
        the given item. self.add_item() will automatically call this, as will
        self.recalc_size().
        """
        self.rect.height += self.console.get_height_rect(self.rect.left, self.rect.top,
                                                         self.init_width,
                                                         text=item.label)

        if self.init_width > 0:
            self.rect.width = self.init_width
        elif len(item.label) > self.rect.width:
            self.rect.width = len(item.label)

    def recalc_size(self):
        """ Call this if you edited self.items without using self.add_item() """
        if self.sub_console is not None:
            raise AttributeError("Trying to resize list after offscreen surface created.")

        self.rect.resize(0, 0)
        for item in self.items:
            self._calc_size(item)


    def scroll_by(self, amount):
        self.scroll_y += amount

    def scroll_to(self, y, height=1):
        if self.init_height < 1:
            return # Nothing to do for variable height lists.

        scroll_bottom = self.scroll_y + self.init_height
        if y < self.scroll_y: # scroll up
            self.scroll_by(y - self.scroll_y)
        elif y+height > scroll_bottom: # scroll down
            self.scroll_by(y+height - scroll_bottom)

    def render(self):
        """
        Note that the first render creates an offscreen surface, which is never
        re-created; self.add_item() and self.recalc_size() will refuse to
        operate.
        """
        if self.sub_console is None:
            self.sub_console = tcod.Console(self.rect.width, self.rect.height)

        draw_width = self.init_width+1 if self.init_width > 0 else self.rect.width
        draw_height = self.init_height if self.init_height > 0 else self.rect.height

        origin = self.point_to_screen(utils.origin)
        self.console.rect(origin.x, origin.y, draw_width, draw_height, clear=True)

        y = 0
        for i in self.items:
            height = self.sub_console.get_height_rect(0, y, text=i.label)

            bgcolor = tcod.color.BLACK
            if self.selected_item is i:
                bgcolor = tcod.color.AZURE
                self.scroll_to(y, height)
            self.sub_console.set_default_background(bgcolor)
            self.sub_console.rect(0, y, self.rect.width, height, clear=True)
            self.sub_console.set_default_background(tcod.color.BLACK)

            if i.disabled:
                self.sub_console.set_default_foreground(tcod.color.GRAY)
            else:
                self.sub_console.set_default_foreground(tcod.color.WHITE)

            self.sub_console.print_rect_ex(0, y, text=i.label)
            if self.render_item_override:
                self.render_item_override(self.sub_console, i, 0, y, self.rect.width, height)
            y += height

        self.sub_console.blit(0, self.scroll_y,
                              draw_width, draw_height,
                              self.console, origin.x, origin.y)

    def handle_event(self, ev, data):
        if ev == event.KEY:
            selected_index = self.items.index(self.selected_item)
            if data.vk == tcod.key.DOWN and (selected_index+1) < len(self.items):
                self.selected_item = self.items[selected_index + 1]
            elif data.vk == tcod.key.UP and selected_index > 0:
                self.selected_item = self.items[selected_index - 1]

class Menu(Widget):
    def __init__(self, parent=None, console=None, x=0, y=0, width=0, height=0):
        super(Menu, self).__init__(parent, console, x, y, width, height)
        self.init_width = width
        self.init_height = height
        self.list = List(parent=self, x=x+1, y=y+1, width=max(0, width-2), height=max(0, height-2))

    def add_item(self, label, disabled=False, on_activate=None):
        item = self.list.add_item(label, disabled, on_activate)
        self.calc_size()
        return item

    @property
    def selected_item(self):
        return self.list.selected_item

    def calc_size(self):
        if self.init_width < 1:
            self.rect.width = self.list.rect.width + 2
        if self.init_height < 1:
            self.rect.height = self.list.rect.height + 2

    def render(self):
        self.console.set_default_foreground(tcod.color.WHITE)
        self.console.print_frame(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
        super(Menu, self).render()
